"""
Dashboard API - 儀表板統計端點
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract

from app.core.database import get_db
from app.models.base import Customer, Visit, Contract, CustomerStatus, CustomerStage, VisitType, VisitStatus

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/statistics")
async def get_dashboard_statistics(db: AsyncSession = Depends(get_db)):
    """取得儀表板統計數據"""
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # --- 客戶統計 ---
    total_customers = (await db.execute(
        select(func.count()).select_from(Customer)
    )).scalar() or 0

    aa_customers = (await db.execute(
        select(func.count()).select_from(Customer).where(Customer.is_aa_customer == True)
    )).scalar() or 0

    new_customers_this_month = (await db.execute(
        select(func.count()).select_from(Customer).where(Customer.created_at >= month_start)
    )).scalar() or 0

    # --- 簽約統計 ---
    total_contracts = (await db.execute(
        select(func.count()).select_from(Contract)
    )).scalar() or 0

    contracts_this_month = (await db.execute(
        select(func.count()).select_from(Contract).where(Contract.created_at >= month_start)
    )).scalar() or 0

    conversion_rate = round(total_contracts / total_customers * 100, 1) if total_customers > 0 else 0

    # --- 拜訪統計 ---
    total_visits = (await db.execute(
        select(func.count()).select_from(Visit)
    )).scalar() or 0

    visits_this_month = (await db.execute(
        select(func.count()).select_from(Visit).where(Visit.visit_date >= month_start)
    )).scalar() or 0

    pending_first_visit = (await db.execute(
        select(func.count()).select_from(Visit).where(
            Visit.visit_type == VisitType.FIRST_VISIT,
            Visit.visit_status == VisitStatus.SCHEDULED
        )
    )).scalar() or 0

    pending_second_visit = (await db.execute(
        select(func.count()).select_from(Visit).where(
            Visit.visit_type == VisitType.SECOND_VISIT,
            Visit.visit_status == VisitStatus.SCHEDULED
        )
    )).scalar() or 0

    # --- 客戶狀態統計 ---
    status_result = await db.execute(
        select(Customer.current_status, func.count(Customer.id))
        .group_by(Customer.current_status)
    )
    status_map = {row[0].value: row[1] for row in status_result}

    customers_by_status = {
        "contacted": status_map.get("contacted", 0),
        "first_visit_scheduled": status_map.get("first_visit_scheduled", 0),
        "first_visit_done": status_map.get("first_visit_done", 0),
        "second_visit_scheduled": status_map.get("second_visit_scheduled", 0),
        "second_visit_done": status_map.get("second_visit_done", 0),
        "negotiating": status_map.get("negotiating", 0),
        "signed": status_map.get("signed", 0),
        "lost": status_map.get("lost", 0),
    }

    # --- 客戶階段統計 ---
    stage_result = await db.execute(
        select(Customer.customer_stage, func.count(Customer.id))
        .group_by(Customer.customer_stage)
    )
    stage_map = {(row[0].value if row[0] else "unknown"): row[1] for row in stage_result}

    customers_by_stage = {
        "individual": stage_map.get("individual", 0),
        "preparing_company": stage_map.get("preparing_company", 0),
        "new_company": stage_map.get("new_company", 0),
        "scaling_up": stage_map.get("scaling_up", 0),
    }

    # --- 月趨勢（最近 6 個月）---
    monthly_trends = []
    for i in range(5, -1, -1):
        target = now - timedelta(days=i * 30)
        m_start = target.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if m_start.month == 12:
            m_end = m_start.replace(year=m_start.year + 1, month=1)
        else:
            m_end = m_start.replace(month=m_start.month + 1)

        new_c = (await db.execute(
            select(func.count()).select_from(Customer)
            .where(Customer.created_at >= m_start, Customer.created_at < m_end)
        )).scalar() or 0

        new_ct = (await db.execute(
            select(func.count()).select_from(Contract)
            .where(Contract.created_at >= m_start, Contract.created_at < m_end)
        )).scalar() or 0

        v = (await db.execute(
            select(func.count()).select_from(Visit)
            .where(Visit.visit_date >= m_start, Visit.visit_date < m_end)
        )).scalar() or 0

        monthly_trends.append({
            "month": m_start.strftime("%Y-%m"),
            "new_customers": new_c,
            "new_contracts": new_ct,
            "visits": v,
        })

    return {
        "total_customers": total_customers,
        "aa_customers": aa_customers,
        "new_customers_this_month": new_customers_this_month,
        "total_contracts": total_contracts,
        "contracts_this_month": contracts_this_month,
        "conversion_rate": conversion_rate,
        "total_visits": total_visits,
        "visits_this_month": visits_this_month,
        "pending_first_visit": pending_first_visit,
        "pending_second_visit": pending_second_visit,
        "customers_by_status": customers_by_status,
        "customers_by_stage": customers_by_stage,
        "monthly_trends": monthly_trends,
    }


@router.get("/recent-customers")
async def get_recent_customers(limit: int = 5, db: AsyncSession = Depends(get_db)):
    """取得最近新增的客戶"""
    result = await db.execute(
        select(Customer)
        .order_by(Customer.created_at.desc())
        .limit(limit)
    )
    customers = result.scalars().all()

    return [
        {
            "id": str(c.id),
            "company_name": c.company_name or "",
            "contact_person": c.contact_person or "",
            "contact_phone": c.contact_phone or "",
            "customer_stage": c.customer_stage.value if c.customer_stage else "",
            "current_status": c.current_status.value if c.current_status else "",
            "is_aa_customer": c.is_aa_customer or False,
            "created_at": c.created_at.isoformat() if c.created_at else "",
        }
        for c in customers
    ]


@router.get("/todos")
async def get_todo_list(completed: bool = False, db: AsyncSession = Depends(get_db)):
    """取得待辦事項（基於排程中的拜訪）"""
    query = select(Visit).where(Visit.visit_status == VisitStatus.SCHEDULED)
    if completed:
        query = select(Visit).where(Visit.visit_status == VisitStatus.COMPLETED)

    query = query.order_by(Visit.visit_date.asc()).limit(20)
    result = await db.execute(query)
    visits = result.scalars().all()

    todos = []
    for v in visits:
        # 取得客戶名稱
        cust_result = await db.execute(select(Customer).where(Customer.id == v.customer_id))
        customer = cust_result.scalar_one_or_none()
        customer_name = customer.company_name if customer else "未知客戶"

        visit_type_label = "一訪" if v.visit_type == VisitType.FIRST_VISIT else "二訪"
        todos.append({
            "id": str(v.id),
            "type": "visit",
            "customer_id": str(v.customer_id),
            "customer_name": customer_name,
            "title": f"{visit_type_label} - {customer_name}",
            "description": v.notes or "",
            "due_date": v.visit_date.isoformat() if v.visit_date else "",
            "priority": "high" if v.visit_type == VisitType.SECOND_VISIT else "medium",
            "completed": v.visit_status == VisitStatus.COMPLETED,
        })

    return todos


@router.get("/follow-ups")
async def get_follow_up_customers(days: int = 7, db: AsyncSession = Depends(get_db)):
    """取得需要跟進的客戶（超過 N 天未聯繫）"""
    cutoff = datetime.now() - timedelta(days=days)

    # 找出有拜訪記錄但最後拜訪超過 N 天的客戶
    subquery = (
        select(Visit.customer_id, func.max(Visit.visit_date).label("last_visit"))
        .group_by(Visit.customer_id)
        .subquery()
    )

    result = await db.execute(
        select(Customer, subquery.c.last_visit)
        .outerjoin(subquery, Customer.id == subquery.c.customer_id)
        .where(
            (subquery.c.last_visit < cutoff) | (subquery.c.last_visit.is_(None))
        )
        .where(Customer.current_status.notin_(["signed", "lost"]))
        .order_by(subquery.c.last_visit.asc().nullsfirst())
        .limit(20)
    )
    rows = result.all()

    return [
        {
            "id": str(row[0].id),
            "company_name": row[0].company_name or "",
            "contact_person": row[0].contact_person or "",
            "last_contact_date": row[1].isoformat() if row[1] else "",
            "days_since_contact": (datetime.now() - row[1]).days if row[1] else 999,
            "current_status": row[0].current_status.value if row[0].current_status else "",
            "next_action": "",
        }
        for row in rows
    ]


@router.put("/todos/{todo_id}/complete")
async def complete_todo(todo_id: str, db: AsyncSession = Depends(get_db)):
    """標記待辦事項（拜訪）為完成"""
    result = await db.execute(select(Visit).where(Visit.id == todo_id))
    visit = result.scalar_one_or_none()
    if not visit:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="待辦事項不存在")

    visit.visit_status = VisitStatus.COMPLETED
    await db.commit()
    return {"message": "已標記為完成"}
