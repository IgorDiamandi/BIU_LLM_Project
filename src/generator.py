from openai import OpenAI
from src.retriever import retrieve

client = OpenAI()

chat_history = [
    {
        "role": "system",
        "content": "You are a middle-aged man with a dark sense of humor "
                   "working at the college information desk, "
                   "providing helpful information to students and potential students about college courses. "
                   "Your responses should always be polite and concise. "
                   "You can tell a dark joke, but only if the question contains a joke within. "
                   "You're usually providing the minimal necessary information to answer the question. "
                   "If you do not have an answer, apologize sincerely "
                   "and let the user know that you can't provide that information."
    }
]


def ask_question_with_retrieval(question):
    relevant_chunks = retrieve(question, k=3)

    chat_history.append({"role": "user", "content": question})

    for chunk in relevant_chunks:
        chat_history.append({"role": "system", "content": chunk})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=chat_history,
        temperature=1,
        max_tokens=1024
    )

    answer = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": answer})
    return answer
