from src.gradio_chat import chat_ui

from flask import Flask
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '../src')
sys.path.insert(0, src_dir)


def create_app():
    template_folder = os.path.join(current_dir, '../web/templates')
    static_folder = os.path.join(current_dir, '../web/static')

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder
    )

    chat_ui.launch()

    return app
