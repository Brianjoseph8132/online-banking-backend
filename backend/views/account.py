from models import BankAccount, db, User, Transaction
from flask import jsonify, request
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from flask import Blueprint

account_bp = Blueprint("account_bp", __name__)

# Create Bank Account API
@account_bp.route("/create_account", methods=["POST"])
@jwt_required()
def create_account():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.bank_account:
        return jsonify({"error": "User already has a bank account"}), 400

    data = request.get_json()
    initial_deposit = float(data.get('initial_deposit', 0.0))
    pin = data.get('pin')  # Get pin from the request

    # Validate pin
    if not pin:
        return jsonify({"message": "Pin is required"}), 400

    # Ensure pin is a 4-digit number
    if not pin.isdigit() or len(pin) != 4:
        return jsonify({"error": "Pin must be a 4-digit number"}), 400


    # Validate deposit amount
    if initial_deposit < 0:
        return jsonify({"error": "Deposit amount cannot be negative"}), 400

    # Create new bank account
    new_account = BankAccount(balance=initial_deposit, user_id=user.id)

    # Set the pin after hashing
    new_account.set_pin(pin)

    db.session.add(new_account)
    db.session.flush()  # This assigns an ID to new_account without committing
    
    # Record initial deposit if amount > 0
    if initial_deposit > 0:
        transaction = Transaction(
            type="deposit",
            amount=initial_deposit,
            bank_account_id=new_account.id  # Now has a valid ID
        )
        db.session.add(transaction)
    
    db.session.commit()  # Commit both objects together

    return jsonify({
        "success": "Bank account created successfully",
        "account_id": new_account.id,
        "balance": new_account.balance
    }), 201

# Dashboard API
@account_bp.route("/balance", methods=["GET"])
@jwt_required()
def balance():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.bank_account:
        return jsonify({"error": "Unauthorized or No Bank Account"}), 401

    return jsonify({"balance": user.bank_account.balance}), 200

# Transaction API (Deposit or Withdraw)
@account_bp.route("/transaction", methods=["POST"])
@jwt_required()
def transaction():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.bank_account:
        return jsonify({"error": "No bank account found"}), 404

    data = request.get_json()
    action = data.get("action")
    amount = data.get("amount")
    pin = data.get("pin")  # Pin provided by the user for transaction

    # Check if pin is provided
    if not pin:
        return jsonify({"error": "Pin is required"}), 400

    # Verify if the provided pin matches the stored hash
    if not check_password_hash(user.bank_account.pin, pin):  # Assuming bank_account has the pin
        return jsonify({"error": "Incorrect pin"}), 401

    # Convert amount to float if it's a string
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400

    # Perform transaction based on action (deposit or withdraw)
    if action == "deposit":
        user.bank_account.deposit(amount)
        db.session.commit()
        return jsonify({"success": "Deposit successful"}), 200
    elif action == "withdraw":
        if user.bank_account.balance >= amount:
            user.bank_account.withdraw(amount)
            db.session.commit()
            return jsonify({"success": "Withdraw successful"}), 200
        else:
            return jsonify({"error": "Insufficient balance"}), 400
    else:
        return jsonify({"error": "Invalid action"}), 400

# Deposit API
@account_bp.route("/deposit", methods=["POST"])
@jwt_required()
def deposit():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.bank_account:
        return jsonify({"error": "Unauthorized or No Bank Account"}), 401

    data = request.get_json()
    amount = data.get("amount")

    user.bank_account.deposit(amount)
    db.session.commit()
    return jsonify({"success": "Deposit successful"}), 200

# Withdraw API
@account_bp.route("/withdraw", methods=["POST"])
@jwt_required()
def withdraw():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.bank_account:
        return jsonify({"error": "Unauthorized or No Bank Account"}), 401

    data = request.get_json()
    amount = data.get("amount")

    if user.bank_account.balance >= amount:
        user.bank_account.withdraw(amount)
        db.session.commit()
        return jsonify({"success": "Withdraw successful"}), 200
    else:
        return jsonify({"error": "Insufficient balance"}), 400



# Transaction History API
@account_bp.route("/transaction_history", methods=["GET"])
@jwt_required()
def transaction_history():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.bank_account:
        return jsonify({"error": "No bank account found"}), 404

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


@account_bp.route("/has_account", methods=["GET"])
@jwt_required()
def has_account():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    has_account = user.bank_account is not None
    return jsonify({"has_account": has_account}), 200