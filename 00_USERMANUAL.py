# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 10:30:24 2023

@author: Szabi
"""

from io import StringIO

import openai
import os
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
import streamlit as st
from streamlit_chat import message
import time


load_dotenv(r'.env')

openai.api_type = "azure"
openai.api_key = os.getenv('PREFIX_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('PREFIX_AZURE_API_BASE')
openai.api_version = os.getenv('PREFIX_AZURE_API_VERSION')

tmp_dir=r"./tmp"

if 'empty_tmp_files' not in st.session_state:
    for f in os.listdir(tmp_dir):
        os.remove(os.path.join(tmp_dir, f))
    st.session_state['empty_tmp_files']=True
if 'goal' not in st.session_state:
    st.session_state['goal']="Készíts használati utasítást!"
if 'page_contents' not in st.session_state:
    st.session_state['page_contents']=[]
    
#Set the application title
st.title("USER MANUAL / SUMMARY CREATOR")


def generate_summarizer(
    max_tokens,
    temperature,
    top_p,
    frequency_penalty,
    prompt,
    person_type,
    sum_instruction='',
):
    res = openai.ChatCompletion.create(
        engine="gpt-35-turbo-deployment",
        max_tokens=4000,
        temperature=0.7,
        top_p=0.5,
        frequency_penalty=0.5,
        messages=
       [
         {
          "role": "system",
          #"content": "Create a user manual!",
          "content": f"{sum_instruction}",
         },
         {
          "role": "user",
          "content": f"{person_type} részére: {prompt}",
         },
        ],
    )
    return res["choices"][0]["message"]["content"]

@st.cache_data
def file_processor(files):
    for i, file in enumerate(files):
        temp_path=os.path.join(tmp_dir, file.name)
        if not os.path.exists(temp_path):
            bytes_data = files[i].read()  # read the content of the file in binary
            temp_path=os.path.join(r"./tmp", file.name)
            print(temp_path)
            with open(temp_path, "wb") as f:
                f.write(bytes_data)  # write this content elsewhere
            loader = PyPDFLoader(temp_path)
            pages = loader.load_and_split()
            for page in pages:
                st.session_state['page_contents'].append(page.page_content.replace("\n", ""))
            print(len(st.session_state['page_contents']))

files = st.file_uploader("File upload", type=["pdf"], accept_multiple_files=True)
file_processor(files)

#Provide the input area for text to be summarized
# input_text = st.text_area("Enter the text you want to summarize:", height=200)

#Initiate three columns for section to be side-by-side
# col1, col2, col3 = st.columns(3)

#Slider to control the model hyperparameter
with st.sidebar:
    token = st.slider("Token", min_value=0.0, max_value=10000.0, value=50.0, step=1.0)
    temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
    top_p = st.slider("Nucleus Sampling", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    f_pen = st.slider("Frequency Penalty", min_value=-1.0, max_value=1.0, value=0.0, step=0.01)

#Selection box to select the summarization style
with st.sidebar:
    option = st.selectbox(
        "How do you like to be explained?",
        (
            "Second-Grader",
            "Professional Data Scientist",
            "Housewives",
            "Retired",
            "University Student",
        ),
    )

#Showing the current parameter used for the model 
with st.sidebar:
    with st.expander("Current Parameter"):
        st.write("Current Token :", token)
        st.write("Current Temperature :", temp)
        st.write("Current Nucleus Sampling :", top_p)
        st.write("Current Frequency Penalty :", f_pen)

#Creating button for execute the text summarization

if st.button("UserManual"):
    if len(st.session_state['page_contents'])>0:
        for i, page_content in enumerate(st.session_state['page_contents']):
            summary_text=generate_summarizer(token, temp, top_p, f_pen, page_content, option,
                                        sum_instruction='Create a User Manual from the content Hungarian!')
            message(f"Page:{i}\n:{summary_text}",key=str(i))
            print(i)
            time.sleep(10)
        # st.write(generate_summarizer(token, temp, top_p, f_pen, input_text, option))
if st.button("Summarize"):
    if len(st.session_state['page_contents'])>0:
        for i, page_content in enumerate(st.session_state['page_contents']):
            summary_text=generate_summarizer(token, temp, top_p, f_pen, page_content, option,
                                        sum_instruction='Summarize the content in Hungarian!')  
            message(f"Page:{i}\n:{summary_text}",key=str(i))
            print(i)
            time.sleep(10)
        # st.write(generate_summarizer(token, temp, top_p, f_pen, input_text, option))