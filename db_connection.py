import mysql.connector
import os
from dotenv import load_dotenv


# Load .env
load_dotenv()

# Connect to MySQL
def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOSTS"),
        user=os.getenv("DB_USERS"),
        password="",  # Make sure password is set in your .env file
        database=os.getenv("DB_NAMES")
    )
    return connection