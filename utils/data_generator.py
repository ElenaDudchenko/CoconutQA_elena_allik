import random
import string

from faker import Faker

faker = Faker()

class DataGenerator:

    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        return f"bep{random_string}@gmail.com"

    @staticmethod
    def generate_random_password():
        return faker.password(
            length=8,
            special_chars=False,
            digits=True,
            upper_case=True,
            lower_case=True
        )

    @staticmethod
    def generate_random_name():
        return f"{faker.first_name()} {faker.last_name()}"

    @staticmethod
    def generate_random_movie_name():
        return faker.sentence(nb_words=3)

    @staticmethod
    def generate_random_image_url():
        return faker.image_url()

    @staticmethod
    def generate_random_price():
        return faker.random_int(min=100, max=1000)

    @staticmethod
    def generate_random_description():
        return faker.text(max_nb_chars=100)

    @staticmethod
    def generate_random_location():
        return faker.random_element(elements=("MSK", "SPB"))

    @staticmethod
    def generate_random_published():
        return faker.boolean()

    @staticmethod
    def generate_random_genreId():
        return faker.random_int(min=1, max=1000)

    @staticmethod
    def generate_random_short_name():
        return "".join(random.choices(string.ascii_letters, k=2))






