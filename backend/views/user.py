from models import User,db
from flask import jsonify,request, Blueprint
from werkzeug.security import generate_password_hash


user_bp = Blueprint("user_bp", __name__)