"""
OpenAIService 測試

遵循 TDD 原則:
1. RED: 先寫測試 (此檔案)
2. GREEN: 實作功能讓測試通過
3. REFACTOR: 重構優化
"""
import os
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.openai_service import OpenAIService


class TestOpenAIServiceTranscribe:
    """OpenAIService.transcribe_audio() 測試"""

    @pytest.fixture
    def service(self):
        """創建 OpenAIService 實例"""
        return OpenAIService()

    @pytest.fixture
    def mock_audio_file(self, tmp_path):
        """創建模擬音訊檔案"""
        audio_path = tmp_path / "test_audio.mp3"
        # 創建小型測試檔案 (< 25MB)
        audio_path.write_bytes(b"fake audio content" * 100)
        return audio_path

    @pytest.fixture
    def large_audio_file(self, tmp_path):
        """創建超過 25MB 的大型音訊檔案"""
        audio_path = tmp_path / "large_audio.mp3"
        # 創建 26MB 檔案
        audio_path.write_bytes(b"x" * (26 * 1024 * 1024))
        return audio_path

    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self, service, mock_audio_file):
        """測試音訊轉文字成功"""
        # Mock OpenAI API 回應
        mock_response = MagicMock()
        mock_response.text = "這是一段測試音訊轉換的文字稿內容。"

        with patch.object(
            service.client.audio.transcriptions,
            'create',
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            result = await service.transcribe_audio(
                audio_file_path=mock_audio_file,
                language="zh"
            )

            # 驗證回傳格式
            assert "text" in result
            assert "model" in result
            assert result["text"] == "這是一段測試音訊轉換的文字稿內容。"
            assert result["model"] == "whisper-1"

    @pytest.mark.asyncio
    async def test_transcribe_audio_english(self, service, mock_audio_file):
        """測試英文音訊轉文字"""
        mock_response = MagicMock()
        mock_response.text = "This is a test transcription."

        with patch.object(
            service.client.audio.transcriptions,
            'create',
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            result = await service.transcribe_audio(
                audio_file_path=mock_audio_file,
                language="en"
            )

            assert result["text"] == "This is a test transcription."

    @pytest.mark.asyncio
    async def test_transcribe_audio_default_language(self, service, mock_audio_file):
        """測試預設語言 (繁體中文)"""
        mock_response = MagicMock()
        mock_response.text = "預設語言測試"

        with patch.object(
            service.client.audio.transcriptions,
            'create',
            new_callable=AsyncMock,
            return_value=mock_response
        ) as mock_create:
            result = await service.transcribe_audio(
                audio_file_path=mock_audio_file
            )

            # 驗證呼叫參數
            call_args = mock_create.call_args
            assert call_args.kwargs['language'] == 'zh'
            assert call_args.kwargs['model'] == 'whisper-1'

    @pytest.mark.asyncio
    async def test_transcribe_audio_file_too_large(self, service, large_audio_file):
        """測試檔案過大 (> 25MB) 拋出錯誤"""
        with pytest.raises(ValueError) as exc_info:
            await service.transcribe_audio(
                audio_file_path=large_audio_file,
                language="zh"
            )

        assert "25MB" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_transcribe_audio_file_not_found(self, service):
        """測試檔案不存在"""
        non_existent_file = Path("/path/to/non/existent/file.mp3")

        with pytest.raises(FileNotFoundError):
            await service.transcribe_audio(
                audio_file_path=non_existent_file,
                language="zh"
            )

    @pytest.mark.asyncio
    async def test_transcribe_audio_api_error(self, service, mock_audio_file):
        """測試 OpenAI API 錯誤處理"""
        with patch.object(
            service.client.audio.transcriptions,
            'create',
            new_callable=AsyncMock,
            side_effect=Exception("OpenAI API Error")
        ):
            with pytest.raises(Exception) as exc_info:
                await service.transcribe_audio(
                    audio_file_path=mock_audio_file,
                    language="zh"
                )

            assert "OpenAI API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_transcribe_audio_empty_file(self, service, tmp_path):
        """測試空白音訊檔案"""
        empty_file = tmp_path / "empty.mp3"
        empty_file.write_bytes(b"")

        mock_response = MagicMock()
        mock_response.text = ""

        with patch.object(
            service.client.audio.transcriptions,
            'create',
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            result = await service.transcribe_audio(
                audio_file_path=empty_file,
                language="zh"
            )

            assert result["text"] == ""

    @pytest.mark.asyncio
    async def test_transcribe_audio_response_format(self, service, mock_audio_file):
        """測試 response_format 參數"""
        mock_response = MagicMock()
        mock_response.text = "測試文字"

        with patch.object(
            service.client.audio.transcriptions,
            'create',
            new_callable=AsyncMock,
            return_value=mock_response
        ) as mock_create:
            await service.transcribe_audio(
                audio_file_path=mock_audio_file,
                language="zh"
            )

            # 驗證 response_format 參數
            call_args = mock_create.call_args
            assert call_args.kwargs['response_format'] == 'text'
