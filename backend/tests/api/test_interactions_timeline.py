"""
測試互動記錄時間軸查詢功能（任務 3.4）
"""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Customer, Interaction, InteractionType


@pytest.mark.asyncio
class TestInteractionTimeline:
    """測試互動記錄時間軸查詢"""

    async def test_list_interactions_time_descending_order(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession
    ):
        """測試互動記錄按時間倒序排列（最新在前）"""
        # 建立測試客戶
        customer = Customer(
            id="test-customer-timeline-1",
            company_name="測試公司",
            contact_name="測試聯絡人",
            contact_phone="0912345678"
        )
        db_session.add(customer)
        await db_session.commit()

        # 建立 3 筆互動記錄，時間不同
        now = datetime.utcnow()
        interactions_data = [
            {
                "id": "interaction-1",
                "title": "最舊的記錄",
                "created_at": now - timedelta(hours=2)
            },
            {
                "id": "interaction-2",
                "title": "中間的記錄",
                "created_at": now - timedelta(hours=1)
            },
            {
                "id": "interaction-3",
                "title": "最新的記錄",
                "created_at": now
            }
        ]

        for data in interactions_data:
            interaction = Interaction(
                id=data["id"],
                customer_id=customer.id,
                interaction_type=InteractionType.STATUS_CHANGE,
                title=data["title"]
            )
            # 手動設置 created_at（繞過 server_default）
            db_session.add(interaction)
            await db_session.flush()
            await db_session.execute(
                f"UPDATE interactions SET created_at = '{data['created_at'].isoformat()}' WHERE id = '{data['id']}'"
            )

        await db_session.commit()

        # 查詢互動記錄
        response = await async_client.get(
            f"/api/v1/interactions?customer_id={customer.id}"
        )

        assert response.status_code == 200
        data = response.json()

        # 驗證結果
        assert data["total"] == 3
        assert len(data["interactions"]) == 3

        # 驗證按時間倒序排列（最新在前）
        assert data["interactions"][0]["title"] == "最新的記錄"
        assert data["interactions"][1]["title"] == "中間的記錄"
        assert data["interactions"][2]["title"] == "最舊的記錄"

    async def test_list_interactions_all_types(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession
    ):
        """測試回傳包含所有互動類型"""
        # 建立測試客戶
        customer = Customer(
            id="test-customer-timeline-2",
            company_name="測試公司2",
            contact_name="測試聯絡人2",
            contact_phone="0912345679"
        )
        db_session.add(customer)
        await db_session.commit()

        # 建立三種類型的互動記錄
        interaction_types = [
            (InteractionType.DOCUMENT, "文檔記錄"),
            (InteractionType.AUDIO, "音訊記錄"),
            (InteractionType.STATUS_CHANGE, "狀態變更")
        ]

        for idx, (itype, title) in enumerate(interaction_types):
            interaction = Interaction(
                id=f"interaction-type-{idx}",
                customer_id=customer.id,
                interaction_type=itype,
                title=title
            )
            db_session.add(interaction)

        await db_session.commit()

        # 查詢所有互動記錄（不篩選類型）
        response = await async_client.get(
            f"/api/v1/interactions?customer_id={customer.id}"
        )

        assert response.status_code == 200
        data = response.json()

        # 驗證包含所有三種類型
        assert data["total"] == 3
        returned_types = {item["interaction_type"] for item in data["interactions"]}
        assert returned_types == {"document", "audio", "status_change"}

    async def test_list_interactions_type_filter(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession
    ):
        """測試類型篩選功能"""
        # 建立測試客戶
        customer = Customer(
            id="test-customer-timeline-3",
            company_name="測試公司3",
            contact_name="測試聯絡人3",
            contact_phone="0912345680"
        )
        db_session.add(customer)
        await db_session.commit()

        # 建立多種類型的記錄
        for idx in range(3):
            # 2 個 AUDIO
            db_session.add(Interaction(
                id=f"audio-{idx}",
                customer_id=customer.id,
                interaction_type=InteractionType.AUDIO,
                title=f"音訊 {idx}"
            ))

        # 1 個 DOCUMENT
        db_session.add(Interaction(
            id="doc-1",
            customer_id=customer.id,
            interaction_type=InteractionType.DOCUMENT,
            title="文檔"
        ))

        await db_session.commit()

        # 僅查詢 AUDIO 類型
        response = await async_client.get(
            f"/api/v1/interactions?customer_id={customer.id}&interaction_type=audio"
        )

        assert response.status_code == 200
        data = response.json()

        # 驗證僅返回 AUDIO 類型
        assert data["total"] == 3
        assert all(item["interaction_type"] == "audio" for item in data["interactions"])

    async def test_list_interactions_pagination_default_limit(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession
    ):
        """測試分頁預設 limit=20"""
        # 建立測試客戶
        customer = Customer(
            id="test-customer-timeline-4",
            company_name="測試公司4",
            contact_name="測試聯絡人4",
            contact_phone="0912345681"
        )
        db_session.add(customer)
        await db_session.commit()

        # 建立 25 筆記錄
        for idx in range(25):
            interaction = Interaction(
                id=f"interaction-page-{idx}",
                customer_id=customer.id,
                interaction_type=InteractionType.STATUS_CHANGE,
                title=f"記錄 {idx}"
            )
            db_session.add(interaction)

        await db_session.commit()

        # 查詢第一頁（不指定 limit）
        response = await async_client.get(
            f"/api/v1/interactions?customer_id={customer.id}"
        )

        assert response.status_code == 200
        data = response.json()

        # 驗證預設返回 20 筆
        assert data["total"] == 25
        assert len(data["interactions"]) == 20
        assert data["limit"] == 20
        assert data["page"] == 1

        # 查詢第二頁
        response = await async_client.get(
            f"/api/v1/interactions?customer_id={customer.id}&page=2"
        )

        assert response.status_code == 200
        data = response.json()

        # 第二頁應該有 5 筆
        assert len(data["interactions"]) == 5

    async def test_list_interactions_includes_file_path(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession
    ):
        """測試回傳包含檔案路徑（用於前端組合下載 URL）"""
        # 建立測試客戶
        customer = Customer(
            id="test-customer-timeline-5",
            company_name="測試公司5",
            contact_name="測試聯絡人5",
            contact_phone="0912345682"
        )
        db_session.add(customer)
        await db_session.commit()

        # 建立包含檔案的互動記錄
        interaction = Interaction(
            id="interaction-with-file",
            customer_id=customer.id,
            interaction_type=InteractionType.DOCUMENT,
            title="帶檔案的記錄",
            file_path="interactions/documents/test.pdf",
            file_name="test.pdf",
            file_size=1024000
        )
        db_session.add(interaction)
        await db_session.commit()

        # 查詢互動記錄
        response = await async_client.get(
            f"/api/v1/interactions?customer_id={customer.id}"
        )

        assert response.status_code == 200
        data = response.json()

        # 驗證包含檔案資訊
        assert len(data["interactions"]) == 1
        interaction_data = data["interactions"][0]
        assert interaction_data["file_path"] == "interactions/documents/test.pdf"
        assert interaction_data["file_name"] == "test.pdf"
        assert interaction_data["file_size"] == 1024000

    async def test_list_interactions_without_customer_filter(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession
    ):
        """測試不指定客戶 ID 時查詢所有互動記錄"""
        # 建立 2 個客戶，各有互動記錄
        for idx in range(2):
            customer = Customer(
                id=f"customer-all-{idx}",
                company_name=f"公司{idx}",
                contact_name=f"聯絡人{idx}",
                contact_phone=f"091234568{idx}"
            )
            db_session.add(customer)
            await db_session.flush()

            # 每個客戶 2 筆記錄
            for j in range(2):
                interaction = Interaction(
                    id=f"interaction-all-{idx}-{j}",
                    customer_id=customer.id,
                    interaction_type=InteractionType.STATUS_CHANGE,
                    title=f"客戶{idx}記錄{j}"
                )
                db_session.add(interaction)

        await db_session.commit()

        # 查詢所有互動記錄（不指定 customer_id）
        response = await async_client.get("/api/v1/interactions")

        assert response.status_code == 200
        data = response.json()

        # 應該返回所有客戶的互動記錄
        assert data["total"] >= 4  # 至少有我們剛建立的 4 筆
