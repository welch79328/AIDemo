"""
Interaction CRUD 操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import joinedload
from typing import Optional, List, Tuple
from datetime import datetime

from app.models.base import Interaction, InteractionType


class InteractionCRUD:
    """Interaction CRUD 操作類"""

    @staticmethod
    async def create(
        db: AsyncSession,
        customer_id: str,
        interaction_type: InteractionType,
        title: Optional[str] = None,
        file_path: Optional[str] = None,
        file_name: Optional[str] = None,
        file_size: Optional[int] = None,
        audio_duration: Optional[int] = None,
        transcript_text: Optional[str] = None,
        notes: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Interaction:
        """
        建立互動記錄

        Args:
            db: 資料庫 session
            customer_id: 客戶 ID
            interaction_type: 互動類型
            title: 標題
            file_path: 檔案路徑
            file_name: 檔案名稱
            file_size: 檔案大小
            audio_duration: 音訊時長（秒）
            transcript_text: 文字稿
            notes: 備註
            created_by: 建立者 ID

        Returns:
            建立的互動記錄
        """
        interaction = Interaction(
            customer_id=customer_id,
            interaction_type=interaction_type,
            title=title,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            audio_duration=audio_duration,
            transcript_text=transcript_text,
            notes=notes,
            created_by=created_by
        )

        db.add(interaction)
        await db.commit()
        await db.refresh(interaction)
        return interaction

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        interaction_id: str
    ) -> Optional[Interaction]:
        """
        根據 ID 取得互動記錄

        Args:
            db: 資料庫 session
            interaction_id: 互動記錄 ID

        Returns:
            互動記錄或 None
        """
        result = await db.execute(
            select(Interaction)
            .options(joinedload(Interaction.customer))
            .where(Interaction.id == interaction_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_customer(
        db: AsyncSession,
        customer_id: str,
        interaction_type: Optional[InteractionType] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Interaction], int]:
        """
        根據客戶取得互動記錄（分頁）

        Args:
            db: 資料庫 session
            customer_id: 客戶 ID
            interaction_type: 互動類型篩選（可選）
            page: 頁碼
            limit: 每頁筆數

        Returns:
            (互動記錄列表, 總數)
        """
        # 構建查詢
        query = select(Interaction).where(Interaction.customer_id == customer_id)
        count_query = select(func.count()).select_from(Interaction).where(
            Interaction.customer_id == customer_id
        )

        # 類型篩選
        if interaction_type:
            query = query.where(Interaction.interaction_type == interaction_type)
            count_query = count_query.where(Interaction.interaction_type == interaction_type)

        # 按時間倒序
        query = query.order_by(desc(Interaction.created_at))

        # 計算總數
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分頁
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # 執行查詢
        result = await db.execute(query)
        interactions = result.scalars().all()

        return list(interactions), total

    @staticmethod
    async def get_all(
        db: AsyncSession,
        customer_id: Optional[str] = None,
        interaction_type: Optional[InteractionType] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Interaction], int]:
        """
        取得所有互動記錄（分頁，支援篩選）

        Args:
            db: 資料庫 session
            customer_id: 客戶 ID 篩選（可選）
            interaction_type: 互動類型篩選（可選）
            page: 頁碼
            limit: 每頁筆數

        Returns:
            (互動記錄列表, 總數)
        """
        # 構建查詢
        query = select(Interaction).options(joinedload(Interaction.customer))
        count_query = select(func.count()).select_from(Interaction)

        # 篩選條件
        if customer_id:
            query = query.where(Interaction.customer_id == customer_id)
            count_query = count_query.where(Interaction.customer_id == customer_id)

        if interaction_type:
            query = query.where(Interaction.interaction_type == interaction_type)
            count_query = count_query.where(Interaction.interaction_type == interaction_type)

        # 按時間倒序
        query = query.order_by(desc(Interaction.created_at))

        # 計算總數
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分頁
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # 執行查詢
        result = await db.execute(query)
        interactions = result.scalars().all()

        return list(interactions), total

    @staticmethod
    async def update(
        db: AsyncSession,
        interaction_id: str,
        **update_data
    ) -> Optional[Interaction]:
        """
        更新互動記錄

        Args:
            db: 資料庫 session
            interaction_id: 互動記錄 ID
            **update_data: 更新的欄位

        Returns:
            更新後的互動記錄或 None
        """
        result = await db.execute(
            select(Interaction).where(Interaction.id == interaction_id)
        )
        interaction = result.scalar_one_or_none()

        if not interaction:
            return None

        # 更新欄位
        for key, value in update_data.items():
            if hasattr(interaction, key) and value is not None:
                setattr(interaction, key, value)

        await db.commit()
        await db.refresh(interaction)
        return interaction

    @staticmethod
    async def delete(
        db: AsyncSession,
        interaction_id: str
    ) -> bool:
        """
        刪除互動記錄

        Args:
            db: 資料庫 session
            interaction_id: 互動記錄 ID

        Returns:
            是否成功刪除
        """
        result = await db.execute(
            select(Interaction).where(Interaction.id == interaction_id)
        )
        interaction = result.scalar_one_or_none()

        if not interaction:
            return False

        await db.delete(interaction)
        await db.commit()
        return True


# 建立全域實例
interaction_crud = InteractionCRUD()
