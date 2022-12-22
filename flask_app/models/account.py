from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.user import User
from flask_app.models.stock import Stock

# Once a User has a PortfolioTrakr account, they can add individual investment accounts. This class is for the individual investment accounts
class Account:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.user_id = data["user_id"]

        # This information will be assigned after API calls have been made.
        self.account_value = None
        self.account_pl = None
    
    @classmethod
    def save(cls, data):
        query = "INSERT INTO accounts(name, created_at, updated_at, user_id) VALUES(%(name)s, NOW(),NOW(), %(user_id)s)"
        return connectToMySQL("portfolio_tracker").query_db(query, data)
        # data is a dictionary
    
    @classmethod
    def get_all(cls, data):
        query = "SELECT * FROM accounts WHERE accounts.user_id = %(user_id)s"
        results = connectToMySQL("portfolio_tracker").query_db(query, data)

        all_accounts = []
        for account in results:
            single_account = cls(account)
            all_accounts.append(single_account)

        return all_accounts
    
    @classmethod
    def get_one_account(cls, data):
        query = "SELECT * FROM accounts WHERE id=%(id)s"
        results = connectToMySQL("portfolio_tracker").query_db(query, data)
        
        one_account = cls(results[0])
        return one_account
    
    @classmethod
    def update_account(cls, data):
        query = "UPDATE accounts SET name=%(name)s, updated_at=NOW() WHERE id=%(id)s"
        return connectToMySQL("portfolio_tracker").query_db(query, data)
    
    @classmethod
    def delete_account(cls, data):
        query = "DELETE FROM accounts WHERE id=%(id)s"
        return connectToMySQL("portfolio_tracker").query_db(query, data)