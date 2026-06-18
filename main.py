from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from app.infrastructure.container import Container
from app.adapters.http.notification_blueprint import bp as notifications_bp

import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)


def create_app() -> Flask:
    app = Flask(__name__)

    # CORS — permite llamadas desde cualquier origen (interfaz en Vercel)
    CORS(app)

    container = Container()
    app.extensions["container"] = container

    app.register_blueprint(notifications_bp)

    @app.get("/")
    def health():
        return jsonify({
            "status": "ok",
            "project": "Python - Flask Hexagonal Architecture",
            "channels": ["email", "sms", "in_app"]
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
