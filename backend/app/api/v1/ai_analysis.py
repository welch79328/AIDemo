"""
AI 分析 API 路由
"""
import json
import time
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.openai_service import openai_service
from app.services.file_service import FileService, LocalStorage
from app.services.ai_analysis_service import ai_analysis_service
from app.crud.interaction import interaction_crud
from app.models.base import InteractionType
from app.schemas.ai_analysis import (
    ConversationAnalysisRequest,
    ConversationAnalysisResponse,
    CustomerInfoExtraction,
    AACustomerAssessment,
    AACustomerAssessmentRequest,
    AudioTranscribeRequest,
    AudioTranscribeResponse
)

router = APIRouter(prefix="/ai", tags=["ai-analysis"])

# 載入問卷資料
QUESTIONNAIRE_PATH = Path(__file__).parent.parent.parent / "data" / "questionnaire_30.json"
with open(QUESTIONNAIRE_PATH, "r", encoding="utf-8") as f:
    QUESTIONNAIRE_DATA = json.load(f)


@router.post("/analyze-conversation", response_model=ConversationAnalysisResponse)
async def analyze_conversation(
    request: ConversationAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    分析對談內容並匹配問卷問題

    這個 API 會使用 OpenAI 分析業務與客戶的對談記錄，
    自動匹配「客戶健檢表 30 問」中的問題，並提取答案。
    """
    try:
        # 呼叫 OpenAI 服務進行分析
        analysis_result = await openai_service.analyze_conversation(
            conversation_text=request.conversation_text,
            questionnaire=QUESTIONNAIRE_DATA
        )

        # 同時提取客戶基本資訊
        customer_info = await openai_service.extract_customer_info(
            conversation_text=request.conversation_text
        )

        # 組合回應
        response = ConversationAnalysisResponse(
            matched_questions=analysis_result.get("matched_questions", []),
            summary=analysis_result.get("summary", ""),
            customer_info=customer_info
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI 分析失敗: {str(e)}"
        )


@router.post("/extract-customer-info", response_model=CustomerInfoExtraction)
async def extract_customer_info(
    request: ConversationAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    從對談中提取客戶基本資訊

    提取包括：公司名稱、物件數量、人員數量、業務類型、主要痛點等
    """
    try:
        customer_info = await openai_service.extract_customer_info(
            conversation_text=request.conversation_text
        )

        return CustomerInfoExtraction(**customer_info)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"客戶資訊提取失敗: {str(e)}"
        )


@router.post("/assess-aa-customer", response_model=AACustomerAssessment)
async def assess_aa_customer(
    request: AACustomerAssessmentRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    評估是否為 AA 客戶（高價值客戶）

    根據問卷答案，使用 AI 評估客戶是否符合 AA 客戶標準。
    AA 客戶判定標準包括：
    - 有規劃擴大營運
    - 大房東數量多
    - 包租物件多（100-200戶以上）
    - 有外籍租客
    - 物件數量多
    - 有完整組織架構
    """
    try:
        assessment = await openai_service.assess_aa_customer(
            questionnaire_data=request.questionnaire_data
        )

        return AACustomerAssessment(**assessment)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AA 客戶評估失敗: {str(e)}"
        )


@router.get("/questionnaire")
async def get_questionnaire():
    """
    取得完整的客戶健檢表 30 問問卷

    返回問卷結構，包含問題編號、階段（一訪/二訪）、問題內容、選項等
    """
    return {
        "questionnaire": QUESTIONNAIRE_DATA,
        "total_questions": len(QUESTIONNAIRE_DATA),
        "first_visit_questions": len([q for q in QUESTIONNAIRE_DATA if q["phase"] == "一訪"]),
        "second_visit_questions": len([q for q in QUESTIONNAIRE_DATA if q["phase"] == "二訪"])
    }


@router.post("/transcribe", response_model=AudioTranscribeResponse)
async def transcribe_audio(
    request: AudioTranscribeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    將音訊檔轉換為文字稿

    使用 OpenAI Whisper API 將互動記錄中的音訊檔轉換為文字。
    轉換完成後會自動更新 interaction 的 transcript_text 欄位。

    Args:
        request: 包含 interaction_id 和 language 的請求
        db: 資料庫 session

    Returns:
        AudioTranscribeResponse: 包含文字稿、時長、處理時間等資訊

    Raises:
        HTTPException 400: Interaction 不存在或非音訊檔
        HTTPException 500: AI 服務錯誤
        HTTPException 503: AI 服務暫時不可用
    """
    start_time = time.time()

    # 1. 驗證 interaction 是否存在
    interaction = await interaction_crud.get_by_id(db, request.interaction_id)
    if not interaction:
        raise HTTPException(
            status_code=404,
            detail=f"互動記錄不存在: {request.interaction_id}"
        )

    # 2. 驗證是否為音訊檔
    if interaction.interaction_type != InteractionType.AUDIO:
        raise HTTPException(
            status_code=400,
            detail=f"互動記錄類型錯誤: {interaction.interaction_type}。僅支援音訊檔 (AUDIO)。"
        )

    # 3. 驗證檔案路徑存在
    if not interaction.file_path:
        raise HTTPException(
            status_code=400,
            detail="互動記錄缺少檔案路徑"
        )

    # 4. 取得檔案完整路徑
    file_service = FileService(storage=LocalStorage())
    try:
        audio_file_path = file_service.get_file_path(interaction.file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"取得檔案路徑失敗: {str(e)}"
        )

    # 5. 呼叫 OpenAI Whisper API 進行轉文字
    try:
        transcribe_result = await openai_service.transcribe_audio(
            audio_file_path=audio_file_path,
            language=request.language
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"音訊檔案不存在: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        # API 錯誤
        raise HTTPException(
            status_code=503,
            detail=f"AI 服務暫時不可用: {str(e)}"
        )

    # 6. 更新 interaction 的 transcript_text
    try:
        await interaction_crud.update(
            db,
            interaction_id=request.interaction_id,
            transcript_text=transcribe_result["text"]
        )
    except Exception as e:
        # 即使更新失敗,仍回傳轉換結果
        print(f"更新 transcript_text 失敗: {str(e)}")

    # 7. 【新增】自動觸發 AI 分析流程
    # 分析對話、評估客戶、建立 AIAnalysis 和 CustomerEvaluation 記錄
    analysis_result = await ai_analysis_service.analyze_after_transcription(
        db=db,
        interaction=interaction,
        transcript_text=transcribe_result["text"]
    )

    # 如果分析成功,記錄結果（失敗不影響轉文字流程）
    if analysis_result:
        print(f"AI 分析完成: {analysis_result}")

    # 8. 計算處理時間
    processing_time = time.time() - start_time

    # 9. 回傳結果
    return AudioTranscribeResponse(
        interaction_id=request.interaction_id,
        transcript_text=transcribe_result["text"],
        audio_duration=interaction.audio_duration or 0,
        processing_time=processing_time,
        ai_model_version=transcribe_result["model"]
    )
