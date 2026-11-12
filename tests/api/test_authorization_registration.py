import requests
import pytest

from models.base_models import RegisterUserResponse


@pytest.mark.regress
@pytest.mark.api
class TestAuth:
    @pytest.mark.smoke
    def test_register_user(self, api_manager, test_user):
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        assert response_data["email"] == test_user["email"]
        assert "id" in response_data
        assert "USER" in response_data["roles"]

    @pytest.mark.smoke
    def test_register_and_login_user(self, api_manager, registered_user):
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        assert "accessToken" in response_data
        assert response_data["user"]["email"] == registered_user["email"]

    def test_register_timeout(self, api_manager, test_user):
        with pytest.raises(requests.exceptions.ConnectTimeout):
            api_manager.auth_api.register_user(test_user, timeout=0.001)

    @pytest.mark.smoke
    def test_get_user_info(self, super_admin,authenticated_user):
        user_id = authenticated_user.id
        response = RegisterUserResponse.model_validate(super_admin.api.user_api.get_user(user_id,
            expected_status=200).json())
        assert authenticated_user.id == response.id
        assert authenticated_user.email == response.email

    @pytest.mark.smoke
    def test_logout_user(self, api_manager, authenticated_user):
        api_manager.auth_api.logout_user()

    @pytest.mark.slow
    def test_delete_user(self, super_admin, authenticated_user):
        user_id = authenticated_user['id']

        super_admin.api.user_api.delete_user(user_id)

        response = super_admin.api.user_api.get_user(user_id, expected_status=200).json()

