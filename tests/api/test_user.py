import pytest
from pydantic import ValidationError

from models.base_models import RegisterUserResponse, TestUser


@pytest.mark.regress
@pytest.mark.api
class TestUserAPI:

    @pytest.mark.smoke
    def test_create_user(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(creation_user_data)
        user = RegisterUserResponse.model_validate(response.json())

        assert user.email == creation_user_data.email
        assert user.fullName == creation_user_data.fullName
        assert user.roles == creation_user_data.roles
        assert user.verified is True
        assert user.id

    @pytest.mark.smoke
    def test_get_user_by_locator(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(creation_user_data)
        created_user_response = RegisterUserResponse.model_validate(response.json())
        response = super_admin.api.user_api.get_user(created_user_response.id)
        data = response.json()
        response_by_id = RegisterUserResponse.model_validate(data)
        response = super_admin.api.user_api.get_user(created_user_response.email)
        data = response.json()
        response_by_email = RegisterUserResponse.model_validate(data)

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"
        assert response_by_id.id == created_user_response.id
        assert response_by_id.email == creation_user_data.email
        assert response_by_id.fullName == creation_user_data.fullName
        assert response_by_id.roles == creation_user_data.roles
        assert response_by_id.verified is True

    @pytest.mark.slow
    def test_get_user_by_id_common_user(self, common_user):
        common_user.api.user_api.get_user(common_user.email, expected_status=403)

    def test_user_model_rejects_invalid_email(self):
        with pytest.raises(ValidationError):
            invalid_user = TestUser(
                email="не-почта",
                fullName = "Anna",
                password = "12345678",
                passwordRepeat = "12345678")



