"""
Lead Import API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json
from pathlib import Path
import shutil
import tempfile

from app.core.database import get_db
from app.crud.lead import lead_import_crud
from app.services.excel_service import excel_service
from app.schemas.lead import (
    LeadImportResponse,
    ImportHistoryResponse,
    ImportOptions,
    DuplicateInfo,
    ImportError as ImportErrorSchema,
)
from app.models.base import ImportStatus

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("/import", response_model=LeadImportResponse)
async def import_leads(
    file: UploadFile = File(..., description="Excel 檔案"),
    options: Optional[str] = Form(None, description="導入選項（JSON 字串）"),
    db: AsyncSession = Depends(get_db)
):
    """
    導入潛在客戶名單（Excel）

    - **file**: Excel 檔案（.xlsx, .xls）
    - **options**: 導入選項（JSON 格式）
      - skip_duplicates: 跳過重複資料
      - update_existing: 更新現有資料
      - dry_run: 乾運行（不實際導入）

    返回導入結果，包含：
    - batch_id: 導入批次 ID
    - status: 狀態（processing, completed, failed）
    - total_rows: 總行數
    - success_count: 成功筆數
    - fail_count: 失敗筆數
    - duplicate_count: 重複筆數
    - duplicates: 重複資料詳情
    - errors: 錯誤詳情
    """

    # 驗證檔案類型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="檔案格式錯誤，僅支援 .xlsx 或 .xls 格式"
        )

    # 驗證檔案大小（10MB）
    file_size_limit = 10 * 1024 * 1024
    file.file.seek(0, 2)  # 移到檔案結尾
    file_size = file.file.tell()
    file.file.seek(0)  # 回到檔案開頭

    if file_size > file_size_limit:
        raise HTTPException(
            status_code=413,
            detail=f"檔案過大，最大支援 10MB（目前：{file_size / 1024 / 1024:.2f}MB）"
        )

    # 解析導入選項
    import_options = ImportOptions()
    if options:
        try:
            options_dict = json.loads(options)
            import_options = ImportOptions(**options_dict)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"導入選項格式錯誤: {str(e)}"
            )

    # 儲存臨時檔案
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_file_path = Path(tmp_file.name)

    try:
        # 1. 建立導入批次記錄
        import_batch = await lead_import_crud.create_import_batch(
            db=db,
            file_name=file.filename,
            file_path=str(tmp_file_path)
        )

        # 2. 解析 Excel 檔案
        try:
            valid_rows, error_rows = await excel_service.parse_lead_import_file(tmp_file_path)
        except Exception as e:
            # 更新批次狀態為失敗
            await lead_import_crud.update_import_batch(
                db=db,
                batch_id=import_batch.id,
                status=ImportStatus.FAILED,
                total_rows=0,
                success_count=0,
                fail_count=0,
                error_log={"error": f"檔案解析失敗: {str(e)}"}
            )
            raise HTTPException(
                status_code=422,
                detail=f"Excel 檔案解析失敗: {str(e)}"
            )

        total_rows = len(valid_rows) + len(error_rows)

        # 3. 檢測重複資料
        duplicates_info = []
        if not import_options.skip_duplicates:
            duplicates_data = await excel_service.detect_duplicates(db, valid_rows)
            duplicates_info = [
                DuplicateInfo(
                    row_number=dup["row_number"],
                    customer_name=dup["customer_name"],
                    contact_phone=dup["contact_phone"],
                    existing_customer_id=dup["existing_customer_id"]
                )
                for dup in duplicates_data
            ]

            # 如果不更新現有資料，則從有效列表中移除重複項
            if not import_options.update_existing:
                duplicate_row_numbers = {dup.row_number for dup in duplicates_info}
                valid_rows = [
                    row for idx, row in enumerate(valid_rows, start=1)
                    if idx not in duplicate_row_numbers
                ]

        # 4. 準備錯誤資訊
        errors_info = [
            ImportErrorSchema(
                row_number=err["row_number"],
                error_type=err["error_type"],
                error_message=err["error_message"],
                row_data=err["row_data"]
            )
            for err in error_rows
        ]

        # 5. 乾運行模式：不實際導入
        if import_options.dry_run:
            await lead_import_crud.update_import_batch(
                db=db,
                batch_id=import_batch.id,
                status=ImportStatus.COMPLETED,
                total_rows=total_rows,
                success_count=len(valid_rows),
                fail_count=len(error_rows),
                duplicate_count=len(duplicates_info)
            )

            return LeadImportResponse(
                batch_id=import_batch.id,
                status="completed",
                total_rows=total_rows,
                success_count=len(valid_rows),
                fail_count=len(error_rows),
                duplicate_count=len(duplicates_info),
                duplicates=duplicates_info,
                errors=errors_info
            )

        # 6. 實際導入資料
        success_count = 0
        try:
            if import_options.update_existing and duplicates_info:
                # 更新重複的客戶資料
                for dup_info in duplicates_info:
                    # 找到對應的行資料
                    row_data = valid_rows[dup_info.row_number - 1] if dup_info.row_number <= len(valid_rows) else None
                    if row_data:
                        await lead_import_crud.update_customer(
                            db=db,
                            customer_id=dup_info.existing_customer_id,
                            customer_data=row_data
                        )
                        success_count += 1

            # 批次插入新客戶
            if valid_rows:
                created_count = await lead_import_crud.batch_create_customers(
                    db=db,
                    customers_data=valid_rows,
                    import_batch_id=import_batch.id,
                    batch_size=100
                )
                success_count += created_count

            # 更新批次狀態為完成
            await lead_import_crud.update_import_batch(
                db=db,
                batch_id=import_batch.id,
                status=ImportStatus.COMPLETED,
                total_rows=total_rows,
                success_count=success_count,
                fail_count=len(error_rows),
                duplicate_count=len(duplicates_info),
                error_log={"errors": [err.dict() for err in errors_info]} if errors_info else None
            )

            return LeadImportResponse(
                batch_id=import_batch.id,
                status="completed",
                total_rows=total_rows,
                success_count=success_count,
                fail_count=len(error_rows),
                duplicate_count=len(duplicates_info),
                duplicates=duplicates_info,
                errors=errors_info
            )

        except Exception as e:
            # 導入失敗，更新批次狀態
            await lead_import_crud.update_import_batch(
                db=db,
                batch_id=import_batch.id,
                status=ImportStatus.FAILED,
                total_rows=total_rows,
                success_count=success_count,
                fail_count=len(error_rows) + (len(valid_rows) - success_count),
                duplicate_count=len(duplicates_info),
                error_log={"error": f"資料導入失敗: {str(e)}"}
            )

            raise HTTPException(
                status_code=500,
                detail=f"資料導入失敗: {str(e)}"
            )

    finally:
        # 清理臨時檔案
        if tmp_file_path.exists():
            tmp_file_path.unlink()


@router.get("/import/history", response_model=ImportHistoryResponse)
async def get_import_history(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    查詢導入歷史記錄

    - **page**: 頁碼（預設 1）
    - **limit**: 每頁筆數（預設 20）
    - **status**: 狀態篩選（processing, completed, failed）

    返回導入歷史列表與分頁資訊
    """
    # 狀態驗證
    import_status = None
    if status:
        try:
            import_status = ImportStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"無效的狀態值: {status}。有效值: processing, completed, failed"
            )

    # 查詢資料
    batches, total = await lead_import_crud.get_import_batches(
        db=db,
        page=page,
        limit=limit,
        status=import_status
    )

    # 計算總頁數
    import math
    total_pages = math.ceil(total / limit) if total > 0 else 0

    return ImportHistoryResponse(
        batches=[
            {
                "id": batch.id,
                "file_name": batch.file_name,
                "status": batch.status.value,
                "total_rows": batch.total_rows,
                "success_count": batch.success_count,
                "fail_count": batch.fail_count,
                "duplicate_count": batch.duplicate_count,
                "created_at": batch.created_at,
                "created_by": batch.created_by
            }
            for batch in batches
        ],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )
