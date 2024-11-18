import gradio as gr
from src.generator import ask_question_with_retrieval


def chat_interface(user_input, history=None):
    """
    Handles user input and appends the bot's response to the chat history.

    :param user_input: The latest input from the user.
    :param history: The ongoing chat history (in 'messages' format).
    :return: Updated chat history.
    """
    # Initialize chat history if it's None
    history = history or []

    # Ensure that history is correctly formatted as a list of dictionaries with 'role' and 'content'
    formatted_history = [
        {"role": entry[0], "content": entry[1]} if isinstance(entry, tuple) else entry
        for entry in history
    ]

    # Append the user's input to the history
    formatted_history.append({"role": "user", "content": user_input})

    # Get the assistant's response using the generator function
    assistant_response = ask_question_with_retrieval(user_input)

    # Append the assistant's response to the chat history
    formatted_history.append(assistant_response)
    return assistant_response

# Define the Gradio ChatInterface
chat_ui = gr.ChatInterface(
    fn=chat_interface,
    title="College Information Desk Chat",
    theme="soft",
    examples=["What courses do you offer?", "Are there courses to learn Data Science"],
    type="messages",
    css_paths="web/static/gradio_styles.css"
)

# Launch the Gradio app
if __name__ == "__main__":
    chat_ui.launch()
