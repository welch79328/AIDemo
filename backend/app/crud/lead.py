"""
Lead Import CRUD 操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, insert
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.base import ImportBatch, Customer, ImportStatus


class LeadImportCRUD:
    """Lead Import CRUD 操作類"""

    @staticmethod
    async def create_import_batch(
        db: AsyncSession,
        file_name: str,
        file_path: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> ImportBatch:
        """建立導入批次記錄"""
        import_batch = ImportBatch(
            file_name=file_name,
            file_path=file_path,
            status=ImportStatus.PROCESSING,
            total_rows=0,
            success_count=0,
            fail_count=0,
            duplicate_count=0,
            created_by=created_by
        )

        db.add(import_batch)
        await db.commit()
        await db.refresh(import_batch)
        return import_batch

    @staticmethod
    async def update_import_batch(
        db: AsyncSession,
        batch_id: str,
        status: ImportStatus,
        total_rows: int,
        success_count: int,
        fail_count: int,
        duplicate_count: int = 0,
        error_log: Optional[Dict] = None
    ) -> ImportBatch:
        """更新導入批次狀態"""
        result = await db.execute(
            select(ImportBatch).where(ImportBatch.id == batch_id)
        )
        batch = result.scalar_one_or_none()

        if not batch:
            raise ValueError(f"ImportBatch {batch_id} not found")

        batch.status = status
        batch.total_rows = total_rows
        batch.success_count = success_count
        batch.fail_count = fail_count
        batch.duplicate_count = duplicate_count
        batch.completed_at = datetime.now() if status != ImportStatus.PROCESSING else None

        if error_log:
            batch.error_log = error_log

        await db.commit()
        await db.refresh(batch)
        return batch

    @staticmethod
    async def batch_create_customers(
        db: AsyncSession,
        customers_data: List[Dict[str, Any]],
        import_batch_id: str,
        batch_size: int = 100
    ) -> int:
        """
        批次建立客戶

        Args:
            db: 資料庫 session
            customers_data: 客戶資料列表
            import_batch_id: 導入批次 ID
            batch_size: 批次大小

        Returns:
            成功建立的客戶數量
        """
        total_created = 0

        # Customer 模型允許的欄位
        allowed_fields = {
            'company_name', 'contact_person', 'contact_phone', 'contact_email',
            'website', 'is_aa_customer', 'customer_stage', 'maturity_score',
            'basic_info', 'current_status', 'ad_source', 'import_batch_id', 'created_by'
        }

        # 分批插入
        for i in range(0, len(customers_data), batch_size):
            batch = customers_data[i:i + batch_size]

            # 過濾並準備資料
            filtered_batch = []
            for row in batch:
                # 只保留 Customer 模型需要的欄位
                filtered_row = {k: v for k, v in row.items() if k in allowed_fields}

                # 處理 company_name（必填欄位）
                if not filtered_row.get('company_name'):
                    # 如果沒有公司名稱，使用聯絡人姓名
                    filtered_row['company_name'] = row.get('contact_person', '未提供')

                # 新增 import_batch_id
                filtered_row['import_batch_id'] = import_batch_id
                filtered_batch.append(filtered_row)

            # 批次插入（使用異步方式）
            stmt = insert(Customer).values(filtered_batch)
            await db.execute(stmt)
            total_created += len(filtered_batch)

        await db.commit()
        return total_created

    @staticmethod
    async def create_customer(
        db: AsyncSession,
        customer_data: Dict[str, Any],
        import_batch_id: Optional[str] = None
    ) -> Customer:
        """建立單一客戶"""
        customer = Customer(
            company_name=customer_data.get("company_name"),
            contact_person=customer_data.get("contact_person"),
            contact_phone=customer_data.get("contact_phone"),
            contact_email=customer_data.get("contact_email"),
            website=customer_data.get("website"),
            ad_source=customer_data.get("ad_source"),
            import_batch_id=import_batch_id,
            created_by=None  # MVP: 無認證
        )

        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def update_customer(
        db: AsyncSession,
        customer_id: str,
        customer_data: Dict[str, Any]
    ) -> Optional[Customer]:
        """更新客戶資料（用於處理重複資料時更新現有記錄）"""
        result = await db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()

        if not customer:
            return None

        # 更新欄位
        for key, value in customer_data.items():
            if hasattr(customer, key) and value is not None:
                setattr(customer, key, value)

        await db.commit()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def get_import_batch_by_id(
        db: AsyncSession,
        batch_id: str
    ) -> Optional[ImportBatch]:
        """根據 ID 取得導入批次"""
        result = await db.execute(
            select(ImportBatch).where(ImportBatch.id == batch_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_import_batches(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        status: Optional[ImportStatus] = None
    ) -> tuple[List[ImportBatch], int]:
        """
        取得導入批次列表（分頁）

        Returns:
            tuple: (批次列表, 總數)
        """
        # 構建查詢
        query = select(ImportBatch).order_by(ImportBatch.created_at.desc())
        count_query = select(func.count()).select_from(ImportBatch)

        # 狀態篩選
        if status:
            query = query.where(ImportBatch.status == status)
            count_query = count_query.where(ImportBatch.status == status)

        # 計算總數
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分頁
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # 執行查詢
        result = await db.execute(query)
        batches = result.scalars().all()

        return list(batches), total


# 建立全域實例
lead_import_crud = LeadImportCRUD()
