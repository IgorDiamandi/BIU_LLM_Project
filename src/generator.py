from openai import OpenAI

client = OpenAI()

chat_history = [
    {
        "role": "system",
        "content": "You are a middle aged man with dark sense of humor working at the college information desk, "
                   "providing helpful information to students and potential students about college courses. "
                   "Your responses should always be polite and concise, "
                   "you can tell a dark joke but only if the question contains a joke within"
                   "you're usually providing the minimal necessary information to answer the question. "
                   "If you do not have an answer, apologize sincerely and let the user know that "
                   "you can't provide that information."
    }
]

def ask_question(question):
    chat_history.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=chat_history,
        temperature=1,
        max_tokens=1024
    )

    answer = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": answer})
    return answer


if __name__ == "__main__":
    user_question = "which courses you can recommend for an old blind captain?"
    answer = ask_question(user_question)
    print(f"Assistant: {answer}")
