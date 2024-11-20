import pandas as pd
import pandas as pd
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss
import numpy as np


# Load the DataFrame from the pickle file
df = pd.read_pickle("dataframe.pkl")


# Initialize OllamaEmbedding
ollama_embedding = OllamaEmbedding(
    model_name="nomic-embed-text:latest",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0},
)

# Dimensions of the embedding model
embedding_dim = 768

# Load the saved FAISS index
faiss_index = faiss.read_index("faiss_index.bin")
# loaded_vector_store = FaissVectorStore(faiss_index=faiss_index)
print("FAISS index loaded successfully")


def get_most_similar(text,k_=1):
    query_embedding = ollama_embedding.get_query_embedding(text)
    query_embedding_np = np.array(query_embedding, dtype="float32")[np.newaxis, :]
    # print(query_embedding)
    distances, indices = faiss_index.search(query_embedding_np, k=k_)
    return distances, indices

 
def get_answer(question):
    distances, indices = get_most_similar(question,k_=1)    
    most_sim = indices[0][0]    
    answer = df.iloc[most_sim]["Response_html"]
    query = df.iloc[most_sim]["Issue"]
    # print(answer)
    return query,answer


