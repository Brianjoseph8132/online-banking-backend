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
        Deposits an amount into the account and records the transaction.
        :param amount: The amount to add to the balance.
        """
        if isinstance(amount, str):
            amount = float(amount)
        self.balance += amount
        # Record the transaction
        transaction = Transaction(type="deposit", amount=amount, bank_account_id=self.id)
        db.session.add(transaction)

    def withdraw(self, amount):
        """
        Withdraws an amount from the account and records the transaction.
        :param amount: The amount to subtract from the balance.
        """
        if isinstance(amount, str):
            amount = float(amount)
        self.balance -= amount
        # Record the transaction
        transaction = Transaction(type="withdraw", amount=amount, bank_account_id=self.id)
        db.session.add(transaction)


    def __repr__(self):
        return f"<BankAccount {self.id} - Balance: {self.balance}>"


class Transaction(db.Model):
    """
    Transaction model representing a transaction in the online banking system.
    """
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)  # 'deposit' or 'withdraw'
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'), nullable=False)

    def __repr__(self):
        return f"<Transaction {self.id} - {self.type} {self.amount}>"



# 
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)