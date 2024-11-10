import gradio as gr
from generator import ask_question_with_retrieval


def chat_interface(user_input, history=[]):
    history = history or []
    response = ask_question_with_retrieval(user_input)
    history.append((user_input, response))
    return history, history


demo = gr.Interface(
    fn=chat_interface,
    inputs=["text", "state"],
    outputs=["state", "chatbot"],
    title="College Information Desk Chat",
    theme="soft",
    css="""
    .gradio-container {
        background-color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .input-textbox {
        border-radius: 15px;
    }
    .chat-message {
        border-radius: 15px;
        padding: 10px;
        margin: 5px;
    }
    .chat-message.user {
        background-color: #003366;
        color: #ffffff;
        align-self: flex-end;
    }
    .chat-message.bot {
        background-color: #ffffff;
        color: #000000;
        align-self: flex-start;
    }
    .btn-primary {
        background-color: #003366;
        color: #ffffff;
    }
    """
)

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch()
