from random import randint

import allure
import pytest
from playwright.sync_api import expect

@allure.epic("Тестирование UI")
@allure.feature("Регистрация")
@pytest.mark.ui
class TestRegistration:
    @allure.title("Успешная регистрация нового пользователя")
    def test_registration(self, register_page, page):
        email = f"aqatest{randint(1, 999999)}@email.qa"
        register_page.register("Иван Иванов", email, "qwerty123Q")
        expect(page.get_by_text("Подтвердите свою почту")).to_be_visible()