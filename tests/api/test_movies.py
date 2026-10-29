from utils.data_generator import DataGenerator

class TestMovies:
    def test_get_movies(self, api_manager_clean):
        response = api_manager_clean.movie_api.get_movies()
        response_data = response.json()

        assert 'movies' in response_data
        assert isinstance(response_data['movies'], list)

    def test_get_movie_by_id(self, api_manager_clean, movie_data_with_cleanup):

        movie_id = movie_data_with_cleanup['id']
        response = api_manager_clean.movie_api.get_movie_by_id(movie_id)
        response_data = response.json()

        assert response_data['id'] == movie_id
        assert 'description' in response_data
        assert 'name' in response_data
        assert 'genre' in response_data

    def test_get_movies_filtered(self, api_manager):
        min_price = 100
        max_price = 200

        response = api_manager.movie_api.get_movies(
            params={
                "minPrice":min_price,
                "maxPrice": max_price
            }
        )
        response_data = response.json()

        assert response_data['movies']
        for movie in response_data['movies']:
            assert min_price <= movie["price"] <= max_price

    def test_create_movie(self, super_admin_api_manager, movie_data):
        response = super_admin_api_manager.movie_api.create_movie(movie_data)
        response_data = response.json()

        try:
            assert 'id' in response_data
            assert response_data['name'] == movie_data['name']
        finally:
            if 'id' in response_data:
                super_admin_api_manager.movie_api.delete_movie(response_data['id'])

    def test_create_movie_without_name(self, super_admin_api_manager, movie_data):
        movie_data_copy = movie_data.copy()
        del movie_data_copy['name']

        response = super_admin_api_manager.movie_api.create_movie(movie_data_copy, expected_status=400)
        response_data = response.json()

        assert response_data['error'] == 'Bad Request'
        assert "Поле name не может быть пустым" in response_data['message']

    def test_create_movie_without_auth(self,api_manager_clean, movie_data):
        response = api_manager_clean.movie_api.create_movie(movie_data, expected_status=401)
        response_data = response.json()

        assert response_data['message'] == 'Unauthorized'

    def test_create_movie_without_rights(self, api_manager, authenticated_user, movie_data):
        response = api_manager.movie_api.create_movie(movie_data, expected_status=403)
        response_data = response.json()

        assert response_data['error'] == 'Forbidden'

    def test_patch_movie(self, super_admin_api_manager, movie_data_with_cleanup):
        movie_id = movie_data_with_cleanup['id']
        update_data = {'name' : movie_data_with_cleanup['name'] + ' updated'}
        response = super_admin_api_manager.movie_api.patch_movie(movie_id, update_data).json()

        assert response['id'] == movie_data_with_cleanup['id']
        assert response['name'] == update_data['name']

        check = super_admin_api_manager.movie_api.get_movie_by_id(response['id']).json()
        assert check['name'] == update_data["name"]

    def test_patch_movie_without_auth(self, api_manager_clean, movie_data_with_cleanup):
        movie_id = movie_data_with_cleanup['id']
        update_data = {'name' : movie_data_with_cleanup['name'] + ' updated'}
        response_data = api_manager_clean.movie_api.patch_movie(movie_id, update_data, expected_status=401).json()

        assert response_data['message'] == 'Unauthorized'

    def test_patch_movie_incorrect_location(self, super_admin_api_manager, movie_data_with_cleanup):
        movie_id = movie_data_with_cleanup['id']
        update_data = {'location' : DataGenerator.generate_random_short_name()}
        response_data = super_admin_api_manager.movie_api.patch_movie(movie_id, update_data, expected_status=400).json()

        assert response_data['error'] == 'Bad Request'
        assert "location must be one of the following values: MSK, SPB" in response_data['message']

    def test_delete_movie(self, super_admin_api_manager, created_movie_data):
        movie_id = created_movie_data['id']
        response = super_admin_api_manager.movie_api.delete_movie(movie_id).json()

        assert response['id'] == created_movie_data['id']

        check = super_admin_api_manager.movie_api.get_movie_by_id(response['id'], expected_status=404).json()
        assert check['message'] == 'Фильм не найден'

    def test_delete_movie_without_rights(self, api_manager, authenticated_user, movie_data_with_cleanup):
        movie_id = movie_data_with_cleanup['id']
        response_data = api_manager.movie_api.delete_movie(movie_id, expected_status=403).json()

        assert response_data['message'] == 'Forbidden resource'

    def test_get_genres(self, api_manager):
        response = api_manager.movie_api.get_genres()
        response_data = response.json()

        assert response_data
        assert isinstance(response_data, list)
        for genre in response_data:
            assert 'id' in genre
            assert 'name' in genre
