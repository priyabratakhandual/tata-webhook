import pandas as pd
import pandas as pd
from llama_index.embeddings.ollama import OllamaEmbedding
import faiss
import numpy as np
import os

index_dir = "all_data"
path = os.getcwd()+"/"+index_dir
# Initialize OllamaEmbedding
ollama_embedding = OllamaEmbedding(
    model_name="nomic-embed-text:latest",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0},
)

# Dimensions of the embedding model
embedding_dim = 768


# Load the DataFrame from the pickle file
df_service = pd.read_pickle(f"{path}/df-data/service_dataframe.pkl")
df_sales = pd.read_pickle(f"{path}/df-data/sales_dataframe.pkl")
# Load the saved FAISS index
faiss_index_service = faiss.read_index(f"{path}/service_faiss_index.bin")
faiss_index_sales = faiss.read_index(f"{path}/sales_faiss_index.bin")
loaded_metadata_sales = pd.read_pickle(f"{path}/df-data/sales_metadata.pkl")
loaded_metadata_service = pd.read_pickle(f"{path}/df-data/service_metadata.pkl")


# loaded_vector_store = FaissVectorStore(faiss_index=faiss_index)
print("FAISS index loaded successfully")

# Function to create FAISS index based on Module and Sub Module
def create_faiss_index_by_module_submodule(df, submodule=None, issuecategory=None):
    # Filter DataFrame based on Module and Sub Module
    if submodule and issuecategory:
        filtered_df = df[(df['Sub-Module'] == submodule) & (df['Issue Category'] == issuecategory)]
    elif submodule and issuecategory==None:
        filtered_df = df[(df['Sub-Module'] == submodule)]        
    
    if filtered_df.empty:
        print(f"No data found for Module: {submodule} and Sub Module: {issuecategory}")
        return None, None

    # Extract the embeddings (convert them into a NumPy array)
    embeddings = np.vstack(filtered_df['embedding'].values).astype("float32")

    # Initialize the FAISS index
    embedding_dim = embeddings.shape[1]  # Assuming all embeddings have the same dimension
    faiss_index = faiss.IndexFlatL2(embedding_dim)

    # Add embeddings to the FAISS index
    faiss_index.add(embeddings)
    # Store metadata
    metadata = filtered_df.to_dict(orient='records')

    return metadata, faiss_index

def get_most_similar(faiss_index,text,k_=10):
    query_embedding = ollama_embedding.get_query_embedding(text)
    query_embedding_np = np.array(query_embedding, dtype="float32")[np.newaxis, :]
    # print(query_embedding)
    distances, indices = faiss_index.search(query_embedding_np, k=k_)

    
    # Set the maximum distance threshold
    max_distance_threshold = 350
    
    # Filter results based on the distance threshold
    filtered_distances = []
    filtered_indices = []

    if distances[0][0] > max_distance_threshold:
        print("No similar Issue found")
    else:    
        for dist, idx in zip(distances[0], indices[0]):
            if dist > max_distance_threshold:
                break  # Stop iterating as distances are sorted
            filtered_distances.append(dist)
            filtered_indices.append(idx)    
    return filtered_distances,filtered_indices
 
def get_answer(module_name, question,submodule=None, issuecategory=None):   

    if module_name == "service":
        faiss_index = faiss_index_service
        df = df_service
        metadata = loaded_metadata_service
    elif module_name == "sales":
        faiss_index = faiss_index_sales
        df = df_sales
        metadata = loaded_metadata_sales
    
    if submodule or issuecategory:
        metadata, faiss_index = create_faiss_index_by_module_submodule(df=df, submodule=submodule, issuecategory=issuecategory)    

    distances, indices = get_most_similar(faiss_index=faiss_index,text=question,k_=10)  
    print(distances)
    print(indices)

    if not indices:
        return None
    else:
        nearest_data = {}

        for j,i in enumerate(indices):
            data = metadata[i]
            print(data['Sub-Module'])
            print(data['Issue Category'])
            print(data['Issue'])
            print(data['Resolution/Escalation'])
            print("\n \n")

            nearest_data[str(j)] = {
                "Issue": data['Issue'],
                "Resolution/Escalation": data['Resolution/Escalation']
            }
        
        return nearest_data
    


def get_submodule(module,submodule=None, issuecategory=None):
    if module == "service":
        df = df_service
        cat_list = df["Sub-Module"].unique()
    elif module == "sales":
        df = df_sales
        cat_list = df["Sub-Module"].unique()
    
    if submodule:
        cat_list = df[df["Sub-Module"] == submodule]["Issue Category"].unique()
        if issuecategory:
            cat_list = df[(df["Sub-Module"] == submodule) & (df["Issue Category"] == issuecategory)]["Issue"].unique()
    return cat_list


    



