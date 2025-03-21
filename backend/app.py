from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import db, TokenBlocklist
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from datetime import timedelta
from datetime import datetime



app = Flask(__name__)


CORS(app)
# migration initialization
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Account.sqlite'
migrate = Migrate(app, db)
db.init_app(app)



# jwt
app.config["JWT_SECRET_KEY"] = "dadfdgjhghkjhkhl"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] =  timedelta(hours=1)

jwt = JWTManager(app)
jwt.init_app(app)



# imports functions from views
from views import *

app.register_blueprint(user_bp)
app.register_blueprint(account_bp)
app.register_blueprint(auth_bp)





@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None



if __name__ == '__main__':
    app.run(debug=True)