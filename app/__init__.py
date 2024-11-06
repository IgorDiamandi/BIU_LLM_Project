from flask import Flask
import os
from .routes import main


def create_app():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_folder = os.path.join(current_dir, '../web/templates')
    static_folder = os.path.join(current_dir, '../web/static')

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder
    )

    app.register_blueprint(main)

    return app
