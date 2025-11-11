from dotenv import load_dotenv
import os

class DevelopmentConfig():
    DEBUG = True
    
config = {
    "development": DevelopmentConfig()
}

load_dotenv()

user = os.environ["APP_USER"]
password = os.environ["APP_PASSWORD"]
host = os.environ["DB_HOST"]
database = os.environ["DB_NAME"]

DATABASE_CONECTION_URI = f"mysql+pymysql://{user}:{password}@{host}/{database}"

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]