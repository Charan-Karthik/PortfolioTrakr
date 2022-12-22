from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re

# This class is for people making an account on the PortfolioTrakr website.
class User:
    def __init__(self, data):
        self.id = data["id"]
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.email = data["email"]
        self.password = data["password"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
    
    # Add User Account to Database
    @classmethod
    def save(cls, data):
        query = "INSERT INTO users(first_name, last_name, email, password, created_at, updated_at) VALUES(%(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW())"

        return connectToMySQL("portfolio_tracker").query_db(query, data)
    
    # Check if user email is already in the database
    @classmethod
    def get_one_by_email(cls, data):
        query = "SELECT * FROM users WHERE email=%(email)s"
        results = connectToMySQL("portfolio_tracker").query_db(query, data)
        if len(results) < 1:
            return False
        
        return cls(results[0])
    
    # Get a specific user
    @classmethod
    def get_one_by_id(cls, data):
        query = "SELECT * FROM users WHERE id=%(id)s"
        results = connectToMySQL("portfolio_tracker").query_db(query, data)
        
        if len(results) < 1:
            return False
        
        return cls(results[0])
    
    @classmethod
    def update_user(cls, data):
        query = "UPDATE users SET first_name=%(first_name)s, last_name=%(last_name)s, email=%(email)s, updated_at=NOW() WHERE id=%(id)s"
        return connectToMySQL("portfolio_tracker").query_db(query, data)
    
    @classmethod
    def update_user_password(cls, data):
        query = "UPDATE users SET password=%(new_password)s, updated_at=NOW() WHERE id=%(id)s"
        return connectToMySQL("portfolio_tracker").query_db(query, data)
    
    # Sign Up/Registration Validation
    @staticmethod
    def validate_user(data):
        is_valid = True

        if len(data["first_name"]) < 1:
            flash("First name must be at least 1 character long.")
            is_valid = False
        
        if len(data["last_name"]) < 1:
            flash("Last name must be at least 1 character long.")
            is_valid = False
        
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(data["email"]):
            flash("Must use valid email format.")
            is_valid = False

        if len(data["password"]) < 8:
            flash("Password must be at least 8 characters long.")
            is_valid = False
        
        if data["password"] != data["confirm_password"]:
            flash("Passwords must match.")
            is_valid = False

        return is_valid
    
    @staticmethod
    def validate_user_info_update(data):
        is_valid = True

        if len(data["first_name"]) < 1:
            flash("First name must be at least 1 character long.")
            is_valid = False
        
        if len(data["last_name"]) < 1:
            flash("Last name must be at least 1 character long.")
            is_valid = False
        
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(data["email"]):
            flash("Must use valid email format.")
            is_valid = False

        return is_valid
    
    @staticmethod
    def validate_user_pwd_update(data):
        is_valid = True

        if len(data["new_password"]) < 8:
            flash("New password must be at least 8 characters long.")
            is_valid = False
        
        if data["new_password"] != data["confirm_new_password"]:
            flash("New passwords must match.")
            is_valid = False

        return is_valid