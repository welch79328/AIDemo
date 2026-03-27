"""
客戶 CRUD 操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
import math

from app.models.base import Customer, CustomerStage, CustomerStatus
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerCRUD:
    """客戶 CRUD 操作類"""

    @staticmethod
    async def create(db: AsyncSession, customer_data: CustomerCreate) -> Customer:
        """建立客戶"""
        customer = Customer(
            company_name=customer_data.company_name,
            contact_person=customer_data.contact_person,
            contact_phone=customer_data.contact_phone,
            contact_email=customer_data.contact_email,
            website=customer_data.website,
            customer_stage=customer_data.customer_stage,
            basic_info=customer_data.basic_info,
            created_by=None,  # MVP 版本無認證系統，設為 None
        )

        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def get_by_id(db: AsyncSession, customer_id: str) -> Optional[Customer]:
        """根據 ID 取得客戶"""
        result = await db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        is_aa: Optional[bool] = None,
        status: Optional[CustomerStatus] = None,
        stage: Optional[CustomerStage] = None,
    ) -> tuple[List[Customer], int]:
        """
        取得客戶列表（分頁）

        Returns:
            tuple: (客戶列表, 總數)
        """
        # 構建查詢
        query = select(Customer)
        count_query = select(func.count()).select_from(Customer)

        # 篩選條件
        conditions = []

        if search:
            search_condition = or_(
                Customer.company_name.ilike(f"%{search}%"),
                Customer.contact_person.ilike(f"%{search}%"),
                Customer.contact_phone.ilike(f"%{search}%"),
            )
            conditions.append(search_condition)

        if is_aa is not None:
            conditions.append(Customer.is_aa_customer == is_aa)

        if status:
            conditions.append(Customer.current_status == status)

        if stage:
            conditions.append(Customer.customer_stage == stage)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # 取得總數
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分頁
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit).order_by(Customer.created_at.desc())

        # 執行查詢
        result = await db.execute(query)
        customers = result.scalars().all()

        return list(customers), total

    @staticmethod
    async def update(
        db: AsyncSession,
        customer_id: str,
        customer_data: CustomerUpdate
    ) -> Optional[Customer]:
        """更新客戶"""
        customer = await CustomerCRUD.get_by_id(db, customer_id)
        if not customer:
            return None

        # 更新欄位
        update_data = customer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)

        await db.commit()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def delete(db: AsyncSession, customer_id: str) -> bool:
        """刪除客戶"""
        customer = await CustomerCRUD.get_by_id(db, customer_id)
        if not customer:
            return False

        await db.delete(customer)
        await db.commit()
        return True

    @staticmethod
    async def get_statistics(db: AsyncSession) -> dict:
        """取得客戶統計資料"""
        # 總客戶數
        total_result = await db.execute(select(func.count()).select_from(Customer))
        total_customers = total_result.scalar()

        # AA 客戶數
        aa_result = await db.execute(
            select(func.count()).select_from(Customer).where(Customer.is_aa_customer == True)
        )
        aa_customers = aa_result.scalar()

        # 按經營階段分類
        stage_result = await db.execute(
            select(
                Customer.customer_stage,
                func.count(Customer.id)
            ).group_by(Customer.customer_stage)
        )
        by_stage = {str(stage.value if stage else "unknown"): count for stage, count in stage_result}

        # 按狀態分類
        status_result = await db.execute(
            select(
                Customer.current_status,
                func.count(Customer.id)
            ).group_by(Customer.current_status)
        )
        by_status = {status.value: count for status, count in status_result}

        # 平均成熟度評分
        avg_score_result = await db.execute(
            select(func.avg(Customer.maturity_score)).where(Customer.maturity_score.isnot(None))
        )
        avg_score = avg_score_result.scalar()

        return {
            "total_customers": total_customers,
            "aa_customers": aa_customers,
            "by_stage": by_stage,
            "by_status": by_status,
            "average_maturity_score": float(avg_score) if avg_score else None
        }


# 建立全域實例
customer_crud = CustomerCRUD()
