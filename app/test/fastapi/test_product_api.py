import pytest
from app.infrastructure.fast_api import create_app
from fastapi.testclient import TestClient
from app.domain.entities.product import ProductEntity
from app.infrastructure.handlers import products
from app.infrastructure.schemas.product import ProductInput
from app.test import create_mock_product_repository, expected_products_catalog, expected_product_description


class TestUserApi:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app()
        self.client = TestClient(self.app)
        self.base_path = '/products'

    def test_get_product_catalog(self):
        with self.app.container.product_repository.override(create_mock_product_repository()):
            response = self.client.get(self.base_path + '/')
            assert expected_products_catalog == response.json()
            assert response.status_code == 200

    def test_get_product_detail(self):
        with self.app.container.product_repository.override(create_mock_product_repository()):
            response = self.client.get(self.base_path + '/mock_id')
            assert expected_product_description == response.json()
            assert response.status_code == 200

    def test_post_register_product(self):
        with self.app.container.product_repository.override(create_mock_product_repository()):
            response = self.client.post(
                self.base_path,
                json=expected_product_description
            )
            assert expected_product_description == response.json()
            assert response.status_code == 200

    def test_put_update_product(self):
        with self.app.container.product_repository.override(create_mock_product_repository()):
            response = self.client.put(
                self.base_path + '/mock_id',
                json=expected_product_description
            )
            assert expected_product_description == response.json()
            assert response.status_code == 200

    def test_register_product_uses_common_helper(self, monkeypatch):
        helper_result = ProductEntity('helper_id', 'from_helper', 'from_helper', 10.0, 1, 'from_helper')
        service_response = ProductEntity('service_id', 'service_name', 'service_description', 15.0, 3, 'service_image')
        helper_calls = []
        service_calls = []

        class FakeService:
            @staticmethod
            def register_product(product_entity):
                service_calls.append(product_entity)
                return service_response

        def fake_helper(product_input, product_factory, uid):
            helper_calls.append((product_input, product_factory, uid))
            return helper_result

        monkeypatch.setattr(products, '_product_entity_from_input', fake_helper)

        payload = ProductInput(
            name='name',
            description='description',
            price=10.0,
            stock=1,
            image='image'
        )
        response = products.register_product(
            product=payload,
            product_factory=object(),
            product_services=FakeService()
        )

        assert response == service_response.__dict__
        assert len(helper_calls) == 1
        helper_payload, _, helper_uid = helper_calls[0]
        assert helper_payload == payload
        assert helper_uid is None
        assert service_calls == [helper_result]

    def test_update_product_uses_common_helper(self, monkeypatch):
        helper_result = ProductEntity('helper_id', 'from_helper', 'from_helper', 10.0, 1, 'from_helper')
        service_response = ProductEntity('service_id', 'service_name', 'service_description', 15.0, 3, 'service_image')
        helper_calls = []
        service_calls = []

        class FakeService:
            @staticmethod
            def update_product(product_entity):
                service_calls.append(product_entity)
                return service_response

        def fake_helper(product_input, product_factory, uid):
            helper_calls.append((product_input, product_factory, uid))
            return helper_result

        monkeypatch.setattr(products, '_product_entity_from_input', fake_helper)

        payload = ProductInput(
            name='name',
            description='description',
            price=10.0,
            stock=1,
            image='image'
        )
        response = products.update_product(
            id='product-id',
            product=payload,
            product_factory=object(),
            product_services=FakeService()
        )

        assert response == service_response.__dict__
        assert len(helper_calls) == 1
        helper_payload, _, helper_uid = helper_calls[0]
        assert helper_payload == payload
        assert helper_uid == 'product-id'
        assert service_calls == [helper_result]
