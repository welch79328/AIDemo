"""
Interaction CRUD 測試
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.interaction import interaction_crud
from app.models.base import Interaction, Customer, InteractionType


class TestInteractionCRUD:
    """Interaction CRUD 測試"""

    @pytest_asyncio.fixture
    async def customer(self, db_session: AsyncSession):
        """創建測試客戶"""
        customer = Customer(
            company_name="測試公司",
            contact_person="測試聯絡人",
            contact_phone="0912345678"
        )
        db_session.add(customer)
        await db_session.commit()
        await db_session.refresh(customer)
        return customer

    @pytest.mark.asyncio
    async def test_create_interaction(self, db_session: AsyncSession, customer):
        """測試建立互動記錄"""
        interaction_data = {
            "customer_id": customer.id,
            "interaction_type": InteractionType.DOCUMENT,
            "title": "測試文檔",
            "file_path": "interactions/documents/test.pdf",
            "file_name": "test.pdf",
            "file_size": 1024,
            "notes": "測試備註"
        }

        interaction = await interaction_crud.create(
            db=db_session,
            **interaction_data
        )

        assert interaction.id is not None
        assert interaction.customer_id == customer.id
        assert interaction.interaction_type == InteractionType.DOCUMENT
        assert interaction.title == "測試文檔"
        assert interaction.file_path == "interactions/documents/test.pdf"
        assert interaction.notes == "測試備註"

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session: AsyncSession, customer):
        """測試根據 ID 查詢"""
        # 創建互動記錄
        interaction = await interaction_crud.create(
            db=db_session,
            customer_id=customer.id,
            interaction_type=InteractionType.AUDIO,
            title="測試錄音",
            file_path="interactions/audios/test.mp3"
        )

        # 查詢
        found = await interaction_crud.get_by_id(db=db_session, interaction_id=interaction.id)

        assert found is not None
        assert found.id == interaction.id
        assert found.title == "測試錄音"

    @pytest.mark.asyncio
    async def test_get_by_customer(self, db_session: AsyncSession, customer):
        """測試根據客戶查詢"""
        # 創建多筆互動記錄
        await interaction_crud.create(
            db=db_session,
            customer_id=customer.id,
            interaction_type=InteractionType.DOCUMENT,
            title="文檔1"
        )
        await interaction_crud.create(
            db=db_session,
            customer_id=customer.id,
            interaction_type=InteractionType.AUDIO,
            title="錄音1"
        )

        # 查詢
        interactions, total = await interaction_crud.get_by_customer(
            db=db_session,
            customer_id=customer.id,
            page=1,
            limit=10
        )

        assert total == 2
        assert len(interactions) == 2
        # 驗證按時間倒序排列
        assert interactions[0].title == "錄音1"
        assert interactions[1].title == "文檔1"

    @pytest.mark.asyncio
    async def test_get_by_customer_with_type_filter(self, db_session: AsyncSession, customer):
        """測試根據客戶與類型篩選"""
        # 創建不同類型的互動記錄
        await interaction_crud.create(
            db=db_session,
            customer_id=customer.id,
            interaction_type=InteractionType.DOCUMENT,
            title="文檔1"
        )
        await interaction_crud.create(
            db=db_session,
            customer_id=customer.id,
            interaction_type=InteractionType.AUDIO,
            title="錄音1"
        )

        # 僅查詢文檔類型
        interactions, total = await interaction_crud.get_by_customer(
            db=db_session,
            customer_id=customer.id,
            interaction_type=InteractionType.DOCUMENT,
            page=1,
            limit=10
        )

        assert total == 1
        assert len(interactions) == 1
        assert interactions[0].interaction_type == InteractionType.DOCUMENT

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, db_session: AsyncSession, customer):
        """測試分頁查詢所有互動記錄"""
        # 創建 5 筆記錄
        for i in range(5):
            await interaction_crud.create(
                db=db_session,
                customer_id=customer.id,
                interaction_type=InteractionType.DOCUMENT,
                title=f"文檔{i+1}"
            )

        # 第一頁（2筆）
        interactions, total = await interaction_crud.get_all(
            db=db_session,
            page=1,
            limit=2
        )

        assert total == 5
        assert len(interactions) == 2

        # 第二頁（2筆）
        interactions, total = await interaction_crud.get_all(
            db=db_session,
            page=2,
            limit=2
        )

        assert total == 5
        assert len(interactions) == 2

    @pytest.mark.asyncio
    async def test_update_interaction(self, db_session: AsyncSession, customer):
        """測試更新互動記錄"""
        # 創建互動記錄
        interaction = await interaction_crud.create(
            db=db_session,
            customer_id=customer.id,
            interaction_type=InteractionType.DOCUMENT,
            title="原始標題",
            notes="原始備註"
        )

        # 更新
        updated = await interaction_crud.update(
            db=db_session,
            interaction_id=interaction.id,
            title="更新後標題",
            notes="更新後備註"
        )

        assert updated.id == interaction.id
        assert updated.title == "更新後標題"
        assert updated.notes == "更新後備註"

    @pytest.mark.asyncio
    async def test_delete_interaction(self, db_session: AsyncSession, customer):
        """測試刪除互動記錄"""
        # 創建互動記錄
        interaction = await interaction_crud.create(
            db=db_session,
            customer_id=customer.id,
            interaction_type=InteractionType.DOCUMENT,
            title="待刪除"
        )

        # 刪除
        await interaction_crud.delete(db=db_session, interaction_id=interaction.id)

        # 驗證已刪除
        found = await interaction_crud.get_by_id(db=db_session, interaction_id=interaction.id)
        assert found is None
