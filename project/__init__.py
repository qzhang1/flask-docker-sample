from flask import Flask, jsonify
from flask_restx import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import os
import sys

# instantiate the db
db = SQLAlchemy()


def create_app(script_info=None):
    # instantiate app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)

    # register blueprints
    from project.api.ping import ping_blueprint
    from project.api.users import users_blueprint
    app.register_blueprint(ping_blueprint)
    app.register_blueprint(users_blueprint)

    # shell context for flask cli
    # now we can work with the app context and db without having to import them directly into the shell
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
