import tiktoken
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
               "and let the user know that you can't provide that information, "
               "then provide a user with the contact info: https://www.hitech-school.biu.ac.il/, 077-8040865 "
               "Provide the contact information only once per conversation."
}

# Initialize the chat history as a global list
chat_history = [system_message]

# Maximum allowed tokens for the history
MAX_HISTORY_TOKENS = 3000  # Adjust as needed


# Function to calculate token count
def count_tokens(messages, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = sum(len(encoding.encode(message["content"])) for message in messages)
    return num_tokens


# Function to trim chat history to fit within the token limit
def trim_history(history, max_tokens, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    total_tokens = count_tokens(history, model)

    # Remove oldest messages until the total tokens fit within the limit
    while total_tokens > max_tokens and len(history) > 1:
        history.pop(1)  # Remove the second message to preserve the system message
        total_tokens = count_tokens(history, model)


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

    # Trim history to ensure it stays within the token limit
    trim_history(chat_history, MAX_HISTORY_TOKENS, model="gpt-4")

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
