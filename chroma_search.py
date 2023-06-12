
import logging
logging.getLogger().setLevel(logging.CRITICAL)

import numpy as np
import logging
import os
import openai
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
from translator import translate_openai



load_dotenv(r'.env')

openai.api_type = "azure"
openai.api_key = os.getenv('PREFIX_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('PREFIX_AZURE_API_BASE')
openai.api_version = os.getenv('PREFIX_AZURE_API_VERSION')


# load_dotenv()
logging.basicConfig(level=logging.DEBUG)


EMBEDDING_MODEL = "text-embedding-ada-002"
ABS_PATH = r'.' #os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(ABS_PATH, "db") # persistent directory
COLLECTION='standards'
# DB_DIR = os.path.join(ABS_PATH, "db2")
# COLLECTION='fonendoscope'


def query_chroma(query_texts, max_results):

    query_texts_en=translate_openai(query_texts)
    embedding_function = OpenAIEmbeddingFunction(api_key=openai.api_key, model_name=EMBEDDING_MODEL)

    client = chromadb.Client(
        chromadb.config.Settings(
            persist_directory=DB_DIR,
            chroma_db_impl="duckdb+parquet",
        )
    )

    collection = client.get_collection(name=COLLECTION,embedding_function=embedding_function)
    
    results = collection.query(query_texts=query_texts_en, n_results=max_results, include=['distances'])
    pages=collection.get(results['ids'][0])
    # pages['metadatas']
    # pages['documents']
    return pages

def get_recommendation(chat_history):
    completion = openai.ChatCompletion.create(
        engine="gpt-35-turbo-deployment",
        messages=chat_history
    )
    return completion.choices[0].message['content']

    
# from bs4 import BeautifulSoup

# import pandas as pd
# question = "Mik a célja az orvostechnikai eszközökhöz adott tájékoztatásnak?"
# question = "Mik az orvostechinkai eszközökre vonatkozó követelmények?"
# question = translate_openai(question)

# message_objects=[]
# answer_list=[]

# message_objects.append({"role": "system", 
#                         "content": "Egy chatbot vagy, aki dokumentumokra vonatkozó kérdésekre felel magyarul"})
# #print("Object before run: ", message_objects)
# message_objects.append({"role": "user", "content": question})
# pages = query_chroma(question, 1)
# df=pd.DataFrame.from_records(pages['metadatas'])
# for i, doc in enumerate(pages['documents']):
#     # score = 1 - float(prod.vector_score)
#     soup = BeautifulSoup(doc)
#     answer_dict = {'role': "assistant", "content": f"{soup.text}"}
#     answer_list.append(answer_dict)


# # message_objects.append({"role": "assistant", "content": f"Ezt a 3 terméket találtam:"})
# message_objects.extend(answer_list)
# message_objects.append(
#     {"role": "assistant", "content": "Ezt a választ szerkesztettem magyarul:"})

# result = get_recommendation(message_objects)