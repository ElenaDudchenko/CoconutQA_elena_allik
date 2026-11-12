import allure
import pytest
from pydantic import TypeAdapter

from utils.data_generator import DataGenerator
from models.base_models import MoviesPage, Movie, Genre, GenreResponse


@pytest.mark.api
@pytest.mark.regress
@allure.epic('Cinescope')
@allure.feature('movie_api')
class TestMovies:
    @pytest.mark.smoke
    @allure.title('Тест получения всех фильмов через GET')
    def test_get_movies(self, api_manager_clean):
        with allure.step('Получение списка фильмов'):
            response = api_manager_clean.movie_api.get_movies()
        with allure.step("Валидация структуры ответа"):
            movies_page = MoviesPage.model_validate(response.json())
        with allure.step('Проверка, что список не пустой'):
            assert movies_page.movies

    @pytest.mark.smoke
    @allure.title('Тест получения фильма по id')
    def test_get_movie_by_id(self, api_manager_clean, movie_data_with_cleanup):
        with allure.step('Получение ID созданного фильма'):
            movie_id = movie_data_with_cleanup['id']

        with allure.step(f'Получение фильма по ID {movie_id}'):
            response = api_manager_clean.movie_api.get_movie_by_id(movie_id)

        with allure.step('Валидация структуры ответа'):
            response_movie = Movie.model_validate(response.json())

        with allure.step('Проверка соответствия данных фильма исходным данным'):
            assert response_movie.id == movie_id
            assert response_movie.description == movie_data_with_cleanup['description']
            assert response_movie.name == movie_data_with_cleanup['name']
            assert response_movie.genre == Genre.model_validate(movie_data_with_cleanup['genre'])


    @pytest.mark.slow
    @pytest.mark.parametrize("min_price, max_price", [(400, 402), (100, 102), ])
    @allure.title('Тест получения фильма по цене')
    def test_get_movies_by_price(self, api_manager_clean, movie_data_with_prices, min_price, max_price):
        with allure.step(f'Получение фильмов с фильтром по цене от {min_price} до {max_price}'):
            response = api_manager_clean.movie_api.get_movies(
                params={
                    "minPrice": min_price,
                    "maxPrice": max_price
                }
            )

        with allure.step('Валидация структуры ответа с фильмами'):
            movie_page = MoviesPage.model_validate(response.json())

        with allure.step('Получение фильмов со всех страниц ответа'):
            movies = movie_page.movies
            page_count = movie_page.pageCount
            for page in range(2, page_count + 1):
                response = api_manager_clean.movie_api.get_movies(
                    params={
                        "minPrice": min_price,
                        "maxPrice": max_price,
                        "page": page
                    }
                )
                page_data = MoviesPage.model_validate(response.json())
                movies.extend(page_data.movies)

        with allure.step('Создание списка для ID фильмов, соответствующих фильтру'):
            returned_ids = []

        with allure.step('Проверка непустого списка и соответствия цен заданному диапазону'):
            assert movies
            for movie in movies:
                assert min_price <= movie.price <= max_price
                returned_ids.append(movie.id)

        with allure.step('Проверка присутствия и отсутствия тестовых фильмов в результатах фильтрации'):
            assert movie_data_with_prices["inside_id"] in returned_ids
            assert movie_data_with_prices["above_id"] not in returned_ids
            assert movie_data_with_prices["below_id"] not in returned_ids


    @pytest.mark.parametrize("location", ["MSK", "SPB"])
    @allure.title('Тест получения фильма по местоположению')
    def test_get_movies_by_location(self, api_manager_clean, location):
        with allure.step(f'Получение фильмов с фильтром по местоположению {location}'):
            response = api_manager_clean.movie_api.get_movies(
                params={
                    "locations": [location],
                }
            )

        with allure.step('Валидация структуры ответа'):
            movie_page = MoviesPage.model_validate(response.json())

        with allure.step('Получение списка фильмов'):
            movies = movie_page.movies

        with allure.step(f'Проверка непустого списка и местоположения {location} у всех фильмов'):
            assert movies
            for movie in movies:
                assert movie.location == location


    @pytest.mark.parametrize("genre_index", [0, 5])
    @allure.title('Тест получения фильма по жанру')
    def test_get_movies_by_genre(self, api_manager_clean, genre_index):
        with allure.step('Получение списка доступных жанров'):
            genres = api_manager_clean.movie_api.get_genres().json()

        with allure.step(f'Получение ID жанра по индексу {genre_index}'):
            genre_id = genres[genre_index]["id"]

        with allure.step(f'Получение фильмов с фильтром по жанру ID {genre_id}'):
            response = api_manager_clean.movie_api.get_movies(
                params={
                    "genreId": genre_id
                }
            )

        with allure.step('Валидация структуры ответа'):
            movie_page = MoviesPage.model_validate(response.json())

        with allure.step('Получение списка фильмов'):
            movies = movie_page.movies

        with allure.step(f'Проверка непустого списка и соответствия жанра ID {genre_id}'):
            assert movies
            for movie in movies:
                assert movie.genreId == genre_id


    @pytest.mark.smoke
    @allure.title('Тест создания фильма через POST')
    def test_create_movie(self, super_admin, movie_data):
        with allure.step('Создание фильма через POST /movies'):
            response = super_admin.api.movie_api.create_movie(movie_data)

        with allure.step('Получение данных ответа'):
            response_data = response.json()

        try:
            with allure.step('Валидация структуры созданного фильма'):
                created_movie = Movie.model_validate(response_data)

            with allure.step('Проверка наличия ID и соответствия названия фильма'):
                assert created_movie.id
                assert created_movie.name == movie_data['name']
        finally:
            with allure.step('Удаление созданного фильма после теста'):
                if 'id' in response_data:
                    super_admin.api.movie_api.delete_movie(response_data['id'])


    @allure.title('Тест создания фильма без имени')
    def test_create_movie_without_name(self, super_admin, movie_data):
        with allure.step('Подготовка данных фильма без обязательного поля name'):
            movie_data_copy = movie_data.copy()
            del movie_data_copy['name']

        with allure.step('Отправка запроса на создание фильма без имени, ожидание 400'):
            response = super_admin.api.movie_api.create_movie(movie_data_copy, expected_status=400)

        with allure.step('Получение данных ответа'):
            response_data = response.json()

        with allure.step('Проверка типа ошибки Bad Request и сообщения валидации'):
            assert response_data['error'] == 'Bad Request'
            assert "Поле name должно быть строкой" in response_data['message']


    @allure.title('Тест создания фильма без авторизации')
    def test_create_movie_without_auth(self, api_manager_clean, movie_data):
        with allure.step('Попытка создания фильма без авторизации, ожидание 401'):
            response = api_manager_clean.movie_api.create_movie(movie_data, expected_status=401)

        with allure.step('Получение данных ответа'):
            response_data = response.json()

        with allure.step('Проверка сообщения об отсутствии авторизации'):
            assert response_data['message'] == 'Unauthorized'


    @pytest.mark.slow
    @allure.title('Тест создания фильма без прав(user)')
    def test_create_movie_without_rights(self, common_user, movie_data):
        with allure.step('Попытка создания фильма пользователем без прав, ожидание 403'):
            response = common_user.api.movie_api.create_movie(movie_data, expected_status=403)

        with allure.step('Получение данных ответа'):
            response_data = response.json()

        with allure.step('Проверка ошибки Forbidden'):
            assert response_data['error'] == 'Forbidden'


    @pytest.mark.smoke
    @allure.title('Тест изменения фильма через PATCH')
    def test_patch_movie(self, super_admin, movie_data_with_cleanup):
        with allure.step('Подготовка ID фильма и нового названия'):
            movie_id = movie_data_with_cleanup['id']
            update_data = {'name': movie_data_with_cleanup['name'] + ' updated'}

        with allure.step(f'Изменение названия фильма ID {movie_id} через PATCH'):
            response = Movie.model_validate(
                super_admin.api.movie_api.patch_movie(movie_id, update_data).json()
            )

        with allure.step('Проверка ID и нового названия в ответе PATCH'):
            assert response.id == movie_data_with_cleanup['id']
            assert response.name == update_data['name']

        with allure.step('Повторное получение обновлённого фильма через GET'):
            check = Movie.model_validate(
                super_admin.api.movie_api.get_movie_by_id(response.id).json()
            )

        with allure.step('Проверка сохранения нового названия фильма'):
            assert check.name == update_data["name"]

    @allure.title('Тест изменения фильма через PATCH без авторизации')
    def test_patch_movie_without_auth(self, api_manager_clean, movie_data_with_cleanup):
        with allure.step('Подготовка ID фильма и новых данных'):
            movie_id = movie_data_with_cleanup['id']
            update_data = {'name': movie_data_with_cleanup['name'] + ' updated'}

        with allure.step('Попытка изменения фильма без авторизации, ожидание 401'):
            response_data = api_manager_clean.movie_api.patch_movie(
                movie_id, update_data, expected_status=401
            ).json()

        with allure.step('Проверка сообщения Unauthorized'):
            assert response_data['message'] == 'Unauthorized'

    @allure.title('Тест изменения фильма через PATCH с некорректным местоположением')
    def test_patch_movie_incorrect_location(self, super_admin, movie_data_with_cleanup):
        with allure.step('Подготовка ID фильма и некорректного местоположения'):
            movie_id = movie_data_with_cleanup['id']
            update_data = {'location': DataGenerator.generate_random_short_name()}

        with allure.step('Изменение фильма с некорректным location, ожидание 400'):
            response_data = super_admin.api.movie_api.patch_movie(
                movie_id, update_data, expected_status=400
            ).json()

        with allure.step('Проверка Bad Request и сообщения о допустимых местоположениях'):
            assert response_data['error'] == 'Bad Request'
            assert "location must be one of the following values: MSK, SPB" in response_data['message']

    @allure.title('Тест удаления фильма через DELETE')
    @pytest.mark.smoke
    def test_delete_movie(self, super_admin, created_movie_data):
        with allure.step('Получение ID созданного фильма'):
            movie_id = created_movie_data['id']

        with allure.step(f'Удаление фильма ID {movie_id} через DELETE'):
            response = super_admin.api.movie_api.delete_movie(movie_id).json()

        with allure.step('Проверка ID удалённого фильма в ответе'):
            assert response['id'] == created_movie_data['id']

        with allure.step('Попытка получения удалённого фильма, ожидание 404'):
            check = super_admin.api.movie_api.get_movie_by_id(
                response['id'], expected_status=404
            ).json()

        with allure.step('Проверка сообщения об отсутствии фильма'):
            assert check['message'] == 'Фильм не найден'

    @pytest.mark.slow
    @allure.title('Тест удаления фильма через DELETE без прав(user)')
    def test_delete_movie_without_rights(self, common_user, movie_data_with_cleanup):
        with allure.step('Получение ID созданного фильма'):
            movie_id = movie_data_with_cleanup['id']

        with allure.step('Попытка удаления фильма пользователем без прав, ожидание 403'):
            response_data = common_user.api.movie_api.delete_movie(
                movie_id, expected_status=403
            ).json()

        with allure.step('Проверка сообщения Forbidden resource'):
            assert response_data['message'] == 'Forbidden resource'

    @allure.title('Тест удаления фильма через DELETE с параметризацией')
    @pytest.mark.parametrize(
        'role, expected_status',
        [('SUPER_ADMIN', 200), ('ADMIN', 403), ('USER', 403)]
    )
    def test_delete_movie_with_parameters(self, role, expected_status, request, created_movie_data, super_admin):
        with allure.step('Получение ID созданного фильма'):
            movie_id = created_movie_data['id']

        with allure.step(f'Удаление фильма ID {movie_id} через API'):
            response = super_admin.api.movie_api.delete_movie(movie_id).json()

        with allure.step('Проверка ID удалённого фильма'):
            assert response['id'] == created_movie_data['id']

        with allure.step('Проверка недоступности удалённого фильма через GET, ожидание 404'):
            check = super_admin.api.movie_api.get_movie_by_id(
                response['id'], expected_status=404
            ).json()

        with allure.step('Проверка сообщения об отсутствии фильма'):
            assert check['message'] == 'Фильм не найден'

    @pytest.mark.smoke
    @allure.title('Тест получения жанров через GET')
    def test_get_genres(self, api_manager):
        with allure.step('Получение списка жанров через GET'):
            response = api_manager.movie_api.get_genres()

        with allure.step('Подготовка TypeAdapter для списка GenreResponse'):
            adapter = TypeAdapter(list[GenreResponse])

        with allure.step('Валидация списка жанров'):
            response_genres = adapter.validate_python(response.json())

        with allure.step('Проверка, что список жанров не пустой'):
            assert response_genres

    @allure.title('Тест создания фильма с проверкой в БД')
    @pytest.mark.db
    def test_create_movie_db(self, super_admin, db_helper, movie_data, movie_cleanup):
        with allure.step('Получение названия фильма для проверки в БД'):
            movie_name = movie_data['name']

        with allure.step(f'Поиск фильма с названием {movie_name} в БД до создания'):
            db_movie = db_helper.get_movie_by_name(movie_name)

        with allure.step('Проверка отсутствия фильма в БД до создания'):
            assert db_movie is None

        with allure.step('Создание фильма через POST /movies'):
            response = super_admin.api.movie_api.create_movie(movie_data)

        with allure.step('Проверка успешного создания фильма, статус 201'):
            assert response.status_code == 201

        with allure.step('Получение ID созданного фильма из ответа'):
            movie_id = response.json()["id"]

        with allure.step(f'Получение фильма ID {movie_id} из БД'):
            db_movie = db_helper.get_movie_by_id(movie_id)

        with allure.step('Проверка наличия фильма и соответствия полей данным запроса'):
            assert db_movie is not None
            assert db_movie.name == movie_data["name"]
            assert db_movie.price == movie_data["price"]
            assert db_movie.description == movie_data["description"]

        with allure.step('Регистрация ID фильма для последующей очистки'):
            movie_cleanup.append(movie_id)

        with allure.step(f'Удаление фильма ID {movie_id} через DELETE'):
            response = super_admin.api.movie_api.delete_movie(movie_id)

        with allure.step('Проверка успешного удаления фильма, статус 200'):
            assert response.status_code == 200

        with allure.step('Поиск удалённого фильма в БД'):
            db_movie = db_helper.get_movie_by_id(movie_id)

        with allure.step('Проверка отсутствия удалённого фильма в БД'):
            assert db_movie is None

        with allure.step('Исключение ID удалённого фильма из списка очистки'):
            movie_cleanup.remove(movie_id)

