from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

client = MongoClient(DATABASE_URL)
client.server_info()
print("Connection to the database established successfully.")
db = client["webauthn"]
collection = db["users"]

