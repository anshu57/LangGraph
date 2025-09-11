import streamlit as st
from langgraph_tool_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# ******************************** utility functions **************
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []


def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']



# ************************** session setuo ************
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []
add_thread(st.session_state['thread_id'])

# ***************************** Sidebar UI ************
st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button("New Chat"):
    reset_chat()


st.sidebar.header("My Conversations")

for thread_id in st.session_state['chat_threads']:
    if st.sidebar.button(str(thread_id)):
        messages = load_conversation(thread_id)

        temp_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role= 'user'
            else:
                role= 'assistant'
            temp_messages.append({'role': role, 'content': message.content})

        st.session_state['message_history'] = temp_messages


for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
user_input = st.chat_input("Type Here")

if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
    with st.chat_message("assisstant"):
        def ai_only_stream():
            for message_chunk in chatbot.stream(
                {"messages": [HumanMessage(content= user_input)]},
                config= CONFIG  
            ):
                print(message_chunk)
                if message_chunk.get('chat_node'):
                    if isinstance(message_chunk['chat_node']['messages'][-1], AIMessage):
                        ai_message = message_chunk['chat_node']['messages'][-1].content
                        yield ai_message
        ai_message = st.write_stream(ai_only_stream())
    st.session_state["message_history"].append({"role": "assisstant", "content": ai_message})

    