from flask import Blueprint, render_template, request, jsonify, url_for
from . import retriever, generator
from .generator import ask_question

main = Blueprint('main', __name__)


@main.route('/')
def index():
    print("Accessing the index route")
    return render_template('chat.html')


@main.route('/ask', methods=['POST'])
def chat():
    user_question = request.json.get("question")
    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    answer = ask_question(user_question)
    return jsonify({"response": answer})

