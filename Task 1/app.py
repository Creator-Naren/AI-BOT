from flask import Flask, jsonify, request, redirect, url_for

from config import Config
from extensions import db, login_manager

login_manager.login_view = "auth.login"  # type: ignore[assignment]


@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith("/api/"):
        return jsonify(
            {"success": False, "code": "auth_error", "message": "Authentication required."}
        ), 401
    return redirect(url_for("auth.login"))


def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object(Config)
    if testing:
        app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")

    db.init_app(app)
    import models  # noqa: F401
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    login_manager.init_app(app)

    from routes.api import api_bp
    from routes.auth import auth_bp
    from routes.pages import pages_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app


if __name__ == "__main__":
    application = create_app()
    with application.app_context():
        db.create_all()
    application.run(debug=True)
