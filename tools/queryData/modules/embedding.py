import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

# from langchain_chroma import Chroma
# from langchain_openai import OpenAIEmbeddings

# # Load your documents and create embeddings
# documents = ['a','b','c']  # Load your documents here
# embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
# print(embeddings)

# # Create the vector store
# vector_store = Chroma.from_documents(documents, embeddings)

# vector_store.add_documents(documents)

# results = vector_store.similarity_search("your query here")


client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_embedding_openai(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding

def cosine_similarity(vec1, vec2):
    """Calculate the cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# def create_chroma_vector_store():
#     print('build a vector')


