from utils.data_generator import DataGenerator

def get_register_payload(roles=None):
    password = DataGenerator.generate_random_password()
    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": password,
        "passwordRepeat": password,
        "roles": roles or ["USER"]
    }