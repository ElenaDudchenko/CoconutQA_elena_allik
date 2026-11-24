import allure
import pytest
from playwright.sync_api import expect

@allure.epic("Тестирование UI")
@allure.feature("Логин")
@pytest.mark.ui
class TestLogin:
    @allure.title("Успешный логин зарегистрированного пользователя")
    def test_login(self, login_page, page, common_user):
        email = common_user.email
        password = common_user.password
        login_page.login(email, password)
        expect(page).to_have_url("https://dev-cinescope.coconutqa.ru/")
        expect(page.get_by_text("Вы вошли в аккаунт")).to_be_visible()