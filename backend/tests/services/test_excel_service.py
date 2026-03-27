"""
ExcelService 測試
"""
import pytest
from pathlib import Path
from openpyxl import Workbook
from app.services.excel_service import ExcelService
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def excel_service():
    """創建 ExcelService 實例"""
    return ExcelService()


@pytest.fixture
def sample_excel_file(tmp_path):
    """創建測試用的 Excel 檔案"""
    file_path = tmp_path / "test_leads.xlsx"

    # 創建工作簿
    wb = Workbook()
    ws = wb.active

    # 標題列
    ws.append([
        "公司名稱",
        "聯絡人",
        "聯絡電話",
        "Email",
        "地址",
        "廣告來源"
    ])

    # 有效資料
    ws.append([
        "測試公司 A",
        "張三",
        "0912345678",
        "test@example.com",
        "台北市信義區",
        "3特點輪播廣告"
    ])

    ws.append([
        "測試公司 B",
        "李四",
        "02-12345678",
        "test2@example.com",
        "新北市板橋區",
        "3特點輪播廣告"
    ])

    # 缺少必填欄位的資料
    ws.append([
        "測試公司 C",
        "",  # 缺少聯絡人
        "0923456789",
        "test3@example.com",
        "台中市西屯區",
        "3特點輪播廣告"
    ])

    # 電話格式錯誤
    ws.append([
        "測試公司 D",
        "王五",
        "12345",  # 錯誤的電話格式
        "test4@example.com",
        "高雄市前鎮區",
        "3特點輪播廣告"
    ])

    # Email 格式錯誤
    ws.append([
        "測試公司 E",
        "趙六",
        "0934567890",
        "invalid-email",  # 錯誤的 Email 格式
        "台南市中西區",
        "3特點輪播廣告"
    ])

    wb.save(file_path)
    return file_path


@pytest.mark.asyncio
async def test_parse_lead_import_file_success(excel_service, sample_excel_file):
    """測試成功解析 Excel 檔案"""
    valid_rows, error_rows = await excel_service.parse_lead_import_file(sample_excel_file)

    # 應該有 2 筆有效資料
    assert len(valid_rows) == 2

    # 驗證第一筆資料
    assert valid_rows[0]["company_name"] == "測試公司 A"
    assert valid_rows[0]["contact_person"] == "張三"
    assert valid_rows[0]["contact_phone"] == "0912345678"
    assert valid_rows[0]["contact_email"] == "test@example.com"
    assert valid_rows[0]["address"] == "台北市信義區"
    assert valid_rows[0]["ad_source"] == "3特點輪播廣告"

    # 驗證第二筆資料
    assert valid_rows[1]["company_name"] == "測試公司 B"
    assert valid_rows[1]["contact_phone"] == "02-12345678"


@pytest.mark.asyncio
async def test_parse_lead_import_file_errors(excel_service, sample_excel_file):
    """測試檔案解析時的錯誤處理"""
    valid_rows, error_rows = await excel_service.parse_lead_import_file(sample_excel_file)

    # 應該有 3 筆錯誤資料
    assert len(error_rows) == 3

    # 驗證錯誤記錄包含必要資訊
    for error in error_rows:
        assert "row_number" in error
        assert "error_type" in error
        assert "error_message" in error
        assert "row_data" in error


@pytest.mark.asyncio
async def test_parse_lead_import_file_missing_contact_name(excel_service, sample_excel_file):
    """測試缺少聯絡人的錯誤"""
    valid_rows, error_rows = await excel_service.parse_lead_import_file(sample_excel_file)

    # 找出缺少聯絡人的錯誤
    missing_name_errors = [
        e for e in error_rows
        if e["error_type"] == "missing_required_field" and "contact_person" in e["error_message"]
    ]

    assert len(missing_name_errors) >= 1


@pytest.mark.asyncio
async def test_parse_lead_import_file_invalid_phone(excel_service, sample_excel_file):
    """測試電話格式錯誤"""
    valid_rows, error_rows = await excel_service.parse_lead_import_file(sample_excel_file)

    # 找出電話格式錯誤
    phone_errors = [
        e for e in error_rows
        if e["error_type"] == "invalid_phone_format"
    ]

    assert len(phone_errors) >= 1


@pytest.mark.asyncio
async def test_parse_lead_import_file_invalid_email(excel_service, sample_excel_file):
    """測試 Email 格式錯誤"""
    valid_rows, error_rows = await excel_service.parse_lead_import_file(sample_excel_file)

    # 找出 Email 格式錯誤
    email_errors = [
        e for e in error_rows
        if e["error_type"] == "invalid_email_format"
    ]

    assert len(email_errors) >= 1


@pytest.mark.asyncio
async def test_parse_lead_import_file_large_file(excel_service, tmp_path):
    """測試處理大型檔案（1000+ 筆資料）"""
    file_path = tmp_path / "large_test.xlsx"

    wb = Workbook()
    ws = wb.active

    # 標題列
    ws.append(["公司名稱", "聯絡人", "聯絡電話", "Email", "地址", "廣告來源"])

    # 生成 1000 筆資料
    for i in range(1000):
        ws.append([
            f"測試公司 {i}",
            f"聯絡人 {i}",
            f"091234{i:04d}",
            f"test{i}@example.com",
            f"台北市信義區 {i} 號",
            "3特點輪播廣告"
        ])

    wb.save(file_path)

    valid_rows, error_rows = await excel_service.parse_lead_import_file(file_path)

    # 應該成功處理 1000 筆資料
    assert len(valid_rows) == 1000
    assert len(error_rows) == 0


@pytest.mark.asyncio
async def test_validate_phone_format(excel_service):
    """測試電話格式驗證"""
    # 有效的手機號碼
    assert excel_service._validate_phone("0912345678") == True
    assert excel_service._validate_phone("0987654321") == True

    # 有效的市話號碼
    assert excel_service._validate_phone("02-12345678") == True
    assert excel_service._validate_phone("04-23456789") == True

    # 無效的電話號碼
    assert excel_service._validate_phone("12345") == False
    assert excel_service._validate_phone("abc") == False
    assert excel_service._validate_phone("") == False


@pytest.mark.asyncio
async def test_validate_email_format(excel_service):
    """測試 Email 格式驗證"""
    # 有效的 Email
    assert excel_service._validate_email("test@example.com") == True
    assert excel_service._validate_email("user.name@company.co.uk") == True

    # 無效的 Email
    assert excel_service._validate_email("invalid-email") == False
    assert excel_service._validate_email("@example.com") == False
    assert excel_service._validate_email("test@") == False
    assert excel_service._validate_email("") == False
