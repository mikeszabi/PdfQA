import numpy as np
import logging
import os
import openai
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv


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
file_names=[r'./docs/1041-2008_A1-2014_MSZ_EN.pdf']


def query_chroma(query_texts, max_results):

    
    embedding_function = OpenAIEmbeddingFunction(api_key=openai.api_key, model_name=EMBEDDING_MODEL)

    client = chromadb.Client(
        chromadb.config.Settings(
            persist_directory=DB_DIR,
            chroma_db_impl="duckdb+parquet",
        )
    )

    collection = client.get_collection(name=COLLECTION,embedding_function=embedding_function)
    
    results = collection.query(query_texts=query_texts, n_results=max_results, include=['distances'])
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

# def generate_response():

    
#     embeddings = OpenAIEmbeddings()


#     query = "Mi a vonatkozó szabvány?"
#     outp = query_chroma(query,k=3)


#     # chain = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0.3), 
#     #                                               retriever=docsearch.as_retriever(search_kwargs={"k": 1}),
#     #                                               return_source_documents=True)
    
#     # result = chain({"question": query, 'chat_history': []}, return_only_outputs=True)
#     # return chain        

# def main():
#     # init_chromadb()
#     # query_chromadb()


# if __name__ == '__main__':
#     main()