import json
import uuid

import streamlit as st

from render.template_render import render_doc
from utils import get_server_response


class StreamlitManager:
    def __init__(self):
        self.header = st.header("DOPNIQUE", divider="violet")
        self.c1, self.c2, self.c3 = st.columns([1, 1, 1])
        st.logo("./static/docs/untitled.png", icon_image="./static/docs/untitled.png")

    def run_server(self):
        if "messages" not in st.session_state:
            st.session_state.messages = self.get_welcome_message()
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        with self.c3:
            if st.button("Очистить сообщения", key="clear_button"):
                st.session_state.messages = self.get_welcome_message()
                st.session_state.session_id = str(uuid.uuid4())

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message['content']:
                    st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("Напишите ваш запрос"):
            if prompt:
                # Add user message to chat history
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": prompt
                    }
                )
                # Display user message in chat message container
                with st.chat_message("user"):
                    st.markdown(prompt)
                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    for mes in get_server_response(st.session_state.session_id, prompt):
                        try:
                            text = json.loads(mes.get('text'))
                        except json.decoder.JSONDecodeError:
                            text = None
                        if text:
                            file_path = './static/docs/additional_template.docx'
                            result_filename = render_doc(text, file_path)
                            with open(f"./static/docs/{result_filename}", 'rb') as f:
                                st.download_button(
                                    'Скачать дополнительное соглашение',
                                    f,
                                    file_name=result_filename
                                )
                        else:
                            response = st.write_stream(self.generate_messages(mes))
                            st.session_state.messages.append(
                                {
                                    "role": "assistant",
                                    "content": response
                                }
                            )

    @staticmethod
    def generate_messages(message_to_gen):
        yield message_to_gen['text']

    @staticmethod
    def get_welcome_message():
        with open('./static/docs/welcome_message.txt', 'r') as f:
            return [
                {
                    "role": "assistant",
                    "content": f.read()
                }
            ]


if __name__ == '__main__':
    StreamlitManager().run_server()
