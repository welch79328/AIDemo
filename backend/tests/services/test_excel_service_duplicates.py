"""
ExcelService 重複資料檢測測試
"""
import pytest
import pytest_asyncio
from app.services.excel_service import ExcelService
from app.models.base import Customer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


@pytest.fixture
def excel_service():
    """創建 ExcelService 實例"""
    return ExcelService()


@pytest_asyncio.fixture
async def sample_customers(db_session: AsyncSession):
    """建立測試用的客戶資料"""
    customers = [
        Customer(
            company_name="現有公司 A",
            contact_person="張三",
            contact_phone="0912345678",
            contact_email="existing1@example.com"
        ),
        Customer(
            company_name="現有公司 B",
            contact_person="李四",
            contact_phone="0987654321",
            contact_email="existing2@example.com"
        ),
        Customer(
            company_name="現有公司 C",
            contact_person="王五",
            contact_phone="02-12345678",
            contact_email="existing3@example.com"
        ),
    ]

    for customer in customers:
        db_session.add(customer)

    await db_session.commit()

    return customers


@pytest.mark.asyncio
async def test_detect_duplicates_by_phone(excel_service, db_session, sample_customers):
    """測試根據電話號碼檢測重複資料"""
    rows = [
        {
            "company_name": "新公司 A",
            "contact_person": "趙六",
            "contact_phone": "0912345678",  # 與現有客戶重複
            "contact_email": "new1@example.com"
        },
        {
            "company_name": "新公司 B",
            "contact_person": "孫七",
            "contact_phone": "0923456789",  # 不重複
            "contact_email": "new2@example.com"
        },
    ]

    duplicates = await excel_service.detect_duplicates(db_session, rows)

    # 應該檢測到 1 筆重複
    assert len(duplicates) == 1
    assert duplicates[0]["contact_phone"] == "0912345678"
    assert duplicates[0]["existing_customer_id"] is not None


@pytest.mark.asyncio
async def test_detect_duplicates_by_email(excel_service, db_session, sample_customers):
    """測試根據 Email 檢測重複資料"""
    rows = [
        {
            "company_name": "新公司 C",
            "contact_person": "周八",
            "contact_phone": "0934567890",
            "contact_email": "existing2@example.com"  # 與現有客戶重複
        },
        {
            "company_name": "新公司 D",
            "contact_person": "吳九",
            "contact_phone": "0945678901",
            "contact_email": "new3@example.com"  # 不重複
        },
    ]

    duplicates = await excel_service.detect_duplicates(db_session, rows)

    # 應該檢測到 1 筆重複
    assert len(duplicates) == 1
    assert duplicates[0]["contact_email"] == "existing2@example.com"
    assert duplicates[0]["existing_customer_id"] is not None


@pytest.mark.asyncio
async def test_detect_duplicates_multiple(excel_service, db_session, sample_customers):
    """測試檢測多筆重複資料"""
    rows = [
        {
            "company_name": "新公司 E",
            "contact_person": "鄭十",
            "contact_phone": "0912345678",  # 重複
            "contact_email": "new4@example.com"
        },
        {
            "company_name": "新公司 F",
            "contact_person": "錢十一",
            "contact_phone": "0956789012",
            "contact_email": "existing3@example.com"  # 重複
        },
        {
            "company_name": "新公司 G",
            "contact_person": "孫十二",
            "contact_phone": "0967890123",
            "contact_email": "new5@example.com"  # 不重複
        },
    ]

    duplicates = await excel_service.detect_duplicates(db_session, rows)

    # 應該檢測到 2 筆重複
    assert len(duplicates) == 2


@pytest.mark.asyncio
async def test_detect_duplicates_no_duplicates(excel_service, db_session, sample_customers):
    """測試沒有重複資料的情況"""
    rows = [
        {
            "company_name": "新公司 H",
            "contact_person": "李十三",
            "contact_phone": "0978901234",
            "contact_email": "new6@example.com"
        },
        {
            "company_name": "新公司 I",
            "contact_person": "周十四",
            "contact_phone": "0989012345",
            "contact_email": "new7@example.com"
        },
    ]

    duplicates = await excel_service.detect_duplicates(db_session, rows)

    # 應該沒有重複
    assert len(duplicates) == 0


@pytest.mark.asyncio
async def test_detect_duplicates_empty_email(excel_service, db_session, sample_customers):
    """測試 Email 為空的情況（不應視為重複）"""
    rows = [
        {
            "company_name": "新公司 J",
            "contact_person": "吳十五",
            "contact_phone": "0990123456",
            "contact_email": ""  # 空 Email
        },
        {
            "company_name": "新公司 K",
            "contact_person": "鄭十六",
            "contact_phone": "0991234567",
            "contact_email": ""  # 空 Email
        },
    ]

    duplicates = await excel_service.detect_duplicates(db_session, rows)

    # 空 Email 不應視為重複
    assert len(duplicates) == 0


@pytest.mark.asyncio
async def test_detect_duplicates_batch_performance(excel_service, db_session):
    """測試批次查詢效能（應避免 N+1 問題）"""
    import time

    # 建立 100 筆現有客戶
    for i in range(100):
        customer = Customer(
            company_name=f"公司 {i}",
            contact_person=f"聯絡人 {i}",
            contact_phone=f"091234{i:04d}",
            contact_email=f"test{i}@example.com"
        )
        db_session.add(customer)

    await db_session.commit()

    # 準備 1000 筆待檢測資料（部分重複）
    rows = []
    for i in range(1000):
        if i < 50:
            # 前 50 筆與現有客戶重複
            rows.append({
                "company_name": f"新公司 {i}",
                "contact_person": f"新聯絡人 {i}",
                "contact_phone": f"091234{i:04d}",
                "contact_email": f"new{i}@example.com"
            })
        else:
            # 後 950 筆不重複
            rows.append({
                "company_name": f"新公司 {i}",
                "contact_person": f"新聯絡人 {i}",
                "contact_phone": f"092345{i:04d}",
                "contact_email": f"new{i}@example.com"
            })

    # 測試效能
    start_time = time.time()
    duplicates = await excel_service.detect_duplicates(db_session, rows)
    end_time = time.time()

    elapsed_time = end_time - start_time

    # 應該檢測到 50 筆重複
    assert len(duplicates) == 50

    # 效能要求：1000 筆資料檢測時間 < 3 秒
    assert elapsed_time < 3.0, f"檢測時間 {elapsed_time:.2f} 秒超過 3 秒限制"


@pytest.mark.asyncio
async def test_detect_duplicates_return_format(excel_service, db_session, sample_customers):
    """測試回傳格式是否正確"""
    rows = [
        {
            "company_name": "新公司 L",
            "contact_person": "王十七",
            "contact_phone": "0912345678",  # 重複
            "contact_email": "new8@example.com"
        },
    ]

    duplicates = await excel_service.detect_duplicates(db_session, rows)

    # 驗證回傳格式
    assert len(duplicates) == 1

    duplicate = duplicates[0]
    assert "row_number" in duplicate
    assert "customer_name" in duplicate
    assert "contact_phone" in duplicate
    assert "contact_email" in duplicate
    assert "existing_customer_id" in duplicate

    # 驗證資料正確性
    assert duplicate["customer_name"] == "新公司 L"
    assert duplicate["contact_phone"] == "0912345678"
    assert duplicate["existing_customer_id"] is not None
