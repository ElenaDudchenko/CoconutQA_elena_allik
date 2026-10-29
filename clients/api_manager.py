from clients.auth_api import AuthApi
from clients.movie_api import MovieApi
from clients.user_api import UserApi

class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthApi(session)
        self.user_api = UserApi(session)
        self.movie_api = MovieApi(session)
