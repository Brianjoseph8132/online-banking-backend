from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

metadata = MetaData()

db = SQLAlchemy(metadata=metadata)


class User(db.Model):
    """
    User model representing a user in the online banking system.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
     
    # relationship
    bank_account = db.relationship('BankAccount', backref='user', uselist=False)

    def __repr__(self):
        return f"<User {self.username}>"


class BankAccount(db.Model):
    """
    BankAccount model representing a bank account in the online banking system.
    """
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.0, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def deposit(self, amount):
        """
        Deposits an amount into the account.
        :param amount: The amount to add to the balance.
        """
        if isinstance(amount, str):
            amount = float(amount)
        self.balance += amount

    def withdraw(self, amount):
        """
        Withdraws an amount from the account.
        :param amount: The amount to subtract from the balance.
        """
        if isinstance(amount, str):
            amount = float(amount)
        self.balance -= amount

    def __repr__(self):
        return f"<BankAccount {self.id} - Balance: {self.balance}>"



# 
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)