from openai import OpenAI
from src.retriever import retrieve

client = OpenAI()

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

# Function to ask a question, retrieve relevant documents, and generate a response
# Function to ask a question, retrieve relevant documents, and generate a response
def ask_question_with_retrieval(question):
    # Retrieve relevant document chunks that provide context for the question
    relevant_chunks = retrieve(question)

    # Build the complete chat history including system message
    messages = [system_message]

    # Append the user's question to the chat history
    messages.append({"role": "user", "content": question})

    # If there are relevant chunks, append them to the chat history as context
    if relevant_chunks:
        context = "Here are some relevant details I found:\n" + "\n\n".join(relevant_chunks)
        messages.append({"role": "system", "content": context})

    # Use the OpenAI API to generate a response based on the chat history and the retrieved context
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=1,
        max_tokens=1024
    )

    # Extract and format the assistant's response as a dictionary
    answer = {
        "role": "assistant",
        "content": response.choices[0].message.content
    }

    # Return the generated answer
    return answer