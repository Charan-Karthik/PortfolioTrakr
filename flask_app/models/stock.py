from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.user import User

import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")

import finnhub
finnhub_client = finnhub.Client(api_key=API_KEY)

# Model for adding a ticker to a specified investment account for a specific user's profile
class Stock:
    def __init__(self, data):
        self.id = data["id"]
        self.ticker = data["ticker"]
        self.num_shares = data["num_shares"]
        self.avg_price = data["avg_price"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.account_id = data["account_id"]

        # These are for storing the information coming from the API
        self.current_price = None
        self.total_purchase_val = None
        self.total_current_val = None
        self.pl = None

        self.current_price_formatted = None
        self.total_purchase_val_formatted = None
        self.total_current_val_formatted = None
        self.pl_formatted = None
        # self.company_name = None
    
    @classmethod
    def get_all(cls, data):
        query = "SELECT * FROM stocks WHERE stocks.account_id = %(account_id)s"
        results = connectToMySQL("portfolio_tracker").query_db(query, data)

        all_stocks = []
        for stock in results:
            single_stock = cls(stock)
            
            single_stock.current_price = finnhub_client.quote(stock['ticker'])['c']
            single_stock.total_purchase_val = single_stock.num_shares * single_stock.avg_price
            single_stock.total_current_val = single_stock.num_shares * single_stock.current_price
            single_stock.pl = single_stock.total_current_val - single_stock.total_purchase_val
            # single_stock.company_name = finnhub_client.company_profile2(symbol=stock['ticker'])['name']
            
            single_stock.current_price_formatted = "${:,.2f}".format(single_stock.current_price)
            single_stock.total_purchase_val_formatted = "${:,.2f}".format(single_stock.total_purchase_val)
            single_stock.total_current_val_formatted = "${:,.2f}".format(single_stock.total_current_val)
            if single_stock.pl < 0:
                single_stock.pl_formatted = "-${:,.2f}".format(abs(single_stock.pl))
            else:
                single_stock.pl_formatted = "${:,.2f}".format(single_stock.pl)

            all_stocks.append(single_stock)

        return all_stocks
    
    @classmethod
    def save(cls, data):
        query = "INSERT INTO stocks(ticker, num_shares, avg_price, created_at, updated_at, account_id) VALUES(%(ticker)s, %(num_shares)s, %(avg_price)s, NOW(), NOW(), %(account_id)s)"
        return connectToMySQL("portfolio_tracker").query_db(query, data)
    
    @classmethod
    def get_one_stock(cls, data):
        query = "SELECT * FROM stocks WHERE id=%(id)s"
        results = connectToMySQL("portfolio_tracker").query_db(query, data)
        
        one_stock = cls(results[0])
        return one_stock
    
    @classmethod
    def update_stock(cls, data):
        query = "UPDATE stocks SET ticker=%(ticker)s, num_shares=%(num_shares)s, avg_price=%(avg_price)s, updated_at=NOW() WHERE id=%(id)s"
        return connectToMySQL("portfolio_tracker").query_db(query, data)
    
    @classmethod
    def delete_stock(cls, data):
        query = "DELETE FROM stocks WHERE id=%(id)s"
        return connectToMySQL("portfolio_tracker").query_db(query, data)
    
    @classmethod
    def delete_stock_by_account(cls, data):
        query = "DELETE FROM stocks WHERE account_id=%(id)s"
        return connectToMySQL("portfolio_tracker").query_db(query, data)

    @classmethod
    def last_update(cls, data):
        query = "SELECT updated_at FROM stocks WHERE stocks.account_id = %(account_id)s GROUP BY updated_at ORDER BY updated_at DESC"
        results = connectToMySQL("portfolio_tracker").query_db(query, data)
        
        if len(results) < 1:
            return
        latest_update = results[0]["updated_at"]

        return latest_update