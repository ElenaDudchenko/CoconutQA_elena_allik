from playwright.sync_api import Page

from pages.base_page import BasePage

class CinescopeMoviePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f'{self.home_url}movies/'

        self.review_input = '[data-qa-id="movie_review_input"]'
        self.rating_select = '[data-qa-id="movie_rating_select"]'
        self.submit_button = '[data-qa-id="movie_review_submit_button"]'


    def open(self, movie_id):
        self.open_url(f'{self.url}{movie_id}')

    def select_rating(self, rating):
        self.click(self.rating_select)
        self.page.get_by_role("option", name=str(rating)).click()

    def submit_review(self, review_text, rating):
        self.enter_text(self.review_input, review_text)
        self.select_rating(rating)
        self.click(self.submit_button)
