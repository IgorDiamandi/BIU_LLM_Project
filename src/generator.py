import tiktoken
from openai import OpenAI
from src.retriever import retrieve
from config.config_helper import openai_api_key

client = OpenAI(api_key=openai_api_key)
print (f"\n Client: {client}")

# Initialize the assistant's persona and behavior
system_message = {
    "role": "system",
    "content": '''
               ABOUT YOU
               You are a middle-aged professional sales person working for high-tech and cyber security school
               at Bar-Ilan University in Israel.
               
               YOUR ROLE
               Your role is to provide helpful information and promote the school courses selling to customers,
               students and other potential students.               
               
               GUARDRAILS
               1. Your knowledge base hold all courses brochures, syllabus, and schedules.
               2. Carefully read the student's questions. 
               3. You should interact only about Bar-Ilan high-tech and cyber security school courses.
               4. Any discussion on any subject that is not related to Bar-Ilan high-tech and cyber security school courses
                  is not allowed. Apologize and tell the student that you can only discuss the schools courses.
               5. When you can not answer a question because it does not related to the school,
                  apologize and tell the student that you can only discuss the schools courses.
                  
               CONVERSATION HANDLING
               1. Your answers MUST be based only on your knowledge base. 
                  Other sources of information you may have are not allowed. 
               2. Ask the student for clarification questions as necessary,
               3. Encourage the student to provide you additional information in order to come up with the best results.
               4. As a professional sales representative Your tone of speech should be:
                  Proactive, engaged, professional, friendly, polite, and concise.
               5. If you do not have the information on hand, apologize sincerely that you cannot provide this information,
                  and give the student this contact info: https://www.hitech-school.biu.ac.il/, 077-8040865.             
               '''
    }

# Initialize the chat history as a global list
chat_history = [system_message]

# Maximum allowed tokens for the history
MAX_HISTORY_TOKENS = 50000  # Adjust as needed

# Function to calculate token count
def count_tokens(messages, model="gpt-4o-2024-11-20"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = sum(len(encoding.encode(message["content"])) for message in messages)
    return num_tokens


# Function to trim chat history to fit within the token limit
def trim_history(history, max_tokens, model="gpt-4o-2024-11-20"):
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
    trim_history(chat_history, MAX_HISTORY_TOKENS, model="gpt-4o-2024-11-20")

    # Use the OpenAI API to generate a response based on the chat history
    response = client.chat.completions.create(
        model="gpt-4o-2024-11-20",
        messages=chat_history,
        temperature=1,
        max_tokens=2048
    )

    # Extract the assistant's response and append it to the chat history
    answer = {
        "role": "assistant",
        "content": response.choices[0].message.content
    }
    chat_history.append(answer)

    # Return the generated answer content
    return answer