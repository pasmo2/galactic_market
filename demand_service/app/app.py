from flask import Flask
from flask_migrate import Migrate
from .views import demands_bp
from .models import db
from flask_cors import CORS
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@db/mydatabase?client_encoding=utf8')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(demands_bp)

CORS(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)