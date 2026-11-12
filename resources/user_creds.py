import os
from dotenv import load_dotenv

load_dotenv()

class SuperAdminCreds:
    USERNAME = os.environ['SUPER_ADMIN_EMAIL']
    PASSWORD = os.environ['SUPER_ADMIN_PASSWORD']