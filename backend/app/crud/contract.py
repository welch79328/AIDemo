"""
簽約記錄 CRUD 操作
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.base import Contract, ContractType
from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractStatistics,
    ContractKPIProgress,
    ContractQueryParams
)


class ContractCRUD:
    """簽約記錄 CRUD 操作類"""

    @staticmethod
    async def create(db: AsyncSession, contract_data: ContractCreate) -> Contract:
        """建立簽約記錄"""
        contract = Contract(
            customer_id=contract_data.customer_id,
            visit_id=contract_data.visit_id,
            contract_date=contract_data.contract_date,
            contract_type=contract_data.contract_type,
            property_count=contract_data.property_count,
            monthly_value=contract_data.monthly_value,
            kpi_property_upload_rate=contract_data.kpi_property_upload_rate,
            kpi_contract_creation_rate=contract_data.kpi_contract_creation_rate,
            kpi_billing_active=contract_data.kpi_billing_active,
            kpi_payment_integrated=contract_data.kpi_payment_integrated,
            kpi_notification_setup=contract_data.kpi_notification_setup,
            kpi_sop_established=contract_data.kpi_sop_established,
            onboarding_success=contract_data.onboarding_success,
            onboarding_date=contract_data.onboarding_date,
            created_by=None,  # MVP 版本無認證系統
        )
        db.add(contract)
        await db.commit()
        await db.refresh(contract)
        return contract

    @staticmethod
    async def get_by_id(db: AsyncSession, contract_id: str) -> Optional[Contract]:
        """根據 ID 取得簽約記錄"""
        result = await db.execute(
            select(Contract)
            .options(selectinload(Contract.customer))
            .filter(Contract.id == contract_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        params: ContractQueryParams
    ) -> tuple[list[Contract], int]:
        """取得簽約記錄列表（分頁、篩選）"""
        # 建立基礎查詢
        query = select(Contract).options(selectinload(Contract.customer))

        # 篩選條件
        if params.customer_id:
            query = query.filter(Contract.customer_id == params.customer_id)

        if params.contract_type:
            query = query.filter(Contract.contract_type == params.contract_type)

        if params.onboarding_success is not None:
            query = query.filter(Contract.onboarding_success == params.onboarding_success)

        if params.date_from:
            query = query.filter(Contract.contract_date >= params.date_from)

        if params.date_to:
            query = query.filter(Contract.contract_date <= params.date_to)

        # 總筆數
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # 排序與分頁
        query = query.order_by(Contract.contract_date.desc())
        query = query.offset((params.page - 1) * params.limit).limit(params.limit)

        # 執行查詢
        result = await db.execute(query)
        contracts = list(result.scalars().all())

        return contracts, total

    @staticmethod
    async def update(
        db: AsyncSession,
        contract_id: str,
        contract_data: ContractUpdate
    ) -> Optional[Contract]:
        """更新簽約記錄"""
        contract = await ContractCRUD.get_by_id(db, contract_id)
        if not contract:
            return None

        # 更新欄位
        update_fields = contract_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(contract, field, value)

        await db.commit()
        await db.refresh(contract)
        return contract

    @staticmethod
    async def delete(db: AsyncSession, contract_id: str) -> bool:
        """刪除簽約記錄"""
        contract = await ContractCRUD.get_by_id(db, contract_id)
        if not contract:
            return False

        await db.delete(contract)
        await db.commit()
        return True

    @staticmethod
    async def get_statistics(db: AsyncSession) -> ContractStatistics:
        """取得簽約統計"""
        # 總簽約數
        total_result = await db.execute(select(func.count(Contract.id)))
        total_contracts = total_result.scalar_one()

        # 按類型統計
        package_rental_result = await db.execute(
            select(func.count(Contract.id))
            .filter(Contract.contract_type == ContractType.PACKAGE_RENTAL)
        )
        package_rental_contracts = package_rental_result.scalar_one()

        property_mgmt_result = await db.execute(
            select(func.count(Contract.id))
            .filter(Contract.contract_type == ContractType.PROPERTY_MGMT)
        )
        property_mgmt_contracts = property_mgmt_result.scalar_one()

        sublease_result = await db.execute(
            select(func.count(Contract.id))
            .filter(Contract.contract_type == ContractType.SUBLEASE)
        )
        sublease_contracts = sublease_result.scalar_one()

        hybrid_result = await db.execute(
            select(func.count(Contract.id))
            .filter(Contract.contract_type == ContractType.HYBRID)
        )
        hybrid_contracts = hybrid_result.scalar_one()

        # 導入成功統計
        onboarding_success_result = await db.execute(
            select(func.count(Contract.id))
            .filter(Contract.onboarding_success == True)
        )
        onboarding_success_count = onboarding_success_result.scalar_one()

        # 導入成功率
        onboarding_success_rate = (
            (onboarding_success_count / total_contracts * 100)
            if total_contracts > 0
            else 0.0
        )

        # 平均物件數
        avg_property_result = await db.execute(
            select(func.avg(Contract.property_count))
            .filter(Contract.property_count.isnot(None))
        )
        avg_property_count = avg_property_result.scalar_one() or 0.0

        # 總月費金額
        total_monthly_result = await db.execute(
            select(func.sum(Contract.monthly_value))
            .filter(Contract.monthly_value.isnot(None))
        )
        total_monthly_value = total_monthly_result.scalar_one() or Decimal('0.00')

        # 按類型統計
        by_type_result = await db.execute(
            select(Contract.contract_type, func.count(Contract.id))
            .group_by(Contract.contract_type)
        )
        by_type = {row[0].value: row[1] for row in by_type_result.all()}

        # 按月份統計 (最近 12 個月)
        by_month_result = await db.execute(
            select(
                extract('year', Contract.contract_date).label('year'),
                extract('month', Contract.contract_date).label('month'),
                func.count(Contract.id)
            )
            .group_by('year', 'month')
            .order_by('year', 'month')
        )
        by_month = {
            f"{int(row[0])}-{int(row[1]):02d}": row[2]
            for row in by_month_result.all()
        }

        return ContractStatistics(
            total_contracts=total_contracts,
            package_rental_contracts=package_rental_contracts,
            property_mgmt_contracts=property_mgmt_contracts,
            sublease_contracts=sublease_contracts,
            hybrid_contracts=hybrid_contracts,
            onboarding_success_count=onboarding_success_count,
            onboarding_success_rate=round(onboarding_success_rate, 2),
            avg_property_count=round(float(avg_property_count), 2),
            total_monthly_value=total_monthly_value,
            by_type=by_type,
            by_month=by_month
        )

    @staticmethod
    async def get_kpi_progress_list(db: AsyncSession) -> list[ContractKPIProgress]:
        """取得所有簽約的 KPI 進度"""
        result = await db.execute(
            select(Contract)
            .options(selectinload(Contract.customer))
            .order_by(Contract.contract_date.desc())
        )
        contracts = result.scalars().all()

        kpi_progress_list = []
        for contract in contracts:
            # 計算 KPI 完成率 (6 個 KPI 指標)
            kpi_count = 6
            completed_count = sum([
                1 if contract.kpi_property_upload_rate and contract.kpi_property_upload_rate >= 80 else 0,
                1 if contract.kpi_contract_creation_rate and contract.kpi_contract_creation_rate >= 80 else 0,
                1 if contract.kpi_billing_active else 0,
                1 if contract.kpi_payment_integrated else 0,
                1 if contract.kpi_notification_setup else 0,
                1 if contract.kpi_sop_established else 0,
            ])
            kpi_completion_rate = (completed_count / kpi_count * 100) if kpi_count > 0 else 0.0

            kpi_progress = ContractKPIProgress(
                contract_id=contract.id,
                customer_name=contract.customer.company_name if contract.customer else "Unknown",
                contract_date=contract.contract_date,
                kpi_property_upload_rate=contract.kpi_property_upload_rate,
                kpi_contract_creation_rate=contract.kpi_contract_creation_rate,
                kpi_billing_active=contract.kpi_billing_active,
                kpi_payment_integrated=contract.kpi_payment_integrated,
                kpi_notification_setup=contract.kpi_notification_setup,
                kpi_sop_established=contract.kpi_sop_established,
                kpi_completion_rate=round(kpi_completion_rate, 2),
                onboarding_success=contract.onboarding_success
            )
            kpi_progress_list.append(kpi_progress)

        return kpi_progress_list

    @staticmethod
    async def get_by_customer(
        db: AsyncSession,
        customer_id: str,
        contract_type: Optional[ContractType] = None
    ) -> list[Contract]:
        """取得特定客戶的簽約記錄"""
        query = select(Contract).filter(Contract.customer_id == customer_id)

        if contract_type:
            query = query.filter(Contract.contract_type == contract_type)

        query = query.order_by(Contract.contract_date.desc())

        result = await db.execute(query)
        return list(result.scalars().all())


# 建立全域實例
contract_crud = ContractCRUD()
