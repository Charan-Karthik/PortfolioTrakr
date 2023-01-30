# print("running init file")

from flask import Flask
import os
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv("APP_SECRET_KEY") # Needed for session