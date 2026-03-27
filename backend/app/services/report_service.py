"""
報告服務
整合報告生成、儲存、Email 功能
"""
import zipfile
from pathlib import Path
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.excel_service import excel_service
from app.crud.customer import customer_crud
from app.crud.customer_evaluation import customer_evaluation_crud
from app.crud.ai_analysis import ai_analysis_crud
from app.crud.report import report_crud
from app.models.base import HealthCheckReport


class ReportService:
    """報告整合服務類"""

    def __init__(self):
        """初始化 ReportService"""
        self.excel_service = excel_service

    async def generate_health_check_report(
        self,
        db: AsyncSession,
        customer_id: str,
        evaluation_id: Optional[str] = None,
        format: str = "xlsx"
    ) -> HealthCheckReport:
        """
        生成健檢報告

        流程:
        1. 獲取客戶資料
        2. 獲取評估記錄（最新或指定）
        3. 獲取 AI 分析結果
        4. 生成報告檔案（Excel 或 PDF）
        5. 儲存報告記錄

        Args:
            db: 資料庫 session
            customer_id: 客戶 ID
            evaluation_id: 評估記錄 ID（可選，不指定則使用最新）
            format: 報告格式（xlsx 或 pdf，目前僅支援 xlsx）

        Returns:
            建立的 HealthCheckReport 記錄

        Raises:
            ValueError: 客戶或評估記錄不存在
        """
        # 1. 獲取客戶資料
        customer = await customer_crud.get_by_id(db, customer_id)
        if not customer:
            raise ValueError(f"客戶不存在: {customer_id}")

        # 2. 獲取評估記錄
        if evaluation_id:
            evaluation = await customer_evaluation_crud.get_by_id(db, evaluation_id)
            if not evaluation:
                raise ValueError(f"評估記錄不存在: {evaluation_id}")
        else:
            # 使用最新評估記錄
            evaluation = await customer_evaluation_crud.get_latest_by_customer(db, customer_id)
            if not evaluation:
                raise ValueError(f"客戶無評估記錄: {customer_id}")

        # 3. 獲取 AI 分析結果（如果有）
        ai_analysis = None
        if evaluation.ai_analysis_id:
            ai_analysis = await ai_analysis_crud.get_by_id(db, evaluation.ai_analysis_id)

        # 4. 生成報告檔案
        if format == "xlsx":
            file_path = await self.excel_service.generate_health_check_report(
                customer=customer,
                evaluation=evaluation,
                ai_analysis=ai_analysis
            )
        else:
            raise ValueError(f"不支援的報告格式: {format}")

        # 5. 建立 HealthCheckReport 記錄
        report = await report_crud.create(
            db=db,
            customer_id=customer_id,
            evaluation_id=evaluation.id,
            file_path=str(file_path),
            file_name=file_path.name,
            report_format=format,
            report_data={
                "customer_name": customer.company_name or customer.contact_name,
                "grade": evaluation.grade.value if evaluation.grade else None,
                "score": evaluation.score,
                "coverage_rate": float(ai_analysis.coverage_rate) if ai_analysis and ai_analysis.coverage_rate else 0
            }
        )

        return report

    async def generate_batch_reports(
        self,
        db: AsyncSession,
        customer_ids: List[str],
        format: str = "xlsx"
    ) -> Path:
        """
        批次生成報告並打包為 ZIP

        Args:
            db: 資料庫 session
            customer_ids: 客戶 ID 列表
            format: 報告格式

        Returns:
            ZIP 檔案路徑

        Raises:
            ValueError: 客戶數量超過限制（最多 50 個）
        """
        if len(customer_ids) > 50:
            raise ValueError("批次匯出最多支援 50 個客戶")

        # 生成各個客戶的報告
        report_paths = []
        for customer_id in customer_ids:
            try:
                report = await self.generate_health_check_report(
                    db=db,
                    customer_id=customer_id,
                    format=format
                )
                report_paths.append(Path(report.file_path))
            except Exception as e:
                # 記錄錯誤但繼續處理其他客戶
                print(f"生成客戶 {customer_id} 報告失敗: {str(e)}")
                continue

        # 打包成 ZIP
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_dir = Path("storage/reports/batch")
        zip_dir.mkdir(parents=True, exist_ok=True)

        zip_path = zip_dir / f"健檢報告批次匯出_{timestamp}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for report_path in report_paths:
                if report_path.exists():
                    zipf.write(report_path, report_path.name)

        return zip_path

    async def send_report_email(
        self,
        db: AsyncSession,
        report_id: str,
        recipient_email: str,
        subject: Optional[str] = None,
        message: Optional[str] = None
    ) -> bool:
        """
        透過 Email 發送報告

        Args:
            db: 資料庫 session
            report_id: 報告 ID
            recipient_email: 收件人 Email
            subject: 郵件主旨（可選）
            message: 郵件內容（可選）

        Returns:
            是否成功發送

        Note:
            此功能需要配置 SMTP 設定（環境變數）
            MVP 階段暫不實作，返回 False
        """
        # TODO: 實作 Email 發送功能
        # 需要:
        # 1. 從環境變數讀取 SMTP 配置
        # 2. 使用 smtplib 發送郵件
        # 3. 附加報告檔案

        print(f"Email 發送功能尚未實作: report_id={report_id}, recipient={recipient_email}")
        return False


# 建立全域實例
report_service = ReportService()
