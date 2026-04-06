import streamlit as st
# from transformers import pipeline
from chatbot_02 import chatbot

mybot = chatbot()
workflow = mybot()

# streamlit UI
st.title("LanGraph Chatbot")
st.write("Ask any que")

# input box
que = st.text_input("Enter your que here:")
input = {"messages":[que]}

# button
if st.button("get answer"):
    if input:
        reply = workflow.invoke(input)
        st.write("ANswer:",reply['messages'][-1].content)
    else:
        st.warning("Please enetr que")