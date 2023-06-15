# https://blog.streamlit.io/ai-talks-chatgpt-assistant-via-streamlit/

from bs4 import BeautifulSoup

import sys
sys.path.append(r'../')

import pandas as pd
import streamlit as st
from streamlit_chat import message
import search_document as search

st.set_page_config(layout="wide")

top_k=5

# @st.cache
# def streamlit_ui():
#   dummy_class = BackendLogic()


# products_list = []
# partner='praktiker'
# col1, col2, col3= st.columns(3)
col1, col2 = st.columns(2)


def clear_text_input():
    # clear_chat_data()
    st.session_state['question'] = st.session_state['input']
    st.session_state['input'] = ""


def clear_chat_data():
    chat_handler.clear_messages()
    st.session_state['input'] = ""
    st.session_state['chat_history'] = []
        

# Initialize state variables

print('###############')
if 'language' not in st.session_state:
    st.session_state.language='Hungarian'
# if 'store' not in st.session_state:
#     st.session_state.store='Praktiker'
if 'question' not in st.session_state:
    st.session_state['question'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'chat_handler' not in st.session_state:
    search_engine=search.Search()
    chat_handler=search.Recommend()
else:
    message_objects = st.session_state['messages']


# Sidebars
with st.sidebar:
    bt_lang_selector = st.radio(
        "Choose a language",
        ("Hungarian", "English"),
        on_change=clear_chat_data,
        key='language'
    )
    # bt_prod_selector = st.radio(
    #     "Choose a store",
    #     ("Praktiker", "Rossman"),
    #     on_change=clear_chat_data,
    #     key='store'
    # )


# Chat input
with col1:
    st.text_input("You: ", placeholder="type your question", key="input", on_change=clear_text_input)
    clear_chat = st.button("Clear chat", key="clear_chat", on_click=clear_chat_data)

# QUESTION PROCESSING
if st.session_state['question']:
    question = st.session_state['question']

    chat_handler.append_message({"role": "user", "content": question})
    
    
    search_item=search_engine.get_topk_related_product(question,top_k)
    
    chat_handler.append_message(
        {"role": "assistant", "content": "Ezeket a  documentumokat találtam:"})
    
    
    document_list, meta_list=chat_handler.append_products(search_item,max_prod=top_k)
    
    chat_handler.append_message(
        {"role": "assistant", "content": "A válaszom: "})
 
   
    result=chat_handler.get_recommendation(st.session_state.language)
    
    st.session_state['chat_history'].append((question, result))
    
    #print("Result: ", result)
    #print("Messages object after run: ", len(message_objects))
    
    with col2:
        df_meta=pd.DataFrame(meta_list)
        st.dataframe(df_meta)
    # with col3:    
    #     for i, row in df_meta.iterrows():
    #         st.image(
    #         row['image_url'],
    #         width=100, # Manually Adjust the width of the image as per requirement
    #     )

        
        

if st.session_state['chat_history']:
    for i in range(len(st.session_state['chat_history'])-1, -1, -1):
        with col1:
            message(st.session_state['chat_history'][i][1], key=str(i))
            message(st.session_state['chat_history'][i][0], is_user=True, key=str(i) + '_user')
    # with col3:
    #     if len(search_engine.search_history):
    #         st.json(search_engine.search_history[-1]['question'])
    #         st.json(search_engine.search_history[-1]['meta'])
    #         st.json(search_engine.search_history[-1]['documents_found'])
            