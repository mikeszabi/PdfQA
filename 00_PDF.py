# https://blog.streamlit.io/ai-talks-chatgpt-assistant-via-streamlit/

from bs4 import BeautifulSoup

import sys
sys.path.append(r'../')


import streamlit as st
import pandas as pd
from streamlit_chat import message
import chroma_search as search


products_list = []
col1, col2 = st.columns(2)

def clear_text_input():
    # clear_chat_data()
    st.session_state['question'] = st.session_state['input']
    st.session_state['input'] = ""
    message_objects = st.session_state['messages']
    products_list = []

def clear_chat_data():
    message_objects = []
    message_objects.append({"role": "system", 
                            "content": "Egy chatbot vagy, aki egy barkácsáruház termékeivel kacsolatban válaszolsz kérdésekre és ajánlásokat adsz."})

    st.session_state['input'] = ""
    st.session_state['chat_history'] = []
    st.session_state['messages'] = []
    st.session_state['reference'] = []


# Initialize chat history
if 'question' not in st.session_state:
    st.session_state['question'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'messages' not in st.session_state:
    message_objects = []
    message_objects.append({"role": "system",
                            "content": "Egy chatbot vagy, aki szabványügyi kérdésekre felel"})
    st.session_state['messages'] = message_objects
if 'reference' not in st.session_state:
    st.session_state['reference'] = []
else:
    message_objects = st.session_state['messages']

# Chat 
with col1:
    st.text_input("You: ", placeholder="type your question", key="input", on_change=clear_text_input)
    clear_chat = st.button("Clear chat", key="clear_chat", on_click=clear_chat_data)

if st.session_state['question']:
    question = st.session_state['question']
    print("Object before run: ", message_objects)
    message_objects.append({"role": "user", "content": question})
    pages = search.query_chroma(question, 3)
    df=pd.DataFrame.from_records(pages['metadatas'])
    for i, doc in enumerate(pages['documents']):
        # score = 1 - float(prod.vector_score)
        soup = BeautifulSoup(doc)
        brand_dict = {'role': "assistant", "content": f"{soup.text}"}
        products_list.append(brand_dict)
    

    # message_objects.append({"role": "assistant", "content": f"Ezt a 3 terméket találtam:"})
    message_objects.extend(products_list)
    message_objects.append(
        {"role": "assistant", "content": "Ezt a választ szerkesztettem:"})

    result = search.get_recommendation(message_objects)
    message_objects.append({"role": "assistant", "content": result})
    with col1:
        st.session_state['chat_history'].append((question, result))
        st.session_state['messages'] = message_objects
    with col2:
        st.session_state['reference'].append(df)
    print("Result: ", result)
    print("Messages object: ", message_objects)
    with col2:
        st.dataframe(df)


if st.session_state['chat_history']:
    with col1:
        for i in range(len(st.session_state['chat_history'])-1, -1, -1):
            message(st.session_state['chat_history'][i][1], key=str(i))
            # st.markdown(f'\n\nSources: {st.session_state["source_documents"][i]}')
            message(st.session_state['chat_history'][i][0], is_user=True, key=str(i) + '_user')
