from openai import OpenAI
from src.retriever import retrieve
from config.config_helper import openai_api_key


client = OpenAI(api_key=openai_api_key)

# Initialize the assistant's persona and behavior
system_message = {
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

# Initialize the chat history as a global list
chat_history = [system_message]


# Function to ask a question, retrieve relevant documents, and generate a response
def ask_question_with_retrieval(question):
    global chat_history

    # Retrieve relevant document chunks that provide context for the question
    relevant_chunks = retrieve(question)

    # Append the user's question to the chat history
    chat_history.append({"role": "user", "content": question})

    # If there are relevant chunks, append them to the chat history as context
    if relevant_chunks:
        context = "Here are some relevant details I found:\n" + "\n\n".join(relevant_chunks)
        chat_history.append({"role": "system", "content": context})

    # Use the OpenAI API to generate a response based on the chat history
    response = client.chat.completions.create(
        model="gpt-4",
        messages=chat_history,
        temperature=1,
        max_tokens=1024
    )

    # Extract the assistant's response and append it to the chat history
    answer = {
        "role": "assistant",
        "content": response.choices[0].message.content
    }
    chat_history.append(answer)

    # Return the generated answer content
    return answer
