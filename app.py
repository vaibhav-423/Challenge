# app.py

from flask import Flask, render_template
from backend.config import Config
from backend.models import db
from backend.routes import routes
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Enable CORS if frontend is served separately

    # Register blueprints
    app.register_blueprint(routes)

    # Serve frontend
    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
