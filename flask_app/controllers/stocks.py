# print("running stocks controller file")

from flask_app import app
from flask import render_template, redirect, session, request, flash
# Import necessary models
from flask_app.models.account import Account
from flask_app.models.user import User
from flask_app.models.stock import Stock

import os
# Hiding API Key from being publicly accessible
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")

# API used to fetch current market price data
import finnhub
finnhub_client = finnhub.Client(api_key=API_KEY)

@app.route('/portfoliotrakr/account/<int:id>/add-stock')
def add_stock_page(id):
    # Route guarding -> this should be inaccessible if there is no user in session
    if "user_id" not in session:
        return redirect('/portfoliotrakr')

    # Getting the specific account to add a stock to and then sending that information to the HTML page
    one_account = Account.get_one_account({"id":id})
    return render_template("add_stock.html", one_account=one_account)

# Post method -> results in 'method not allowed' error when attempted to access directly via URL
@app.route('/portfoliotrakr/account/<int:id>/add-stock/submit', methods=['POST'])
def add_stock(id):
    # Route guarding -> this should be inaccessible if there is no user in session
    if "user_id" not in session:
        return redirect('/portfoliotrakr')

    data = {
        "ticker": request.form["ticker"].upper(),
        "num_shares": request.form["num_shares"],
        "avg_price": request.form["avg_price"],
        "account_id": id
    }

    # Attempt to get information from API. Gracefully handle any errors.
    try:
        finnhub_client.quote(data["ticker"])['c'] # The 'c' indicates current price (reference Finnhub Stock API documentation)
    except:
        flash("Incorrect or Unsupported Ticker Symbol, Please Try Again.")
        flash("Currently, PortfolioTrakr only supports US stocks and ETFs (support for Index and Mutual Funds as well as International Stocks is coming soon!).")
        return redirect('/portfoliotrakr/account/'+str(id)+'/add-stock')

    # Inserting the stock information to the database linked by that specific account.
    Stock.save(data)

    return redirect('/portfoliotrakr/account/'+str(id))

@app.route('/portfoliotrakr/account/<int:account_id>/edit-stock-info/<int:stock_id>')
def edit_stock_page(account_id, stock_id):
    # Route guarding -> this should be inaccessible if there is no user in session
    if "user_id" not in session:
        return redirect('/portfoliotrakr')
    
    # Get both the unique account's information and the unique stock's information to send to the HTML
    one_account = Account.get_one_account({"id":account_id})
    one_stock = Stock.get_one_stock({"id":stock_id})

    return render_template("edit_stock.html", one_account=one_account, one_stock=one_stock)

# Post method -> results in 'method not allowed' error when attempted to access directly via URL
@app.route('/portfoliotrakr/account/<int:account_id>/update-stock-info/<int:stock_id>', methods=['POST']) # Could've made this a PUT method since it's updating stock information
def update_stock_info(account_id, stock_id):
    # Route guarding -> this should be inaccessible if there is no user in session
    if "user_id" not in session:
        return redirect('/portfoliotrakr')
    
    data = {
        "id": stock_id,
        "ticker": request.form["ticker"].upper(),
        "num_shares": request.form["num_shares"],
        "avg_price": request.form["avg_price"],
        "account_id": account_id
    }

    # Attempt to get information from API. Gracefully handle any errors.
    try:
        finnhub_client.quote(data["ticker"])['c'] # The 'c' indicates current price (reference Finnhub Stock API documentation)
    except:
        flash("Incorrect or Unsupported Ticker Symbol, Please Try Again.")
        flash("Currently, PortfolioTrakr only supports US stocks and ETFs (support for Index and Mutual Funds as well as International Stocks is coming soon!).")
        return redirect('/portfoliotrakr/account/'+str(account_id)+'/edit-stock-info/'+str(stock_id))

    Stock.update_stock(data)
    return redirect('/portfoliotrakr/account/'+str(account_id))

@app.route('/portfoliotrakr/account/<int:account_id>/delete/<int:stock_id>')
def delete_stock(account_id, stock_id):
    # Route guarding -> this should be inaccessible if there is no user in session
    if "user_id" not in session:
        return redirect('/portfoliotrakr')
    
    Stock.delete_stock({"id":stock_id})
    return redirect('/portfoliotrakr/account/'+str(account_id))