"""
AI 分析相關 Schema
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ConversationAnalysisRequest(BaseModel):
    """對談分析請求"""
    conversation_text: str = Field(..., description="對談記錄文字")
    customer_id: Optional[str] = Field(None, description="客戶 ID（可選）")


class MatchedQuestion(BaseModel):
    """匹配到的問卷問題"""
    question_number: int = Field(..., description="問題編號")
    question_text: str = Field(..., description="問題內容")
    answer: str = Field(..., description="從對談提取的答案")
    confidence: int = Field(..., description="信心度 (0-100)")
    evidence: str = Field(..., description="對談中的相關片段")


class ConversationAnalysisResponse(BaseModel):
    """對談分析回應"""
    matched_questions: List[MatchedQuestion] = Field(..., description="匹配到的問題")
    summary: str = Field(..., description="對談整體摘要")
    customer_info: Optional[Dict[str, Any]] = Field(None, description="提取的客戶資訊")


class CustomerInfoExtraction(BaseModel):
    """客戶資訊提取結果"""
    company_name: Optional[str] = Field(None, description="公司名稱")
    property_count: Optional[int] = Field(None, description="物件數量")
    staff_count: Optional[int] = Field(None, description="人員數量")
    business_type: Optional[str] = Field(None, description="業務類型")
    pain_points: List[str] = Field(default_factory=list, description="主要痛點")


class AACustomerAssessment(BaseModel):
    """AA 客戶評估結果"""
    is_aa_customer: bool = Field(..., description="是否為 AA 客戶")
    confidence: int = Field(..., description="信心度 (0-100)")
    reasons: List[str] = Field(..., description="判定原因")
    score: int = Field(..., description="評分 (0-100)")


class AACustomerAssessmentRequest(BaseModel):
    """AA 客戶評估請求"""
    questionnaire_data: Dict[str, Any] = Field(..., description="問卷答案資料")


# ================================
# Audio Transcription Schemas
# ================================

class AudioTranscribeRequest(BaseModel):
    """音訊轉文字請求"""
    interaction_id: str = Field(..., description="互動記錄 ID（包含音訊檔）")
    language: str = Field(default="zh", description="語言代碼（zh=中文, en=英文）")


class AudioTranscribeResponse(BaseModel):
    """音訊轉文字回應"""
    interaction_id: str = Field(..., description="互動記錄 ID")
    transcript_text: str = Field(..., description="轉換後的文字稿")
    audio_duration: int = Field(..., description="音訊時長（秒）", ge=0)
    processing_time: float = Field(..., description="處理時間（秒）", ge=0)
    ai_model_version: str = Field(..., description="AI 模型版本")
