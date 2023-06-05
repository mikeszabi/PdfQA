# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 09:08:17 2023

@author: Szabi
"""

import logging
import os
import openai
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
import time

load_dotenv(r'.env')

openai.api_type = "azure"
openai.api_key = os.getenv('PREFIX_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('PREFIX_AZURE_API_BASE')
openai.api_version = os.getenv('PREFIX_AZURE_API_VERSION')


# load_dotenv()
logging.basicConfig(level=logging.DEBUG)


EMBEDDING_MODEL = "text-embedding-ada-002"
ABS_PATH = r'.' #os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(ABS_PATH, "db")
COLLECTION='standards'
FILE_DIR=r'./docs'
#file_names=[r'./docs/1041-2008_A1-2014_MSZ_EN.pdf']


def populate_chromadb(file_names):
    # https://github.com/openai/openai-cookbook/blob/main/examples/vector_databases/Using_vector_databases_for_embeddings_search.ipynb

    persist_directory = 'db' # Directory to store persisted Chroma data. 
    client = chromadb.Client(
        chromadb.config.Settings(
            persist_directory=persist_directory,
            chroma_db_impl="duckdb+parquet",
        )
    )
    embedding_function = OpenAIEmbeddingFunction(api_key=openai.api_key, model_name=EMBEDDING_MODEL)

    collection = client.create_collection(name=COLLECTION,embedding_function=embedding_function)
    
    id=0
    for file_name in file_names:
        loader = PyPDFLoader(file_name)
        pages = loader.load_and_split()
        #print(pages[0].page_content)
    
        for page in pages:
            id+=1
            content=page.page_content.replace("\n", "")
            collection.add(
                documents=[content], # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
                metadatas=[page.metadata], # filter on these!
                #embeddings=[content],
                ids=[str(id)]) # unique for each doc
            time.sleep(1)
            
def main():
    file_names = [os.path.join(FILE_DIR,f) for f in os.listdir(FILE_DIR) if f.lower().endswith('.pdf')]
    populate_chromadb(file_names)

# if __name__ == '__main__':
#     main()