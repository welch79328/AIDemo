"""
Interaction API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.database import get_db
from app.crud.interaction import interaction_crud
from app.schemas.interaction import (
    InteractionCreate,
    InteractionResponse,
    InteractionListResponse,
    InteractionUploadResponse,
    InteractionTypeEnum
)
from app.models.base import InteractionType
from app.services.file_service import file_service


router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("", response_model=InteractionResponse, status_code=201)
async def create_interaction(
    data: InteractionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    建立互動記錄（非檔案上傳）

    用於手動記錄狀態變更等非檔案類型的互動
    """
    # 轉換 enum
    interaction_type = InteractionType(data.interaction_type)

    interaction = await interaction_crud.create(
        db=db,
        customer_id=data.customer_id,
        interaction_type=interaction_type,
        title=data.title,
        notes=data.notes,
        created_by=None  # MVP: 無認證
    )

    return InteractionResponse.model_validate(interaction)


@router.get("", response_model=InteractionListResponse)
async def list_interactions(
    customer_id: Optional[str] = Query(None, description="客戶 ID 篩選"),
    interaction_type: Optional[InteractionTypeEnum] = Query(None, description="互動類型篩選"),
    page: int = Query(1, ge=1, description="頁碼"),
    limit: int = Query(20, ge=1, le=100, description="每頁筆數"),
    db: AsyncSession = Depends(get_db)
):
    """
    查詢互動記錄列表

    支援：
    - 客戶篩選 (customer_id)
    - 類型篩選 (interaction_type)
    - 分頁 (page, limit)
    - 按時間倒序排列
    """
    # 轉換 enum
    interaction_type_filter = None
    if interaction_type:
        interaction_type_filter = InteractionType(interaction_type)

    if customer_id:
        interactions, total = await interaction_crud.get_by_customer(
            db=db,
            customer_id=customer_id,
            interaction_type=interaction_type_filter,
            page=page,
            limit=limit
        )
    else:
        interactions, total = await interaction_crud.get_all(
            db=db,
            interaction_type=interaction_type_filter,
            page=page,
            limit=limit
        )

    import math
    total_pages = math.ceil(total / limit) if total > 0 else 0

    return InteractionListResponse(
        interactions=[
            InteractionResponse.model_validate(interaction)
            for interaction in interactions
        ],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(
    interaction_id: str,
    db: AsyncSession = Depends(get_db)
):
    """取得單一互動記錄"""
    interaction = await interaction_crud.get_by_id(db=db, interaction_id=interaction_id)

    if not interaction:
        raise HTTPException(status_code=404, detail="互動記錄不存在")

    return InteractionResponse.model_validate(interaction)


@router.delete("/{interaction_id}", status_code=204)
async def delete_interaction(
    interaction_id: str,
    db: AsyncSession = Depends(get_db)
):
    """刪除互動記錄"""
    success = await interaction_crud.delete(db=db, interaction_id=interaction_id)

    if not success:
        raise HTTPException(status_code=404, detail="互動記錄不存在")

    return None


@router.post("/upload", response_model=InteractionUploadResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(..., description="上傳的檔案"),
    customer_id: str = Form(..., description="客戶 ID"),
    interaction_type: InteractionTypeEnum = Form(..., description="互動類型（DOCUMENT 或 AUDIO）"),
    title: Optional[str] = Form(None, description="標題"),
    notes: Optional[str] = Form(None, description="備註"),
    db: AsyncSession = Depends(get_db)
):
    """
    上傳檔案並建立互動記錄

    支援：
    - 文檔類型：.pdf, .docx, .doc, .jpg, .png (最大 10MB)
    - 音訊類型：.mp3, .wav, .m4a (最大 50MB)

    自動處理：
    - 檔案儲存到 storage/interactions/documents 或 storage/interactions/audios
    - 建立 Interaction 資料庫記錄
    - 音訊檔自動提取時長（未來實作）
    """
    # 驗證 interaction_type
    if interaction_type not in [InteractionTypeEnum.DOCUMENT, InteractionTypeEnum.AUDIO]:
        raise HTTPException(
            status_code=400,
            detail="檔案上傳僅支援 DOCUMENT 或 AUDIO 類型"
        )

    # 根據類型決定檔案類別
    file_category = "document" if interaction_type == InteractionTypeEnum.DOCUMENT else "audio"

    try:
        # 1. 上傳檔案
        file_info = file_service.upload_file(file, file_category=file_category)

        # 2. 建立互動記錄
        interaction = await interaction_crud.create(
            db=db,
            customer_id=customer_id,
            interaction_type=InteractionType(interaction_type),
            title=title or file.filename,
            file_path=file_info["file_path"],
            file_name=file_info["file_name"],
            file_size=file_info["file_size"],
            audio_duration=None,  # TODO: 音訊時長提取（未來實作）
            notes=notes,
            created_by=None  # MVP: 無認證
        )

        return InteractionUploadResponse(
            id=interaction.id,
            customer_id=interaction.customer_id,
            interaction_type=interaction.interaction_type.value,
            title=interaction.title,
            file_path=interaction.file_path,
            file_name=interaction.file_name,
            file_size=interaction.file_size,
            audio_duration=interaction.audio_duration,
            notes=interaction.notes,
            created_at=interaction.created_at
        )

    except ValueError as e:
        # 檔案驗證失敗
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 其他錯誤
        raise HTTPException(status_code=500, detail=f"檔案上傳失敗: {str(e)}")
