from models import BankAccount, db, User, Transaction
from flask import jsonify, request
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint

account_bp = Blueprint("account_bp", __name__)

# Create Bank Account API
@account_bp.route("/create_account", methods=["POST"])
@jwt_required()
def create_bank_account():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Check if the user already has a bank account
    if user.bank_account:
        return jsonify({"message": "User already has a bank account"}), 400

    # Create a new bank account
    new_bank_account = BankAccount(balance=0.0, user_id=user.id)
    db.session.add(new_bank_account)
    db.session.commit()

    return jsonify({"message": "Bank account created successfully"}), 201

# Dashboard API
@account_bp.route("/balance", methods=["GET"])
@jwt_required()
def balance():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.bank_account:
        return jsonify({"message": "Unauthorized or No Bank Account"}), 401

    return jsonify({"balance": user.bank_account.balance}), 200

# Transaction API (Deposit or Withdraw)
@account_bp.route("/transaction", methods=["POST"])
@jwt_required()
def transaction():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.bank_account:
        return jsonify({"message": "Unauthorized or No Bank Account"}), 401

    data = request.get_json()
    action = data.get("action")
    amount = data.get("amount")

    if action == "deposit":
        user.bank_account.deposit(amount)
        db.session.commit()
        return jsonify({"message": "Deposit successful"}), 200
    elif action == "withdraw":
        if user.bank_account.balance >= amount:
            user.bank_account.withdraw(amount)
            db.session.commit()
            return jsonify({"message": "Withdraw successful"}), 200
        else:
            return jsonify({"message": "Insufficient balance"}), 400
    else:
        return jsonify({"message": "Invalid action"}), 400

# Deposit API
@account_bp.route("/deposit", methods=["POST"])
@jwt_required()
def deposit():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.bank_account:
        return jsonify({"message": "Unauthorized or No Bank Account"}), 401

    data = request.get_json()
    amount = data.get("amount")

    user.bank_account.deposit(amount)
    db.session.commit()
    return jsonify({"message": "Deposit successful"}), 200

# Withdraw API
@account_bp.route("/withdraw", methods=["POST"])
@jwt_required()
def withdraw():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.bank_account:
        return jsonify({"message": "Unauthorized or No Bank Account"}), 401

    data = request.get_json()
    amount = data.get("amount")

    if user.bank_account.balance >= amount:
        user.bank_account.withdraw(amount)
        db.session.commit()
        return jsonify({"message": "Withdraw successful"}), 200
    else:
        return jsonify({"message": "Insufficient balance"}), 400



# Transaction History API
@account_bp.route("/transaction_history", methods=["GET"])
@jwt_required()
def transaction_history():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not user.bank_account:
        return jsonify({"message": "No bank account found"}), 404

    # Fetch all transactions for the user's bank account
    transactions = Transaction.query.filter_by(bank_account_id=user.bank_account.id).all()

    # Format the transactions for the response
    transaction_history = [
        {
            "id": transaction.id,
            "type": transaction.type,
            "amount": transaction.amount,
            "timestamp": transaction.timestamp.isoformat(),
        }
        for transaction in transactions
    ]

    return jsonify({"transactions": transaction_history}), 200