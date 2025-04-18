from models import User,db, TokenBlocklist
from flask import jsonify,request, Blueprint
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from datetime import timedelta
from datetime import timezone


auth_bp = Blueprint("auth_bp", __name__)



# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")  # Either username or email
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    
    else:
        return jsonify({"error": "Either email/password is incorrect"}), 404
    

# Current User
@auth_bp.route("/current_user", methods=["GET"])
@jwt_required()
def current_user():
    current_user_id  = get_jwt_identity()
    user =  User.query.get(current_user_id)
    user_data = {
            'id':user.id,
            'email':user.email,
            'username':user.username
        }

    return jsonify(user_data)


# Logout
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify({"success":"Logged out successfully"})


# login with google
@auth_bp.route("/login_with_google", methods=["POST"])
def login_with_google():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    email = data["email"]

    user = User.query.filter_by(email=email).first()

    if user :
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200

    return jsonify({"error": "Email is incorrect"})
