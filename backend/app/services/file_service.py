"""
檔案管理服務
提供檔案上傳、儲存、檢索功能
"""
import os
import uuid
import re
from pathlib import Path
from typing import Dict, Any, Protocol
from fastapi import UploadFile
import shutil


class StorageBackend(Protocol):
    """儲存後端抽象介面"""

    def save_file(self, file: UploadFile, subfolder: str) -> tuple[str, Dict[str, Any]]:
        """
        儲存檔案

        Args:
            file: 上傳的檔案
            subfolder: 子資料夾路徑

        Returns:
            (相對路徑, metadata)
        """
        ...

    def get_file_path(self, relative_path: str) -> Path:
        """取得檔案完整路徑"""
        ...

    def delete_file(self, relative_path: str) -> None:
        """刪除檔案"""
        ...


class LocalStorage:
    """本地檔案儲存"""

    def __init__(self, base_path: str = "./storage"):
        """
        初始化本地儲存

        Args:
            base_path: 基礎儲存路徑
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_file(self, file: UploadFile, subfolder: str) -> tuple[str, Dict[str, Any]]:
        """
        儲存檔案到本地

        Args:
            file: 上傳的檔案
            subfolder: 子資料夾（如 "documents", "audio"）

        Returns:
            (相對路徑, metadata)
        """
        # 創建子資料夾
        folder_path = self.base_path / subfolder
        folder_path.mkdir(parents=True, exist_ok=True)

        # 清理檔案名稱
        safe_filename = self._sanitize_filename(file.filename)

        # 生成唯一檔案名稱
        unique_filename = f"{uuid.uuid4()}_{safe_filename}"
        file_path = folder_path / unique_filename

        # 儲存檔案
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # 取得檔案大小
        file_size = file_path.stat().st_size

        # 相對路徑
        relative_path = f"{subfolder}/{unique_filename}"

        metadata = {
            "file_name": file.filename,
            "file_size": file_size,
            "file_type": file.content_type
        }

        return relative_path, metadata

    def get_file_path(self, relative_path: str) -> Path:
        """
        取得檔案完整路徑

        Args:
            relative_path: 相對路徑

        Returns:
            完整檔案路徑
        """
        return self.base_path / relative_path

    def delete_file(self, relative_path: str) -> None:
        """
        刪除檔案

        Args:
            relative_path: 相對路徑
        """
        file_path = self.get_file_path(relative_path)
        if file_path.exists():
            file_path.unlink()

    def _sanitize_filename(self, filename: str) -> str:
        """
        清理檔案名稱（防止路徑穿越攻擊）

        Args:
            filename: 原始檔案名稱

        Returns:
            清理後的檔案名稱
        """
        # 移除路徑分隔符
        filename = filename.replace("\\", "_").replace("/", "_")

        # 移除 ..
        filename = filename.replace("..", "")

        # 替換空格
        filename = filename.replace(" ", "_")

        # 移除開頭的 . 和 _
        filename = filename.lstrip("._")

        return filename


class FileService:
    """檔案管理服務"""

    # 允許的檔案類型（MIME type）
    ALLOWED_DOCUMENT_TYPES = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "image/jpeg",
        "image/png"
    }

    ALLOWED_AUDIO_TYPES = {
        "audio/mpeg",  # .mp3
        "audio/wav",
        "audio/mp4",   # .m4a
        "audio/x-m4a"
    }

    # 檔案大小限制（bytes）
    MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_AUDIO_SIZE = 50 * 1024 * 1024     # 50MB

    def __init__(self, storage: StorageBackend = None):
        """
        初始化檔案服務

        Args:
            storage: 儲存後端（預設使用 LocalStorage）
        """
        self.storage = storage or LocalStorage()

    def upload_file(
        self,
        file: UploadFile,
        file_category: str = "document"
    ) -> Dict[str, Any]:
        """
        上傳檔案

        Args:
            file: 上傳的檔案
            file_category: 檔案類別（"document" 或 "audio"）

        Returns:
            檔案資訊（file_path, file_name, file_size, file_type）

        Raises:
            ValueError: 檔案類型不支援或檔案過大
        """
        # 驗證檔案類型
        if not self._validate_file_type(file.filename, file.content_type, file_category):
            raise ValueError(f"不支援的檔案類型: {file.content_type}")

        # 驗證檔案大小
        file.file.seek(0, 2)  # 移到檔案結尾
        file_size = file.file.tell()
        file.file.seek(0)     # 回到檔案開頭

        size_limit = self._get_file_size_limit(file_category)
        if file_size > size_limit:
            raise ValueError(
                f"檔案大小超過限制: {file_size / 1024 / 1024:.2f}MB "
                f"(最大 {size_limit / 1024 / 1024:.0f}MB)"
            )

        # 根據類別決定子資料夾
        subfolder = f"interactions/{file_category}s"  # "documents" or "audios"

        # 儲存檔案
        file_path, metadata = self.storage.save_file(file, subfolder)

        return {
            "file_path": file_path,
            **metadata
        }

    def get_file_path(self, relative_path: str) -> Path:
        """
        取得檔案完整路徑

        Args:
            relative_path: 相對路徑

        Returns:
            完整檔案路徑
        """
        return self.storage.get_file_path(relative_path)

    def delete_file(self, file_path: str) -> None:
        """
        刪除檔案

        Args:
            file_path: 檔案路徑
        """
        self.storage.delete_file(file_path)

    def _validate_file_type(
        self,
        filename: str,
        content_type: str,
        file_category: str
    ) -> bool:
        """
        驗證檔案類型

        Args:
            filename: 檔案名稱
            content_type: MIME 類型
            file_category: 檔案類別

        Returns:
            是否有效
        """
        if file_category == "document":
            return content_type in self.ALLOWED_DOCUMENT_TYPES
        elif file_category == "audio":
            return content_type in self.ALLOWED_AUDIO_TYPES
        else:
            return False

    def _get_file_size_limit(self, file_category: str) -> int:
        """
        取得檔案大小限制

        Args:
            file_category: 檔案類別

        Returns:
            大小限制（bytes）
        """
        if file_category == "document":
            return self.MAX_DOCUMENT_SIZE
        elif file_category == "audio":
            return self.MAX_AUDIO_SIZE
        else:
            return 0


# 建立全域實例
file_service = FileService()
