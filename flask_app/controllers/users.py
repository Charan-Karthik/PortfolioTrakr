# print("running users controller file")

from flask_app import app
from flask import render_template, redirect, session, request, flash
from flask_app.models.user import User
# from flask_app.models.stock import Stock
# from flask_app.models.account import Account
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
from flask_app.controllers import accounts

# Default base URL, should redirect to landing page
@app.route('/')
def initial_page():
    if "user_id" in session:
        del session["user_id"]
    return redirect('/portfoliotrakr')

# Landing page.
@app.route('/portfoliotrakr')
def landing_page():
    # To prevent bugs from a logged in user visiting this page, the logged in user is removed from session
    if "user_id" in session:
        del session["user_id"]
    return render_template("landing_page.html")

@app.route('/portfoliotrakr/login')
def login_page():
    # To prevent bugs from a logged in user visiting this page, the logged in user is removed from session
    if "user_id" in session:
        del session["user_id"]
    return render_template("login.html")

# Post method, shouldn't be directly accessible from the front end
@app.route('/portfolio/sign-in', methods=['POST'])
def sign_in():
    data = {
        "email": request.form['email']
    }
    user_in_db = User.get_one_by_email(data)
    if not user_in_db:
        flash("Incorrect email and/or password.")
        return redirect('/portfoliotrakr/login')
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Incorrect email and/or password.")
        return redirect('/portfoliotrakr/login')
    session["user_id"] = user_in_db.id
    return redirect('/portfoliotrakr/portfolio')

@app.route('/portfoliotrakr/about')
def about_page():
    return render_template("about.html")

@app.route('/portfoliotrakr/preview')
def preview_page():
    return render_template("preview.html")

@app.route('/portfoliotrakr/register', methods=['POST'])
def register_user():
    # Validate user registration info
    if not User.validate_user(request.form):
        return redirect('/portfoliotrakr')
    data = {
        "email": request.form['email']
    }
    user_in_db = User.get_one_by_email(data)
    if user_in_db:
        flash("Email already in use")
        return redirect('/portfoliotrakr')
    else: # encrypt user password
        pw_hash = bcrypt.generate_password_hash(request.form["password"])
    
    # Add user to database
    data = {
            "first_name": request.form["first_name"],
            "last_name": request.form["last_name"],
            "email": request.form["email"],
            "password": pw_hash
        }
    user_id = User.save(data)
    session["user_id"] = user_id
    return redirect('/portfoliotrakr/portfolio')

@app.route('/portfoliotrakr/edit-user-account')
def edit_account():
    user_data = {
        "id": session['user_id']
    }
    user_in_db = User.get_one_by_id(user_data)
    return render_template("edit_user.html", user_in_db=user_in_db)

@app.route('/portfoliotrakr/update-user-account', methods=['POST'])
def update_user_account():
    if "user_id" not in session:
        return redirect('/portfoliotrakr')

    data = {
        "id": session['user_id'],
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email']
    }
    if not User.validate_user_info_update(data):
        return redirect('/portfoliotrakr/edit-user-account')
    
    User.update_user(data)
    flash("User Information Updated Successfully")

    return redirect('/portfoliotrakr/portfolio')

@app.route('/portfoliotrakr/update-user-password', methods=['POST'])
def update_user_password():
    if "user_id" not in session:
        return redirect('/portfoliotrakr')

    user_in_db = User.get_one_by_id({"id":session['user_id']})
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Current password is incorrect. Please try again.")
        return redirect('/portfoliotrakr/edit-user-account')
    
    if request.form['password'] == request.form['new_password']:
        flash("New password cannot be the same as the current password.")
        return redirect('/portfoliotrakr/edit-user-account')
    
    pwd_data = {
        "new_password":request.form['new_password'],
        "confirm_new_password":request.form['confirm_new_password'],
    }
    if not User.validate_user_pwd_update(pwd_data):
        return redirect('/portfoliotrakr/edit-user-account')

    pw_hash = bcrypt.generate_password_hash(request.form["new_password"])
    data = {
        "id": session['user_id'],
        "new_password": pw_hash
    }
    User.update_user_password(data)
    flash("Password Updated Successfully")

    return redirect('/portfoliotrakr/portfolio')