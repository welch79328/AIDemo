"""
Health Check Report CRUD 操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload
from typing import Optional, List, Tuple, Dict, Any

from app.models.base import HealthCheckReport


class ReportCRUD:
    """Health Check Report CRUD 操作類"""

    @staticmethod
    async def create(
        db: AsyncSession,
        customer_id: str,
        evaluation_id: str,
        file_path: str,
        file_name: str,
        report_format: str = "xlsx",
        report_data: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> HealthCheckReport:
        """
        建立健檢報告記錄

        Args:
            db: 資料庫 session
            customer_id: 客戶 ID
            evaluation_id: 評估記錄 ID
            file_path: 檔案路徑
            file_name: 檔案名稱
            report_format: 報告格式
            report_data: 報告資料
            created_by: 建立者 ID

        Returns:
            建立的健檢報告記錄
        """
        report = HealthCheckReport(
            customer_id=customer_id,
            evaluation_id=evaluation_id,
            file_path=file_path,
            file_name=file_name,
            report_format=report_format,
            report_data=report_data or {},
            created_by=created_by
        )

        db.add(report)
        await db.commit()
        await db.refresh(report)
        return report

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        report_id: str
    ) -> Optional[HealthCheckReport]:
        """
        根據 ID 取得報告記錄

        Args:
            db: 資料庫 session
            report_id: 報告 ID

        Returns:
            報告記錄或 None
        """
        result = await db.execute(
            select(HealthCheckReport)
            .options(
                joinedload(HealthCheckReport.customer),
                joinedload(HealthCheckReport.evaluation)
            )
            .where(HealthCheckReport.id == report_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_customer(
        db: AsyncSession,
        customer_id: str,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[HealthCheckReport], int]:
        """
        根據客戶取得報告列表（分頁）

        Args:
            db: 資料庫 session
            customer_id: 客戶 ID
            page: 頁碼
            limit: 每頁筆數

        Returns:
            (報告列表, 總數)
        """
        # 構建查詢
        query = select(HealthCheckReport).where(
            HealthCheckReport.customer_id == customer_id
        ).order_by(desc(HealthCheckReport.created_at))

        # 計算總數
        from sqlalchemy import func, select as sql_select
        count_query = sql_select(func.count()).select_from(HealthCheckReport).where(
            HealthCheckReport.customer_id == customer_id
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分頁
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # 執行查詢
        result = await db.execute(query)
        reports = result.scalars().all()

        return list(reports), total

    @staticmethod
    async def get_all(
        db: AsyncSession,
        customer_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[HealthCheckReport], int]:
        """
        取得所有報告（分頁，支援篩選）

        Args:
            db: 資料庫 session
            customer_id: 客戶 ID 篩選（可選）
            page: 頁碼
            limit: 每頁筆數

        Returns:
            (報告列表, 總數)
        """
        # 構建查詢
        query = select(HealthCheckReport).options(
            joinedload(HealthCheckReport.customer),
            joinedload(HealthCheckReport.evaluation)
        )

        # 計算總數的查詢
        from sqlalchemy import func, select as sql_select
        count_query = sql_select(func.count()).select_from(HealthCheckReport)

        # 篩選條件
        if customer_id:
            query = query.where(HealthCheckReport.customer_id == customer_id)
            count_query = count_query.where(HealthCheckReport.customer_id == customer_id)

        # 按時間倒序
        query = query.order_by(desc(HealthCheckReport.created_at))

        # 計算總數
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分頁
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # 執行查詢
        result = await db.execute(query)
        reports = result.scalars().all()

        return list(reports), total

    @staticmethod
    async def delete(
        db: AsyncSession,
        report_id: str
    ) -> bool:
        """
        刪除報告記錄

        Args:
            db: 資料庫 session
            report_id: 報告 ID

        Returns:
            是否成功刪除
        """
        result = await db.execute(
            select(HealthCheckReport).where(HealthCheckReport.id == report_id)
        )
        report = result.scalar_one_or_none()

        if not report:
            return False

        # 刪除檔案（如果存在）
        from pathlib import Path
        file_path = Path(report.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                print(f"刪除檔案失敗: {str(e)}")

        # 刪除資料庫記錄
        await db.delete(report)
        await db.commit()
        return True


# 建立全域實例
report_crud = ReportCRUD()
