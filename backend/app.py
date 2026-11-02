from flask import Flask, jsonify
from flask_cors import CORS

from V1_reference.backend.routes.sensor_routes import sensor_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "gaitmate-api"})

    app.register_blueprint(sensor_bp, url_prefix="/api")
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
