"""
Customer Evaluation CRUD 操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any, List

from app.models.base import CustomerEvaluation, CustomerGrade


class CustomerEvaluationCRUD:
    """Customer Evaluation CRUD 操作類"""

    @staticmethod
    async def create(
        db: AsyncSession,
        customer_id: str,
        grade: CustomerGrade,
        score: int,
        evaluation_data: Dict[str, Any],
        ai_analysis_id: Optional[str] = None,
        criteria_version: Optional[str] = None,
        notes: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> CustomerEvaluation:
        """
        建立客戶評估記錄

        Args:
            db: 資料庫 session
            customer_id: 客戶 ID
            grade: 客戶等級 (AA/A/B/C)
            score: 評分 (0-100)
            evaluation_data: 完整評估資料
            ai_analysis_id: AI 分析記錄 ID
            criteria_version: 評估規則版本
            notes: 備註
            created_by: 建立者 ID

        Returns:
            建立的客戶評估記錄
        """
        evaluation = CustomerEvaluation(
            customer_id=customer_id,
            ai_analysis_id=ai_analysis_id,
            grade=grade,
            score=score,
            evaluation_data=evaluation_data,
            criteria_version=criteria_version,
            notes=notes,
            created_by=created_by
        )

        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        return evaluation

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        evaluation_id: str
    ) -> Optional[CustomerEvaluation]:
        """
        根據 ID 取得客戶評估記錄

        Args:
            db: 資料庫 session
            evaluation_id: 評估記錄 ID

        Returns:
            客戶評估記錄或 None
        """
        result = await db.execute(
            select(CustomerEvaluation).where(CustomerEvaluation.id == evaluation_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_latest_by_customer(
        db: AsyncSession,
        customer_id: str
    ) -> Optional[CustomerEvaluation]:
        """
        取得客戶最新的評估記錄

        Args:
            db: 資料庫 session
            customer_id: 客戶 ID

        Returns:
            最新的客戶評估記錄或 None
        """
        result = await db.execute(
            select(CustomerEvaluation)
            .where(CustomerEvaluation.customer_id == customer_id)
            .order_by(CustomerEvaluation.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_customer(
        db: AsyncSession,
        customer_id: str
    ) -> List[CustomerEvaluation]:
        """
        取得客戶所有評估記錄

        Args:
            db: 資料庫 session
            customer_id: 客戶 ID

        Returns:
            客戶評估記錄列表
        """
        result = await db.execute(
            select(CustomerEvaluation)
            .where(CustomerEvaluation.customer_id == customer_id)
            .order_by(CustomerEvaluation.created_at.desc())
        )
        return list(result.scalars().all())


# 建立全域實例
customer_evaluation_crud = CustomerEvaluationCRUD()
