import streamlit as st
from chatbot_backend import chatbot
from langchain_core.messages import HumanMessage



# st.seesion_state -> dict -> 
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# message_history= []


# Loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.write(message['content'])

user_input = st.chat_input('Type Here')


if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.write(user_input)    
    
    # response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    # ai_message = response['messages'][-1].content
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]}, 
                config={'configurable': {'thread_id': 'thread-1'}},
                stream_mode="messages"
            )
        )
        
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})





