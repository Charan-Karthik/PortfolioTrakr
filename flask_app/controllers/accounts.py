# print("running accounts controller file")

from flask_app import app
from flask import render_template, redirect, session, request, flash
# Import necessary models
from flask_app.models.account import Account
from flask_app.models.user import User
from flask_app.models.stock import Stock

import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")

import finnhub
finnhub_client = finnhub.Client(api_key=API_KEY)

@app.route('/portfoliotrakr/portfolio')
def dashboard():
    if "user_id" not in session:
        return redirect('/portfoliotrakr')
    user_data = {
        "id": session['user_id']
    }
    user_in_db = User.get_one_by_id(user_data)
    
    data = {
        "user_id": session["user_id"]
    }
    all_accounts = Account.get_all(data)

    accounts_total_values = {}
    accounts_total_pls = {}

    for account in all_accounts:
        all_stocks_in_account = Stock.get_all({"account_id":account.id})
        
        sum_purchase_val = 0
        sum_current_val = 0
        sum_pl = 0

        for stock in all_stocks_in_account:
            sum_purchase_val += stock.total_purchase_val
            sum_current_val += stock.total_current_val
            sum_pl += stock.pl
        
        accounts_total_values[account.name] = sum_current_val
        accounts_total_pls[account.name] = sum_pl

    total_value = 0
    for key in accounts_total_values:
        total_value += accounts_total_values[key]
        accounts_total_values[key] = "${:,.2f}".format(accounts_total_values[key])
    total_value_formatted = "${:,.2f}".format(total_value)
    
    total_pl = 0
    for key in accounts_total_pls:
        total_pl += accounts_total_pls[key]
        if accounts_total_pls[key] < 0:
            accounts_total_pls[key] = "-${:,.2f}".format(abs(accounts_total_pls[key]))
        else:
            accounts_total_pls[key] = "${:,.2f}".format(accounts_total_pls[key])
    if total_pl < 0:
        total_pl_formatted = "-${:,.2f}".format(abs(total_pl))
    else:
        total_pl_formatted = "${:,.2f}".format(total_pl)


    return render_template("all_accounts.html", all_accounts=all_accounts, user_in_db=user_in_db, accounts_total_values=accounts_total_values, accounts_total_pls=accounts_total_pls, total_pl=total_pl, total_pl_formatted=total_pl_formatted, total_value_formatted=total_value_formatted)

@app.route('/portfoliotrakr/add-account')
def add_account():
    if "user_id" not in session:
        return redirect('/portfoliotrakr')
    return render_template("add_account.html")

@app.route('/portfoliotrakr/add-account/submit', methods=['POST'])
def submit_add_account():
    if "user_id" not in session:
        return redirect('/portfoliotrakr')
    
    data = {
        "name": request.form["name"],
        "user_id": session["user_id"]
    }
    Account.save(data)

    return redirect('/portfoliotrakr/portfolio')

@app.route('/portfoliotrakr/account/<int:id>')
def show_account_info(id):
    if "user_id" not in session:
        return redirect('/portfoliotrakr')

    one_account = Account.get_one_account({"id":id})
    all_stocks = Stock.get_all({"account_id":id})

    sum_purchase_val = 0
    sum_current_val = 0
    sum_pl = 0

    for stock in all_stocks:
        sum_purchase_val += stock.total_purchase_val
        sum_current_val += stock.total_current_val
        sum_pl += stock.pl

    sum_purchase_val = "${:,.2f}".format(sum_purchase_val)
    sum_current_val = "${:,.2f}".format(sum_current_val)
    if sum_pl < 0:
        formatted_sum_pl = "-${:,.2f}".format(abs(sum_pl))
    else:
        formatted_sum_pl = "${:,.2f}".format(sum_pl)

    latest_update = Stock.last_update({"account_id":id})
    
    return render_template("one_account.html", one_account=one_account, all_stocks=all_stocks, latest_update=latest_update, sum_purchase_val=sum_purchase_val, sum_current_val=sum_current_val, sum_pl=sum_pl, formatted_sum_pl=formatted_sum_pl)

@app.route('/portfoliotrakr/account/<int:id>/edit')
def edit_account_info(id):
    if "user_id" not in session:
        return redirect('/portfoliotrakr')
    
    one_account = Account.get_one_account({"id":id})

    return render_template("edit_account.html", one_account=one_account)

@app.route('/portfoliotrakr/account/<int:id>/update', methods=['POST'])
def update_account_info(id):
    if "user_id" not in session:
        return redirect('/portfoliotrakr')

    data = {
        "id": id,
        "name": request.form["name"]
    }

    Account.update_account(data)
    return redirect('/portfoliotrakr/account/'+str(id))

@app.route('/portfoliotrakr/account/<int:id>/delete')
def delete_account_and_stocks(id):
    if "user_id" not in session:
        return redirect('/portfoliotrakr')
    
    all_stocks = Stock.get_all({"account_id":id})
    
    if len(all_stocks) == 0:
        Account.delete_account({"id":id})
    else:
        Stock.delete_stock_by_account({"id":id})
        Account.delete_account({"id":id})
    
    return redirect('/portfoliotrakr/portfolio')