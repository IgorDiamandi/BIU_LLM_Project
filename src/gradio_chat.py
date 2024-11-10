import gradio as gr
from generator import ask_question


def chat_interface(user_input):
    return ask_question(user_input)


demo = gr.Interface(fn=chat_interface, inputs="text", outputs="text", title="College Information Desk Chat")

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch()
