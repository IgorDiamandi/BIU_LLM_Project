from flask import Blueprint, render_template, request, jsonify, url_for
from . import retriever, generator

main = Blueprint('main', __name__)


@main.route('/')
def index():
    print("Accessing the index route")
    return render_template('chat.html')


@main.route('/ask', methods=['POST'])
def ask():
    user_query = request.form.get('question')
    if not user_query:
        return jsonify({'error': 'Empty query'}), 400

    relevant_chunks = retriever.retrieve(user_query)
    response = generator.generate_response(user_query, relevant_chunks)

    return jsonify({'response': response})

