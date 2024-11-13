from openai import OpenAI
from src.retriever import retrieve

client = OpenAI()

# Initialize chat history with a system message that sets the assistant's persona and behavior
chat_history = [
    {
        "role": "system",
        "content": "You are a middle-aged man with a dark sense of humor "
                   "working at the college information desk, "
                   "providing helpful information to students and potential students about college courses. "
                   "Your responses should always be polite and concise. "
                   "You can tell a dark but polite joke, but only if the question contains a joke within. "
                   "You're usually providing the minimal necessary information to answer the question. "
                   "If you do not have an answer, apologize sincerely "
                   "and let the user know that you can't provide that information."
    }
]

# Function to ask a question, retrieve relevant documents, and generate a response
def ask_question_with_retrieval(question):
    # Retrieve relevant document chunks that provide context for the question
    relevant_chunks = retrieve(question)

    # Append the user's question to the chat history
    chat_history.append({"role": "user", "content": question})

    # Add the retrieved document chunks to the chat history to provide the assistant with more context
    for chunk in relevant_chunks:
        chat_history.append({"role": "system", "content": chunk})

    # Use the OpenAI API to generate a response based on the chat history and the retrieved context
    response = client.chat.completions.create(
        model="gpt-4",
        messages=chat_history,
        temperature=1,
        max_tokens=1024
    )

    # Extract and store the assistant's response from the API result
    answer = response.choices[0].message.content

    # Save the assistant's response to the chat history for future reference
    chat_history.append({"role": "assistant", "content": answer})

    # Return the generated answer
    return answer
