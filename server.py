# print("running server file")

from flask_app import app
# Import Controller(s)
from flask_app.controllers import users
from flask_app.controllers import accounts
from flask_app.controllers import stocks

if __name__ == "__main__":
    app.run(debug = True)