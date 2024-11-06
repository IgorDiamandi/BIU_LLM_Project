from flask import render_template, request, jsonify
from . import retriever, generator
from . import create_app

app = create_app()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({'error': 'Empty query'}), 400

    # Retrieve relevant documents
    relevant_chunks = retriever.retrieve(user_query)

    # Generate response using retrieved content
    response = generator.generate_response(user_query, relevant_chunks)

    return jsonify({'response': response})