from flask import Flask
from flask_migrate import Migrate
from views import users_bp, galactic_objects_bp, demand_bp
from models import db
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(users_bp)
app.register_blueprint(galactic_objects_bp)
app.register_blueprint(demand_bp)

CORS(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)