"""
健檢報告 API 路由
"""
import math
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.report_service import report_service
from app.crud.report import report_crud
from app.schemas.report import (
    ReportGenerateRequest,
    ReportGenerateResponse,
    BatchExportRequest,
    ReportEmailRequest,
    ReportEmailResponse,
    ReportResponse,
    ReportListResponse
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=ReportListResponse)
async def list_reports(
    customer_id: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    查詢報告列表（支援分頁與篩選）

    支援按 customer_id 篩選，按 created_at 倒序排列。

    Args:
        customer_id: 客戶 ID（可選）
        page: 頁碼（從 1 開始）
        limit: 每頁筆數（最多 100）

    Returns:
        ReportListResponse: 報告列表與分頁資訊
    """
    # 限制每頁筆數
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 20

    if page < 1:
        page = 1

    # 查詢報告
    reports, total = await report_crud.get_all(
        db=db,
        customer_id=customer_id,
        page=page,
        limit=limit
    )

    # 計算總頁數
    total_pages = math.ceil(total / limit) if total > 0 else 0

    return ReportListResponse(
        reports=reports,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    查詢單一報告詳情

    Args:
        report_id: 報告 ID

    Returns:
        ReportResponse: 報告詳細資訊

    Raises:
        HTTPException 404: 報告不存在
    """
    report = await report_crud.get_by_id(db, report_id)

    if not report:
        raise HTTPException(status_code=404, detail=f"報告不存在: {report_id}")

    return report


@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    刪除報告

    同時刪除資料庫記錄與檔案。

    Args:
        report_id: 報告 ID

    Returns:
        成功訊息

    Raises:
        HTTPException 404: 報告不存在
    """
    success = await report_crud.delete(db, report_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"報告不存在: {report_id}")

    return {"message": f"報告已成功刪除: {report_id}"}


@router.post("/generate", response_model=ReportGenerateResponse, status_code=201)
async def generate_report(
    request: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    生成客戶健檢報告

    生成包含以下內容的 Excel 報告：
    - 客戶基本資料
    - 評估結果（等級、評分）
    - 業務30問問答記錄（已討論標綠色，未討論標黃色）
    - AA 客戶判定理由（如適用）

    流程：
    1. 查詢客戶與評估資料
    2. 生成 Excel 檔案
    3. 儲存報告記錄
    """
    try:
        # 生成報告
        report = await report_service.generate_health_check_report(
            db=db,
            customer_id=request.customer_id,
            evaluation_id=request.evaluation_id,
            format=request.format
        )

        return ReportGenerateResponse(
            report_id=report.id,
            customer_id=report.customer_id,
            file_path=report.file_path,
            file_format=report.report_format,
            created_at=report.created_at
        )

    except ValueError as e:
        # 客戶或評估記錄不存在
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 其他錯誤
        raise HTTPException(status_code=500, detail=f"報告生成失敗: {str(e)}")


@router.get("/{report_id}/export")
async def export_report(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    下載報告檔案

    返回報告的 Excel 檔案供下載
    """
    # 查詢報告記錄
    report = await report_crud.get_by_id(db, report_id)

    if not report:
        raise HTTPException(status_code=404, detail=f"報告不存在: {report_id}")

    # 檢查檔案是否存在
    file_path = Path(report.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="報告檔案不存在")

    # 返回檔案
    return FileResponse(
        path=file_path,
        filename=report.file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.post("/batch-export")
async def batch_export_reports(
    request: BatchExportRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    批次匯出多個客戶的報告

    將多個客戶的健檢報告打包為 ZIP 檔案供下載。
    最多支援 50 個客戶。
    """
    try:
        # 生成批次報告 ZIP
        zip_path = await report_service.generate_batch_reports(
            db=db,
            customer_ids=request.customer_ids,
            format=request.format
        )

        # 返回 ZIP 檔案
        return FileResponse(
            path=zip_path,
            filename=zip_path.name,
            media_type="application/zip"
        )

    except ValueError as e:
        # 客戶數量超過限制
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 其他錯誤
        raise HTTPException(status_code=500, detail=f"批次匯出失敗: {str(e)}")


@router.post("/send-email", response_model=ReportEmailResponse)
async def send_report_email(
    request: ReportEmailRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    透過 Email 分享報告

    發送包含報告附件的 Email 給指定收件人。
    Email 發送為非同步處理（背景任務）。

    注意：此功能需要配置 SMTP 設定（環境變數）。
    MVP 階段暫未實作，返回未實作訊息。
    """
    # 驗證報告存在
    report = await report_crud.get_by_id(db, request.report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"報告不存在: {request.report_id}")

    # 呼叫 Email 發送服務
    success = await report_service.send_report_email(
        db=db,
        report_id=request.report_id,
        recipient_email=request.recipient_email,
        subject=request.subject,
        message=request.message
    )

    if not success:
        return ReportEmailResponse(
            success=False,
            message="Email 發送功能尚未實作（需配置 SMTP）"
        )

    return ReportEmailResponse(
        success=True,
        message=f"Email 已成功發送至 {request.recipient_email}"
    )
