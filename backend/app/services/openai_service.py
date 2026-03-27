"""
OpenAI API 服務
用於對談分析、問卷匹配等 AI 功能
"""
import json
from typing import Dict, List, Optional
from pathlib import Path
from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from app.core.config import settings


class OpenAIService:
    """OpenAI API 服務類"""

    def __init__(self):
        """初始化 OpenAI 客戶端"""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE

    async def analyze_conversation(
        self,
        conversation_text: str,
        questionnaire: List[Dict]
    ) -> Dict:
        """
        分析對談內容並匹配問卷問題

        Args:
            conversation_text: 對談記錄文字
            questionnaire: 問卷問題列表

        Returns:
            分析結果，包含匹配的問題和建議答案
        """
        # 構建問卷問題清單
        questions_list = "\n".join([
            f"{q['number']}. [{q['phase']}] {q['question']}"
            for q in questionnaire
        ])

        # 構建 prompt
        system_prompt = """你是一個專業的包租代管業務分析助手。
你的任務是分析業務與客戶的對談記錄，並根據「客戶健檢表 30 問」問卷，提取出對談中已經回答的問題。

【重要提示】
1. 對談內容可能是連續的口語化文字，沒有明確的角色標記（如「業務」「業者」）
2. 請從上下文推斷問答關係，即使問題不是以標準形式提出
3. 某些資訊可能隱含在對話中，需要推理判斷

【特別注意以下問題的多種表述方式】
- Q1 (官網 FB): 包括「有FB」「有粉專」「有官網」「沒有官網」等
- Q2 (LINE管理): 「LINE個人」「LINE OA」「官方帳號」「沒用LINE」等
- Q3 (公司名稱): 公司或品牌名稱
- Q4 (經營階段): 「剛起步」「成立X年」「剛成立公司」「準備公司化」「個人戶」等
- Q5 (公司背景): 「之前做XX」「我們是XX背景」「從XX轉型」「仲介」「建設」「工程」等
- Q6 (物件比例): 「包租X成代管Y成」「主要包租」「主要代管」「純包租」「純代管」等
- Q7 (案場規劃): 「套房」「雅房」「整層」「透套」「共生宅」「商務中心」等
- Q8 (分布地點): 城市區域如「台北」「新北」「板橋」「中永和」「台中」等
- Q9 (社宅): 「有經營社宅」「沒有社宅」等
- Q10 (痛點): 客戶提到的問題或需求
- Q11 (擴大營運): 「有計畫擴大」「要增加物件」「新案場」「不打算擴大」等
- Q12 (公司目標): 「戶數增加」「人員異動」「人力減少」「提升效率」等
- Q13 (組織人力數據): 「我一個人」「X個人」「X個業務Y個客服」「總戶數」「總人數」「人員分工」等
- Q14 (帳務方式): 「紙本記帳」「用系統」「外包會計」「虛擬帳戶」等
- Q15 (大房東數量): 「X個房東」「要給房東報表」「損益表」等
- Q16 (差額發票): 「需要開發票」「包租物件開發票」「不用開發票」等
- Q17 (租客取向): 「高資產」「中資產」「低資產」「學生」「上班族」等
- Q18 (外籍租客): 「有外籍」「X個外籍」「沒有外籍」等
- Q19 (會計部門): 「有會計」「X個會計」「沒有會計」「外包」等
- Q20 (作業方式): 這是最容易遺漏的問題！
  * 系統相關：「用XX系統」「自己開發」「有用軟體」「包管家」「DDROOM」「飛豬」
  * 手工作業：「Excel記帳」「Word打合約」「手寫」「用本子記」「筆記本」
  * 管理方式：「怎麼管理」「如何記錄」「怎麼做帳」「報表怎麼處理」
- Q21 (官網需求): 「有興趣做官網」「已有官網」「不需要官網」等
- Q22 (競品): 「飛豬」「DDROOM」「包管家」「了解過XX」「沒了解過」等
- Q23 (LINE拉群/唐三藏): 「有用」「沒用」等
- Q24 (決策人員): 老闆、負責人、決策者的資訊

【信心度判定原則】
- 明確提及：80-100%
- 合理推斷：60-80%
- 有一定依據但需推理：40-60%
- 請不要過度保守，合理的推理答案也應該回報（信心度 ≥ 40%）

請仔細分析對談內容，找出可以回答以下問卷問題的資訊。
對於每個可以回答的問題，請提供：
1. 問題編號（**務必使用問卷列表中的編號，不要自己推測**）
2. 問題原文（**完整複製問卷列表中的問題文字**）
3. 從對談中提取的答案
4. 信心度（0-100%）
5. 支持此答案的對談片段引用

**重要**: question_number 和 question_text 必須完全對應問卷列表中的資訊！
例如：
- 如果回答的是「公司組織人力數據(會計 業務 經理 )」，question_number 必須是 13
- 如果回答的是「(代管) 大房東數量」，question_number 必須是 15

請以 JSON 格式回覆，格式如下：
{
  "matched_questions": [
    {
      "question_number": 13,
      "question_text": "公司組織人力數據(會計 業務 經理 )",
      "answer": "從對談提取的答案",
      "confidence": 85,
      "evidence": "對談中的相關片段"
    }
  ],
  "summary": "對談整體摘要"
}
"""

        user_prompt = f"""
以下是業務與客戶的對談記錄：

{conversation_text}

---

以下是需要匹配的問卷問題：

{questions_list}

---

請分析對談內容，找出可以回答哪些問卷問題。
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"OpenAI API 錯誤: {str(e)}")
            raise

    async def extract_customer_info(
        self,
        conversation_text: str
    ) -> Dict:
        """
        從對談中提取客戶基本資訊

        Args:
            conversation_text: 對談記錄文字

        Returns:
            客戶資訊字典
        """
        system_prompt = """你是一個資訊提取助手。
請從對談中提取客戶的基本資訊，包括：
- 公司名稱
- 物件數量
- 人員數量
- 主要業務類型（包租/代管/代租）
- 主要痛點

請以 JSON 格式回覆：
{
  "company_name": "公司名稱（如果未提及則為 null）",
  "property_count": 物件數量（數字，如果未提及則為 null）,
  "staff_count": 人員數量（數字，如果未提及則為 null）,
  "business_type": "包租/代管/代租/混合",
  "pain_points": ["痛點1", "痛點2"]
}
"""

        user_prompt = f"""
以下是業務與客戶的對談記錄：

{conversation_text}

請提取客戶資訊。
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"OpenAI API 錯誤: {str(e)}")
            raise

    async def assess_aa_customer(
        self,
        questionnaire_data: Dict
    ) -> Dict:
        """
        根據問卷答案評估是否為 AA 客戶

        Args:
            questionnaire_data: 問卷答案資料

        Returns:
            AA 客戶評估結果
        """
        system_prompt = """你是一個包租代管業務專家。

【客戶等級評估標準】

**AA 客戶（score ≥ 80）** - 高價值客戶，符合以下任一強指標：
1. 物件數 > 150 間
2. 大房東數量 > 10 個（每個大房東 ≥ 10 間）
3. 包租物件需開差額發票 > 80 張/月
4. 外籍租客 > 20 間
5. 有明確擴大營運計劃且規模已達中型（> 60間）
6. 多據點經營（≥ 2 個辦公室/城市）

**A 客戶（score 75-79）** - 優質客戶：
- 物件數 60-150 間
- 有專業團隊（≥ 6 人）
- 有會計部門或使用專業系統
- 穩定經營，有擴大計劃

**B 客戶（score 50-74）** - 成長中客戶：
- 物件數 20-60 間
- 小團隊（2-5 人）
- 半系統化管理
- 有成長潛力

**C 客戶（score < 50）** - 小規模客戶：
- 物件數 < 20 間
- 個人或夫妻經營
- 傳統手工管理方式
- 副業或剛起步

【評分原則】
1. 物件數是基礎指標（佔 40% 權重）
2. 組織規模和專業度（佔 30% 權重）
3. 成長性和潛力（佔 20% 權重）
4. 特殊優勢（外籍租客、大房東、系統化等，佔 10% 權重）

【重要】對於物件數 < 20 間的客戶：
- 即使資訊不完整，也應給予合理評分（不要因資訊缺失而評分過低）
- 個人/夫妻經營是正常現象，不應扣分過多
- 手工管理方式（Excel/筆記本）是合理的，應給予 30-50 分

請根據問卷答案，評估客戶等級。

回覆 JSON 格式：
{
  "is_aa_customer": true/false,
  "confidence": 0-100,
  "reasons": ["原因1", "原因2"],
  "score": 0-100
}
"""

        user_prompt = f"""
以下是客戶的問卷答案：

{json.dumps(questionnaire_data, ensure_ascii=False, indent=2)}

請評估是否為 AA 客戶。
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"OpenAI API 錯誤: {str(e)}")
            raise

    async def transcribe_audio(
        self,
        audio_file_path: Path,
        language: str = "zh"
    ) -> Dict:
        """
        使用 Whisper API 將音訊轉為文字

        Args:
            audio_file_path: 音訊檔案路徑
            language: 語言代碼 (zh 為中文, en 為英文)

        Returns:
            {
                "text": "轉換後的文字稿",
                "model": "whisper-1"
            }

        Raises:
            FileNotFoundError: 檔案不存在
            ValueError: 檔案過大 (> 25MB)
            Exception: OpenAI API 錯誤

        Note:
            API 呼叫使用指數退避重試機制,最多重試 3 次
        """
        # 檢查檔案是否存在
        if not audio_file_path.exists():
            raise FileNotFoundError(f"音訊檔案不存在: {audio_file_path}")

        # 檢查檔案大小 (OpenAI Whisper API 限制 25MB)
        file_size = audio_file_path.stat().st_size
        max_size = 25 * 1024 * 1024  # 25MB in bytes

        if file_size > max_size:
            raise ValueError(
                f"音訊檔案過大 ({file_size / 1024 / 1024:.2f}MB)。"
                f"OpenAI Whisper API 限制為 25MB。"
            )

        # 內部方法:呼叫 API (帶重試機制)
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            reraise=True
        )
        async def _call_whisper_api():
            with open(audio_file_path, "rb") as audio_file:
                return await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="text"
                )

        try:
            transcript = await _call_whisper_api()

            return {
                "text": transcript.text,
                "model": "whisper-1"
            }

        except Exception as e:
            print(f"Whisper API 錯誤: {str(e)}")
            raise


# 建立全域實例
openai_service = OpenAIService()
