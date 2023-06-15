# -*- coding: utf-8 -*-
"""
Created on Wed May 31 17:06:58 2023

@author: Szabi
"""

################search
import os
import re
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
import openai
import translator
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

load_dotenv(r'./.env')

openai.api_type = "azure"
openai.api_key = os.getenv('PREFIX_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('PREFIX_AZURE_API_BASE')
openai.api_version = os.getenv('PREFIX_AZURE_API_VERSION')

initial_message_objects={}
initial_message_objects['Document']={"role": "system", 
                        "content": "Egy chatbot vagy, aki dokumentumokra vonatkozó kérdésekre felel magyarul"}

EMBEDDING_MODEL = "text-embedding-ada-002"
ABS_PATH = r'.' #os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(ABS_PATH, "db") # persistent directory
COLLECTION='guides'

class Search:
    def __init__(self):
        # API parameters
        
        self.search_history=[]
        self.embedding_function = OpenAIEmbeddingFunction(api_key=openai.api_key, model_name=EMBEDDING_MODEL)

        
        self.search_history=[]
        
        self.client = chromadb.Client(
            chromadb.config.Settings(
                persist_directory=DB_DIR,
                chroma_db_impl="duckdb+parquet",
            )
        )

        self.collection = self.client.get_collection(name=COLLECTION,embedding_function=self.embedding_function)
        

    
    # def __del__(self):
    #     self.conn.close()
 

    def get_topk_related_product(self,question,max_results):
        # The main seacrh function
        print("Searching for similar documents...")
        query_texts_en=translator.translate_openai(question)
        
        search_item={}
        search_item['question']=question
  
        
        results = self.collection.query(query_texts=query_texts_en, n_results=max_results, include=['distances'])
        pages= self.collection.get(results['ids'][0])

        search_item['documents_found']=pages['documents']
        search_item['meta']=pages['metadatas']

        # for doc, meta in zip(pages['documents'],pages['metadatas']):
        #     # score = 1 - float(prod.vector_score)
        #     #soup = BeautifulSoup(doc)
        #     # answer_dict = {'role': "assistant", "content": f"{soup.text}"}
        #     # answer_list.append(answer_dict)
        
        #     search_item['text'].append(doc)
        #     search_item['source'].append(meta['source'])
        #     search_item['page'].append(meta['page'])
       
       
        self.search_history.append(search_item)
        return search_item
            
class Recommend():
    def __init__(self):
        self.initial_message_object=initial_message_objects['Document']

        self.questions=[]
        self.message_objects=[]
        self.message_objects.append(self.initial_message_object)
        # self.search_history=[]
        
    def clear_messages(self):
        self.message_objects = []
        self.initial_message_object=self.initial_message_object
    
    # def trim_messages(self,max_l=10):
    #     message_objects_trimmed=self.message_objects[len(self.message_objects)-max_l:]
    #     self.message_objects = []
    #     self.message_objects.append(self.initial_message_object)
    #     self.message_objects.extend(message_objects_trimmed)
        
    def append_message(self,new_message_object):
        self.message_objects.append(new_message_object)
        
    def append_products(self,search_item,max_prod=3):
        document_list=[]
        meta_list=[]
        i=0
        for doc, meta in zip(search_item['documents_found'],search_item['meta']):
       
            soup = BeautifulSoup(doc)
            new_message_object={'role': "assistant", "content": f"{soup.text}"}
            self.append_message(new_message_object)


            document_list.append(new_message_object)
            meta_list.append({'source':meta['source'],'page':meta['page']})
            i+=1
            # self.search_history.append(search_item)
            
            
        return document_list, meta_list
        

    def get_recommendation(self,language='Hungarian',max_message=10):
        completion = openai.ChatCompletion.create(
            engine="gpt-35-turbo-deployment",
            messages=self.message_objects[-max_message:]
        )
        comp_text=completion.choices[0].message['content']
        if language=='English':
            comp_text=translator.translate_openai(comp_text)
        return comp_text