"""
FileService 測試
"""
import os
import pytest
from pathlib import Path
from io import BytesIO
from fastapi import UploadFile
from starlette.datastructures import Headers
from app.services.file_service import FileService, LocalStorage


def create_upload_file(filename: str, content: bytes, content_type: str) -> UploadFile:
    """創建 UploadFile 測試物件"""
    file = BytesIO(content)
    headers = Headers({"content-type": content_type})
    upload_file = UploadFile(file=file, filename=filename, headers=headers)
    return upload_file


class TestLocalStorage:
    """LocalStorage 測試"""

    @pytest.fixture
    def storage(self, tmp_path):
        """創建測試用 storage"""
        return LocalStorage(base_path=str(tmp_path))

    @pytest.fixture
    def mock_file(self):
        """創建模擬檔案"""
        content = b"Test file content"
        return create_upload_file("test_document.pdf", content, "application/pdf")

    def test_save_file_success(self, storage, mock_file):
        """測試檔案儲存成功"""
        file_path, metadata = storage.save_file(
            file=mock_file,
            subfolder="documents"
        )

        # 驗證檔案路徑格式
        assert file_path.startswith("documents/")
        assert file_path.endswith("_test_document.pdf")

        # 驗證 metadata
        assert metadata["file_name"] == "test_document.pdf"
        assert metadata["file_size"] > 0
        assert metadata["file_type"] == "application/pdf"

        # 驗證檔案實際存在
        full_path = Path(storage.base_path) / file_path
        assert full_path.exists()
        assert full_path.read_bytes() == b"Test file content"

    def test_save_file_creates_subfolder(self, storage, mock_file):
        """測試自動創建子資料夾"""
        file_path, _ = storage.save_file(mock_file, "test/nested/folder")

        folder_path = Path(storage.base_path) / "test" / "nested" / "folder"
        assert folder_path.exists()
        assert folder_path.is_dir()

    def test_sanitize_filename(self, storage):
        """測試檔案名稱清理（防止路徑穿越）"""
        # 測試路徑穿越攻擊
        assert storage._sanitize_filename("../../etc/passwd") == "etc_passwd"
        assert storage._sanitize_filename("../test.txt") == "test.txt"

        # 測試特殊字元
        assert storage._sanitize_filename("test file.pdf") == "test_file.pdf"
        assert storage._sanitize_filename("中文檔案.docx") == "中文檔案.docx"

    def test_get_file_path(self, storage, mock_file):
        """測試取得檔案完整路徑"""
        file_path, _ = storage.save_file(mock_file, "documents")

        full_path = storage.get_file_path(file_path)
        assert full_path.exists()
        assert full_path.is_file()

    def test_delete_file(self, storage, mock_file):
        """測試刪除檔案"""
        file_path, _ = storage.save_file(mock_file, "documents")

        # 確認檔案存在
        assert storage.get_file_path(file_path).exists()

        # 刪除檔案
        storage.delete_file(file_path)

        # 確認檔案已刪除
        assert not storage.get_file_path(file_path).exists()


class TestFileService:
    """FileService 測試"""

    @pytest.fixture
    def file_service(self, tmp_path):
        """創建測試用 FileService"""
        return FileService(storage=LocalStorage(base_path=str(tmp_path)))

    @pytest.fixture
    def pdf_file(self):
        """PDF 檔案"""
        content = b"%PDF-1.4 test content"
        return create_upload_file("document.pdf", content, "application/pdf")

    @pytest.fixture
    def image_file(self):
        """圖片檔案"""
        content = b"fake image content"
        return create_upload_file("photo.jpg", content, "image/jpeg")

    @pytest.fixture
    def audio_file(self):
        """音訊檔案"""
        content = b"fake audio content"
        return create_upload_file("recording.mp3", content, "audio/mpeg")

    def test_upload_document_success(self, file_service, pdf_file):
        """測試上傳文檔成功"""
        result = file_service.upload_file(pdf_file, file_category="document")

        assert result["file_path"].startswith("interactions/documents/")
        assert result["file_name"] == "document.pdf"
        assert result["file_size"] > 0
        assert result["file_type"] == "application/pdf"

    def test_upload_image_success(self, file_service, image_file):
        """測試上傳圖片成功"""
        result = file_service.upload_file(image_file, file_category="document")

        assert result["file_path"].startswith("interactions/documents/")
        assert result["file_name"] == "photo.jpg"

    def test_upload_audio_success(self, file_service, audio_file):
        """測試上傳音訊成功"""
        result = file_service.upload_file(audio_file, file_category="audio")

        assert result["file_path"].startswith("interactions/audios/")
        assert result["file_name"] == "recording.mp3"

    def test_upload_invalid_file_type(self, file_service):
        """測試上傳不支援的檔案類型"""
        invalid_file = create_upload_file("script.exe", b"malicious", "application/x-msdownload")

        with pytest.raises(ValueError, match="不支援的檔案類型"):
            file_service.upload_file(invalid_file, file_category="document")

    def test_upload_file_too_large_document(self, file_service):
        """測試文檔檔案過大"""
        # 創建 11MB 檔案 (超過 10MB 限制)
        large_content = b"x" * (11 * 1024 * 1024)
        large_file = create_upload_file("large.pdf", large_content, "application/pdf")

        with pytest.raises(ValueError, match="檔案大小超過限制"):
            file_service.upload_file(large_file, file_category="document")

    def test_upload_file_too_large_audio(self, file_service):
        """測試音訊檔案過大"""
        # 創建 51MB 檔案 (超過 50MB 限制)
        large_content = b"x" * (51 * 1024 * 1024)
        large_file = create_upload_file("long_recording.mp3", large_content, "audio/mpeg")

        with pytest.raises(ValueError, match="檔案大小超過限制"):
            file_service.upload_file(large_file, file_category="audio")

    def test_validate_file_type_document(self, file_service):
        """測試文檔類型驗證"""
        # 允許的文檔類型
        assert file_service._validate_file_type("test.pdf", "application/pdf", "document")
        assert file_service._validate_file_type("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "document")
        assert file_service._validate_file_type("test.jpg", "image/jpeg", "document")
        assert file_service._validate_file_type("test.png", "image/png", "document")

        # 不允許的類型
        assert not file_service._validate_file_type("test.exe", "application/x-msdownload", "document")

    def test_validate_file_type_audio(self, file_service):
        """測試音訊類型驗證"""
        # 允許的音訊類型
        assert file_service._validate_file_type("test.mp3", "audio/mpeg", "audio")
        assert file_service._validate_file_type("test.wav", "audio/wav", "audio")
        assert file_service._validate_file_type("test.m4a", "audio/mp4", "audio")

        # 不允許的類型
        assert not file_service._validate_file_type("test.pdf", "application/pdf", "audio")

    def test_get_file_size_limit(self, file_service):
        """測試取得檔案大小限制"""
        # 文檔限制 10MB
        assert file_service._get_file_size_limit("document") == 10 * 1024 * 1024

        # 音訊限制 50MB
        assert file_service._get_file_size_limit("audio") == 50 * 1024 * 1024
