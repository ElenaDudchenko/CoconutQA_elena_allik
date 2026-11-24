from playwright.sync_api import Page

from pages.base_page import BasePage

class CinescopeLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f'{self.home_url}login'

        self.email_input = '[data-qa-id="login_email_input"]'
        self.password_input = '[data-qa-id="login_password_input"]'
        self.submit_button = '[data-qa-id="login_submit_button"]'

    def open(self):
        self.page.goto(self.url)

    def login(self, email: str, password: str):
        self.page.fill(self.email_input, email)
        self.page.fill(self.password_input, password)
        self.page.click(self.submit_button)