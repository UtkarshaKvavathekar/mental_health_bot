# setup streamlit
import streamlit as st
st.set_page_config(page_title="Mental_bot" , layout="wide")
st.title("Mega Mental Bot") #will be deployed on page

# # step4) 
import requests
BACKEND_URL = "http://127.0.0.1:8000/ask"


# # Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    # st.session_state → Streamlit’s memory box(for one session)

# step2: user should be able to add que
# chat input
user_input = st.chat_input("what's in your mind today?")# chat_input → creates a chat text box
if user_input:
    # append user massage
    st.session_state.chat_history.append({"role":"user","content":user_input})
    res = requests.post(BACKEND_URL,json={"message":user_input})
# 1
    # fixed_dummy_res = "im here with you!"
    fixed_dummy_res_from_backend = res
#     #1
    # st.session_state.chat_history.append({"role":"assistant","content":fixed_dummy_res})
    # 2
    st.session_state.chat_history.append({"role":"assistant","content":fixed_dummy_res_from_backend.json()})

# # step3 : show responce from backend-This step is what makes the chatbot actually look like a chat on screen.
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
# # with → enter a special UI block
# # st.chat_message(...) → creates a chat bubble
# # msg["role"] → "user" or "assistant"

#  uv run Streamlit run frontend.py    --run                                   
