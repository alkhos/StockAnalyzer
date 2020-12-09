from flask import Flask
from config import Config
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# get the app
app = Flask(__name__)

# get session, login manager and DB
sess = Session()
db = SQLAlchemy()
migrate = Migrate(app, db)

# initialize app from config
app.config.from_object(Config)

# Initialize Plugins
db.init_app(app)
sess.init_app(app)

from app import routes, models