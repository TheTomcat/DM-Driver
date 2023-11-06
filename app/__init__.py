import os

from flask import Flask, request
from alchemical.flask import Alchemical
from flask_migrate import Migrate
from config import Config

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

db = Alchemical()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.cli import cli

    app.register_blueprint(cli)
    # from app.gallery import gallery

    # app.register_blueprint(gallery)
    from app.manager import manager

    app.register_blueprint(manager)
    from app.loading import loading

    app.register_blueprint(loading)
    from app.api import api

    app.register_blueprint(api, url_prefix="/api")

    @app.get('/')
    def test():
        return 'Yes'

    @app.after_request
    def after_request(response):
        # Werkzeu sometimes does not flush the request body so we do it here
        request.get_data()
        return response

    return app
