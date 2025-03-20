from models import BankAccount,db
from flask import jsonify,request, Blueprint
from werkzeug.security import generate_password_hash


account_bp = Blueprint("account_bp", __name__)