"""
AI 分析整合服務

整合音訊轉文字、對話分析、客戶評估等 AI 功能
"""
import json
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.openai_service import openai_service
from app.crud.ai_analysis import ai_analysis_crud
from app.crud.customer_evaluation import customer_evaluation_crud
from app.crud.customer import customer_crud
from app.models.base import Interaction, CustomerGrade


# 載入問卷資料
QUESTIONNAIRE_PATH = Path(__file__).parent.parent / "data" / "questionnaire_30.json"
with open(QUESTIONNAIRE_PATH, "r", encoding="utf-8") as f:
    QUESTIONNAIRE_DATA = json.load(f)


class AIAnalysisService:
    """AI 分析整合服務"""

    async def analyze_after_transcription(
        self,
        db: AsyncSession,
        interaction: Interaction,
        transcript_text: str
    ) -> Optional[Dict[str, Any]]:
        """
        音訊轉文字後自動執行 AI 分析流程

        流程:
        1. 分析對話並匹配業務30問
        2. 提取客戶資訊
        3. 評估 AA 客戶
        4. 建立 AIAnalysis 記錄
        5. 建立 CustomerEvaluation 記錄
        6. 更新 Customer 資訊（如有需要）

        Args:
            db: 資料庫 session
            interaction: 互動記錄
            transcript_text: 轉換後的文字稿

        Returns:
            分析結果摘要,若分析失敗則返回 None
        """
        try:
            # 1. 分析對話並匹配業務30問
            conversation_analysis = await openai_service.analyze_conversation(
                conversation_text=transcript_text,
                questionnaire=QUESTIONNAIRE_DATA
            )

            matched_questions = conversation_analysis.get("matched_questions", [])
            summary = conversation_analysis.get("summary", "")

            # 計算覆蓋率
            coverage_rate = Decimal(len(matched_questions) / len(QUESTIONNAIRE_DATA) * 100) if matched_questions else Decimal(0)

            # 2. 提取客戶資訊
            customer_info = await openai_service.extract_customer_info(
                conversation_text=transcript_text
            )

            # 3. 評估 AA 客戶
            # 構建問卷資料用於評估
            questionnaire_data = {
                "matched_questions": matched_questions,
                "customer_info": customer_info,
                "coverage_rate": float(coverage_rate)
            }

            aa_assessment = await openai_service.assess_aa_customer(
                questionnaire_data=questionnaire_data
            )

            # 4. 建立 AIAnalysis 記錄
            ai_analysis = await ai_analysis_crud.create(
                db=db,
                interaction_id=interaction.id,
                customer_id=interaction.customer_id,
                matched_questions=matched_questions,
                summary=summary,
                coverage_rate=coverage_rate,
                quality_score=None,  # TODO: 實作品質評分邏輯
                extracted_info=customer_info,
                is_aa_customer=aa_assessment.get("is_aa_customer", False),
                aa_confidence=aa_assessment.get("confidence", 0),
                aa_reasons=aa_assessment.get("reasons", []),
                aa_score=aa_assessment.get("score", 0),
                ai_model_version="gpt-4o-mini"  # TODO: 從 settings 取得
            )

            # 5. 建立 CustomerEvaluation 記錄
            # 根據 AA 評估結果決定等級
            if aa_assessment.get("is_aa_customer", False):
                grade = CustomerGrade.AA
            elif aa_assessment.get("score", 0) >= 75:
                grade = CustomerGrade.A
            elif aa_assessment.get("score", 0) >= 50:
                grade = CustomerGrade.B
            else:
                grade = CustomerGrade.C

            evaluation = await customer_evaluation_crud.create(
                db=db,
                customer_id=interaction.customer_id,
                grade=grade,
                score=aa_assessment.get("score", 0),
                evaluation_data={
                    "matched_questions": matched_questions,
                    "coverage_rate": float(coverage_rate),
                    "aa_assessment": aa_assessment,
                    "customer_info": customer_info
                },
                ai_analysis_id=ai_analysis.id,
                criteria_version="1.0",
                notes=f"基於互動記錄 {interaction.id} 的 AI 自動評估"
            )

            # 6. 更新 Customer 資訊（如有新資訊且欄位為空）
            await self._update_customer_info_if_needed(
                db=db,
                customer_id=interaction.customer_id,
                customer_info=customer_info
            )

            return {
                "ai_analysis_id": ai_analysis.id,
                "evaluation_id": evaluation.id,
                "is_aa_customer": aa_assessment.get("is_aa_customer", False),
                "grade": grade.value,
                "score": aa_assessment.get("score", 0),
                "coverage_rate": float(coverage_rate),
                "matched_questions_count": len(matched_questions)
            }

        except Exception as e:
            # AI 分析失敗不影響文字稿儲存
            print(f"AI 分析流程失敗: {str(e)}")
            # 不拋出異常,讓文字稿仍能成功儲存
            return None

    async def _update_customer_info_if_needed(
        self,
        db: AsyncSession,
        customer_id: str,
        customer_info: Dict[str, Any]
    ) -> None:
        """
        根據 AI 提取的資訊更新客戶資料（僅當欄位為空時）

        Args:
            db: 資料庫 session
            customer_id: 客戶 ID
            customer_info: AI 提取的客戶資訊
        """
        try:
            customer = await customer_crud.get_by_id(db, customer_id)
            if not customer:
                return

            update_data = {}

            # 僅當欄位為空時才更新
            if not customer.company_name and customer_info.get("company_name"):
                update_data["company_name"] = customer_info["company_name"]

            # TODO: 根據 Customer 模型的實際欄位調整
            # 如果有其他欄位需要更新,在此添加

            if update_data:
                await customer_crud.update(db, customer_id, **update_data)

        except Exception as e:
            print(f"更新客戶資訊失敗: {str(e)}")
            # 不拋出異常,允許流程繼續


# 建立全域實例
ai_analysis_service = AIAnalysisService()
