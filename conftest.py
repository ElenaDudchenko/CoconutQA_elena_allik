import os
from random import choice

import requests
import pytest

from clients.api_manager import ApiManager
from data.movies.movies_data import get_movie_payload
from utils.data_generator import DataGenerator

@pytest.fixture(scope="session")
def unauthenticated_api_manager(registered_user):
    session = requests.Session()
    yield ApiManager(session)
    session.close()

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

@pytest.fixture(scope="function")
def test_user():
    password = DataGenerator.generate_random_password()
    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": password,
        "passwordRepeat": password,
        "roles": ["USER"]
    }

@pytest.fixture(scope="function")
def movie_by_id(api_manager):
    response = api_manager.movie_api.get_movies()
    response_data = response.json()

    movies = response_data["movies"]
    assert movies, "Список фильмов пуст"

    movie = choice(movies)
    return movie["id"]


@pytest.fixture(scope="function")
def super_admin_api_manager():
    email = os.environ["SUPER_ADMIN_EMAIL"]
    password = os.environ["SUPER_ADMIN_PASSWORD"]

    with requests.Session() as session:
        admin_manager = ApiManager(session)
        admin_manager.auth_api.authenticate((email, password))
        yield admin_manager

@pytest.fixture(scope="function")
def created_movie_data(super_admin_api_manager, movie_data):
    response = super_admin_api_manager.movie_api.create_movie(movie_data).json()
    return response

@pytest.fixture(scope="function")
def movie_data_with_cleanup(super_admin_api_manager, created_movie_data):
    yield created_movie_data
    super_admin_api_manager.movie_api.delete_movie(created_movie_data['id'])


@pytest.fixture(scope="function")
def registered_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    test_user["id"] = response["id"]
    return test_user

@pytest.fixture(scope="function")
def authenticated_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    test_user["id"] = response["id"]
    email= test_user["email"]
    password = test_user["password"]
    api_manager.auth_api.authenticate((email, password))
    return test_user

@pytest.fixture(scope="function")
def movie_data(api_manager):
    genres = api_manager.movie_api.get_genres().json()

    assert genres, "Невозможно подготовить фильм: список жанров пуст"

    genre_id = genres[0]['id']

    return get_movie_payload(genre_id)