"""
拜訪記錄 CRUD 操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
import math

from app.models.base import Visit, Customer, VisitType, VisitStatus
from app.schemas.visit import VisitCreate, VisitUpdate


class VisitCRUD:
    """拜訪記錄 CRUD 操作類"""

    @staticmethod
    async def create(db: AsyncSession, visit_data: VisitCreate) -> Visit:
        """建立拜訪記錄"""
        visit = Visit(
            customer_id=visit_data.customer_id,
            visit_type=visit_data.visit_type,
            visit_date=visit_data.visit_date,
            visit_status=visit_data.visit_status,
            questionnaire_data=visit_data.questionnaire_data,
            notes=visit_data.notes,
            next_action=visit_data.next_action,
            next_visit_date=visit_data.next_visit_date,
            created_by=None,  # MVP 版本無認證系統
        )

        db.add(visit)
        await db.commit()
        await db.refresh(visit)
        return visit

    @staticmethod
    async def get_by_id(db: AsyncSession, visit_id: str) -> Optional[Visit]:
        """根據 ID 取得拜訪記錄"""
        result = await db.execute(
            select(Visit)
            .options(selectinload(Visit.customer))
            .where(Visit.id == visit_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        customer_id: Optional[str] = None,
        visit_type: Optional[VisitType] = None,
        visit_status: Optional[VisitStatus] = None,
    ) -> tuple[List[Visit], int]:
        """
        取得拜訪記錄列表（分頁）

        Returns:
            tuple: (拜訪記錄列表, 總數)
        """
        # 構建查詢
        query = select(Visit).options(selectinload(Visit.customer))
        count_query = select(func.count()).select_from(Visit)

        # 篩選條件
        conditions = []

        if customer_id:
            conditions.append(Visit.customer_id == customer_id)

        if visit_type:
            conditions.append(Visit.visit_type == visit_type)

        if visit_status:
            conditions.append(Visit.visit_status == visit_status)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # 取得總數
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分頁
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit).order_by(Visit.visit_date.desc())

        # 執行查詢
        result = await db.execute(query)
        visits = result.scalars().all()

        return list(visits), total

    @staticmethod
    async def update(
        db: AsyncSession,
        visit_id: str,
        visit_data: VisitUpdate
    ) -> Optional[Visit]:
        """更新拜訪記錄"""
        visit = await VisitCRUD.get_by_id(db, visit_id)
        if not visit:
            return None

        # 更新欄位
        update_data = visit_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(visit, field, value)

        await db.commit()
        await db.refresh(visit)
        return visit

    @staticmethod
    async def delete(db: AsyncSession, visit_id: str) -> bool:
        """刪除拜訪記錄"""
        visit = await VisitCRUD.get_by_id(db, visit_id)
        if not visit:
            return False

        await db.delete(visit)
        await db.commit()
        return True

    @staticmethod
    async def get_statistics(db: AsyncSession) -> dict:
        """取得拜訪統計資料"""
        # 總拜訪數
        total_result = await db.execute(select(func.count()).select_from(Visit))
        total_visits = total_result.scalar()

        # 一訪數量
        first_visit_result = await db.execute(
            select(func.count()).select_from(Visit).where(Visit.visit_type == VisitType.FIRST_VISIT)
        )
        first_visits = first_visit_result.scalar()

        # 二訪數量
        second_visit_result = await db.execute(
            select(func.count()).select_from(Visit).where(Visit.visit_type == VisitType.SECOND_VISIT)
        )
        second_visits = second_visit_result.scalar()

        # 已完成拜訪數
        completed_result = await db.execute(
            select(func.count()).select_from(Visit).where(Visit.visit_status == VisitStatus.COMPLETED)
        )
        completed_visits = completed_result.scalar()

        # 已排程拜訪數
        scheduled_result = await db.execute(
            select(func.count()).select_from(Visit).where(Visit.visit_status == VisitStatus.SCHEDULED)
        )
        scheduled_visits = scheduled_result.scalar()

        # 按狀態分類
        status_result = await db.execute(
            select(
                Visit.visit_status,
                func.count(Visit.id)
            ).group_by(Visit.visit_status)
        )
        by_status = {status.value: count for status, count in status_result}

        return {
            "total_visits": total_visits,
            "first_visits": first_visits,
            "second_visits": second_visits,
            "completed_visits": completed_visits,
            "scheduled_visits": scheduled_visits,
            "by_status": by_status
        }

    @staticmethod
    async def get_by_customer(
        db: AsyncSession,
        customer_id: str,
        visit_type: Optional[VisitType] = None
    ) -> List[Visit]:
        """取得特定客戶的所有拜訪記錄"""
        query = select(Visit).where(Visit.customer_id == customer_id)

        if visit_type:
            query = query.where(Visit.visit_type == visit_type)

        query = query.order_by(Visit.visit_date.desc())

        result = await db.execute(query)
        return list(result.scalars().all())


# 建立全域實例
visit_crud = VisitCRUD()
