# print("running init file")

from flask import Flask
app = Flask(__name__)
app.secret_key = "St0nks!" # Needed for session