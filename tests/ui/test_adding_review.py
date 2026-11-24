import allure
import pytest
from playwright.sync_api import expect
from random import randint

@allure.epic("Тестирование UI")
@allure.feature("Добавление отзыва")
@pytest.mark.ui
class TestReview:
    @allure.title("Добавление отзыва к фильму")
    def test_submit_review(self, movie_page, page):
        review_text = f'Отличный фильм для просмотра! {randint(1, 999999)}'
        with allure.step('Отправка отзыва с оценкой'):
            movie_page.submit_review(review_text, 5)
        with allure.step('Проверка публикации отзыва'):
            expect(page.get_by_text('Отзыв успешно создан')).to_be_visible()
            expect(page.get_by_text(review_text )).to_be_visible()
            review_card = page.locator(".rounded-xl").filter(has_text=review_text)
            expect(review_card.locator('h3')).to_contain_text("5/5")
