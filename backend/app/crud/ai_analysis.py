"""
AI Analysis CRUD 操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any, List
from decimal import Decimal

from app.models.base import AIAnalysis


class AIAnalysisCRUD:
    """AI Analysis CRUD 操作類"""

    @staticmethod
    async def create(
        db: AsyncSession,
        interaction_id: str,
        customer_id: str,
        matched_questions: List[Dict[str, Any]],
        summary: Optional[str] = None,
        coverage_rate: Optional[Decimal] = None,
        quality_score: Optional[int] = None,
        extracted_info: Optional[Dict[str, Any]] = None,
        is_aa_customer: Optional[bool] = None,
        aa_confidence: Optional[int] = None,
        aa_reasons: Optional[List[str]] = None,
        aa_score: Optional[int] = None,
        ai_model_version: Optional[str] = None
    ) -> AIAnalysis:
        """
        建立 AI 分析記錄

        Args:
            db: 資料庫 session
            interaction_id: 互動記錄 ID
            customer_id: 客戶 ID
            matched_questions: 匹配的業務30問
            summary: 對話摘要
            coverage_rate: 覆蓋率 (0-100)
            quality_score: 品質評分 (0-100)
            extracted_info: 提取的客戶資訊
            is_aa_customer: 是否為 AA 客戶
            aa_confidence: AA 評估信心度
            aa_reasons: AA 判定原因
            aa_score: AA 評分
            ai_model_version: AI 模型版本

        Returns:
            建立的 AI 分析記錄
        """
        ai_analysis = AIAnalysis(
            interaction_id=interaction_id,
            customer_id=customer_id,
            matched_questions=matched_questions,
            summary=summary,
            coverage_rate=coverage_rate,
            quality_score=quality_score,
            extracted_info=extracted_info or {},
            is_aa_customer=is_aa_customer,
            aa_confidence=aa_confidence,
            aa_reasons=aa_reasons or [],
            aa_score=aa_score,
            ai_model_version=ai_model_version
        )

        db.add(ai_analysis)
        await db.commit()
        await db.refresh(ai_analysis)
        return ai_analysis

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        analysis_id: str
    ) -> Optional[AIAnalysis]:
        """
        根據 ID 取得 AI 分析記錄

        Args:
            db: 資料庫 session
            analysis_id: AI 分析記錄 ID

        Returns:
            AI 分析記錄或 None
        """
        result = await db.execute(
            select(AIAnalysis).where(AIAnalysis.id == analysis_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_interaction(
        db: AsyncSession,
        interaction_id: str
    ) -> Optional[AIAnalysis]:
        """
        根據互動記錄 ID 取得 AI 分析

        Args:
            db: 資料庫 session
            interaction_id: 互動記錄 ID

        Returns:
            AI 分析記錄或 None
        """
        result = await db.execute(
            select(AIAnalysis).where(AIAnalysis.interaction_id == interaction_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_customer(
        db: AsyncSession,
        customer_id: str
    ) -> List[AIAnalysis]:
        """
        根據客戶 ID 取得所有 AI 分析記錄

        Args:
            db: 資料庫 session
            customer_id: 客戶 ID

        Returns:
            AI 分析記錄列表
        """
        result = await db.execute(
            select(AIAnalysis)
            .where(AIAnalysis.customer_id == customer_id)
            .order_by(AIAnalysis.created_at.desc())
        )
        return list(result.scalars().all())


# 建立全域實例
ai_analysis_crud = AIAnalysisCRUD()
