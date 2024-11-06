from flask import Blueprint, render_template, request, jsonify
from . import retriever, generator

main = Blueprint('main', __name__)


@main.route('/')
def index():
    # Debug line to see if this function is accessed
    print("Accessing the index route")
    return render_template('index.html')


@main.route('/chat', methods=['POST'])
def chat():
    if request.is_json:
        user_query = request.json.get('query')
    else:
        return jsonify({'error': 'Invalid content type, JSON required'}), 415

    if not user_query:
        return jsonify({'error': 'Empty query'}), 400

    # Retrieve relevant documents
    relevant_chunks = retriever.retrieve(user_query)

    # Generate response using retrieved content
    response = generator.generate_response(user_query, relevant_chunks)

    return jsonify({'response': response})