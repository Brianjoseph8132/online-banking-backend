from models import User,db
from flask import jsonify,request, Blueprint
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request



user_bp = Blueprint("user_bp", __name__)



# Add user
@user_bp.route("/users", methods=["POST"])
def add_users():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    raw_password = data.get('password')  # Get the original password

    # # Debugging prints
    # print("Username:", username)
    # print("Email:", email)
    # print("Raw password:", raw_password)


    # Validate password length before hashing
    if not isinstance(raw_password, str) or len(raw_password) != 8:
        return jsonify({"error": "Password must be exactly 8 characters"}), 400

    password = generate_password_hash(raw_password)  # Hash the password

    check_username = User.query.filter_by(username=username).first()
    check_email = User.query.filter_by(email=email).first()

    

    if check_username or check_email:
        return jsonify({"error":"Username/email exists"}), 404

    else:
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": "Added successfully"}), 201



# Update User
@user_bp.route('/update_profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    # Check if new username/email already exists
    if "username" in data:
        existing_user = User.query.filter_by(username=data["username"]).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Username already taken'}), 400
        user.username = data["username"]

    if "email" in data:
        existing_email = User.query.filter_by(email=data["email"]).first()
        if existing_email and existing_email.id != user_id:
            return jsonify({'error': 'Email already in use'}), 400
        user.email = data["email"]

    if "password" in data and data["password"]:
        user.password = generate_password_hash(data["password"])

    db.session.commit()
    return jsonify({'success': 'Profile updated successfully'}), 200

    
# Delete
@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_users(user_id):
    current_user_id = get_jwt_identity()

    if user_id != current_user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User you are trying to delete doesn't exist"}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"success": "Deleted successfully"}), 200
