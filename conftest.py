from random import choice
from uuid import uuid4

import requests
import pytest
from sqlalchemy.orm import Session
from playwright.sync_api import Page


from clients.api_manager import ApiManager
from constants.roles import Roles
from data.movies.movies_data import get_movie_payload
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper
from entities.user import User
from pages.login_page import CinescopeLoginPage
from pages.movie_page import CinescopeMoviePage
from resources.user_creds import SuperAdminCreds
from utils.data_generator import DataGenerator
from models.base_models import TestUser, RegisterUserResponse, RegisteredUserId
from utils.tools import Tools
from pages.register_page import CinescopeRegisterPage


@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(session)


@pytest.fixture(scope='function')
def api_manager_clean():
    with requests.Session() as session:
        clean_manager = ApiManager(session)
        yield clean_manager


@pytest.fixture
def test_user():
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER]
    )


@pytest.fixture(scope="function")
def movie_by_id(api_manager):
    response = api_manager.movie_api.get_movies()
    response_data = response.json()

    movies = response_data["movies"]
    assert movies, "Список фильмов пуст"

    movie = choice(movies)
    return movie["id"]


@pytest.fixture(scope="function")
def created_movie_data(super_admin, movie_data):
    response = super_admin.api.movie_api.create_movie(movie_data).json()
    return response


@pytest.fixture(scope="function")
def movie_data_with_cleanup(super_admin, created_movie_data):
    yield created_movie_data
    super_admin.api.movie_api.delete_movie(created_movie_data['id'])


@pytest.fixture(scope="function")
def registered_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    test_user["id"] = response["id"]
    return test_user


@pytest.fixture(scope="function")
def authenticated_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user)
    registered_user = RegisteredUserId.model_validate(response.json())
    test_user.id = registered_user.id

    api_manager.auth_api.authenticate((test_user.email, test_user.password))
    return test_user


@pytest.fixture(scope="function")
def movie_data(api_manager):
    genres = api_manager.movie_api.get_genres().json()

    assert genres, "Невозможно подготовить фильм: список жанров пуст"

    genre_id = genres[0]['id']

    return get_movie_payload(genre_id)


@pytest.fixture(scope="function")
def movie_data_with_prices(super_admin, min_price, max_price):
    genres = super_admin.api.movie_api.get_genres().json()

    assert genres, "Невозможно подготовить фильм: список жанров пуст"

    genre_id = genres[0]['id']

    ids = []
    prices = [
        min_price - 1,
        (min_price + max_price) // 2,
        max_price + 10,
    ]

    try:
        for price in prices:
            data = get_movie_payload(genre_id)
            data['price'] = price
            data["published"] = True
            movie = super_admin.api.movie_api.create_movie(data).json()
            ids.append(movie['id'])

        yield {
            "min_price": min_price,
            "max_price": max_price,
            "below_id": ids[0],
            "inside_id": ids[1],
            "above_id": ids[2],
        }

    finally:
        for movie_id in ids:
            super_admin.api.movie_api.delete_movie(movie_id)


@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session


    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin


@pytest.fixture(scope="function")
def creation_user_data(test_user):
    updated_data = test_user.model_copy(update={
        "verified": True,
        "banned": False
    })
    return updated_data


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER.value],
        new_session)

    response = super_admin.api.user_api.create_user(creation_user_data)
    user_id = response.json()["id"]

    try:
        common_user.api.auth_api.authenticate(common_user.creds)
        yield common_user
    finally:
        super_admin.api.user_api.delete_user(user_id)


@pytest.fixture
def admin_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    corrected_data = creation_user_data.model_copy(update=
    {"email": f"qa-admin-{uuid4().hex}@example.com",
        "roles": [Roles.ADMIN],})

    admin_user = User(
        corrected_data.email,
        corrected_data.password,
        [Roles.ADMIN.value],
        new_session)

    response = super_admin.api.user_api.create_user(corrected_data)
    admin_id = response.json()["id"]
    try:
        super_admin.api.user_api.patch_user(admin_id,
        {"roles": [Roles.ADMIN.value]},)
        admin_user.api.auth_api.authenticate(admin_user.creds)
        yield admin_user
    finally:
        super_admin.api.user_api.delete_user(admin_id)

@pytest.fixture(scope="module")
def db_session() -> Session:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    yield db_session
    db_session.close()

@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    """
    Фикстура для экземпляра хелпера
    """
    db_helper = DBHelper(db_session)
    return db_helper

@pytest.fixture(scope="function")
def created_test_user(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user
    # Cleanup после теста
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)

@pytest.fixture
def movie_cleanup(super_admin):
    movie_ids = []

    yield movie_ids

    for movie_id in movie_ids:
        super_admin.api.movie_api.delete_movie(movie_id)

DEFAULT_UI_TIMEOUT = 30000  # Пример значения таймаута

@pytest.fixture(scope="session")  # Браузер запускается один раз для всей сессии
def browser(playwright):
    browser = playwright.chromium.launch(headless=False,
    slow_mo=500,)  # headless=True для CI/CD, headless=False для локальной разработки
    yield browser  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    browser.close()  # Браузер закрывается после завершения всех тестов

@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    context.set_default_timeout(DEFAULT_UI_TIMEOUT)
    yield context
    log_name = f"trace_{Tools.get_timestamp()}.zip"
    trace_path = Tools.files_dir('playwright_trace', log_name)
    context.tracing.stop(path=trace_path)
    context.close()

@pytest.fixture(scope="function")  # Страница создается для каждого теста
def page(context):
    page = context.new_page()
    yield page  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    page.close()  # Страница закрывается после завершения теста

@pytest.fixture
def register_page(page: Page) -> CinescopeRegisterPage:
    register_page = CinescopeRegisterPage(page)
    register_page.open()
    return register_page

@pytest.fixture
def login_page(page: Page) -> CinescopeLoginPage:
    login_page = CinescopeLoginPage(page)
    login_page.open()
    return login_page

@pytest.fixture
def movie_page(page: Page, common_user, login_page, movie_data_with_cleanup):
    movie_page = CinescopeMoviePage(page)
    login_page.login(common_user.email, common_user.password)
    movie_id = movie_data_with_cleanup['id']
    movie_page.open(movie_id)
    return movie_page