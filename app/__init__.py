from flask import Flask
import os

def create_app():
    # Use absolute paths to avoid any issues with locating the folders
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_folder = os.path.join(current_dir, '../web/templates')
    static_folder = os.path.join(current_dir, '../web/static')

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder
    )

    # Import and register routes explicitly to ensure they are included
    from .routes import main
    app.register_blueprint(main)

    return app
