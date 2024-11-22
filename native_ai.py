import pandas as pd
import pandas as pd
from llama_index.embeddings.ollama import OllamaEmbedding
# from llama_index.vector_stores.faiss import FaissVectorStore
import faiss
import numpy as np
import os


path = os.getcwd()

# Load the DataFrame from the pickle file
df = pd.read_pickle(f"{path}/df-data/service_new_dataframe_2.pkl")


# Initialize OllamaEmbedding
ollama_embedding = OllamaEmbedding(
    model_name="nomic-embed-text:latest",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0},
)

# Dimensions of the embedding model
embedding_dim = 768

# Load the saved FAISS index
faiss_index = faiss.read_index(f"{path}/service_faiss_index.bin")
# loaded_vector_store = FaissVectorStore(faiss_index=faiss_index)
print("FAISS index loaded successfully")


def get_most_similar(text,k_=1):
    query_embedding = ollama_embedding.get_query_embedding(text)
    query_embedding_np = np.array(query_embedding, dtype="float32")[np.newaxis, :]
    # print(query_embedding)
    distances, indices = faiss_index.search(query_embedding_np, k=k_)
    return distances, indices


def get_top_similar(text,k_=3):
    query_embedding = ollama_embedding.get_query_embedding(text)
    query_embedding_np = np.array(query_embedding, dtype="float32")[np.newaxis, :]
    # print(query_embedding)
    distances, indices = faiss_index.search(query_embedding_np, k=k_)
    return distances, indices

 
def get_answer(question):
    distances, indices = get_most_similar(question,k_=1)   
    if min(distances[0]) > 350:
        return None,None 
    most_sim = indices[0][0]    
    answer = df.iloc[most_sim]["html_sol"]
    query = df.iloc[most_sim]["Issue"]
    # print(answer)
    return query,answer


def get_answers_list(question):
    distances, indices = get_most_similar(question,k_=10)    
    most_sim_list = list(indices[0])

    print("Distances:", list(distances[0]))  

    if distances[0][0] > 350:
        answer_list = None
        query_list = None    
    elif distances[0][0] < 50 and distances[0][1] - distances[0][0] > 70:
        answer_list = [df.iloc[most_sim_list[0]]["html_sol"]]
        query_list = [df.iloc[most_sim_list[0]]["Issue"]]    
    else:       
        answer_list = [df.iloc[most_sim]["html_sol"] for most_sim in most_sim_list]
        query_list = [df.iloc[most_sim]["Issue"] for most_sim in most_sim_list]
    # print(answer)
    return answer_list,query_list


