from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import db
from flask_cors import CORS



app = Flask(__name__)


CORS(app)
# migration initialization
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Account.sqlite'
migrate = Migrate(app, db)
db.init_app(app)



# imports functions from views
from views import *

app.register_blueprint(user_bp)
app.register_blueprint(account_bp)
app.register_blueprint(auth_bp)





if __name__ == '__main__':
    app.run(debug=True)