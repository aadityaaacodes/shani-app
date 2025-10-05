import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import pandas as pd
import json, csv


chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="semanticSentences")

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
def generate_embedding(text):
    return model.encode(text).tolist()  # convert to list for Chroma

# Load sentences

def load():
    df = pd.read_csv('semantic_chunks.csv')
    batch_size = 5000
    total_rows = len(df)
    # print(total_rows)
    c = 0
    while (c<=total_rows+1):
        batch_df = df.iloc[c:c + batch_size]
        sentences = batch_df['chunk'].tolist()
        # print(sentences)
        makeDB(sentences=sentences)
        c+=batch_size
        print(c)


def makeDB(sentences):
    ids = [f"id_{i+1}" for i in range(len(sentences))]
    vectors = [generate_embedding(s) for s in sentences]

    collection.upsert(
        ids=ids,
        documents=sentences,
        embeddings=vectors
    )

    items = collection.get(
        include=["metadatas", "documents", "embeddings"]
    )

    items["embeddings"] = [embedding.tolist() for embedding in items["embeddings"]]
    with open("sentence_vectors.json", "w") as f:
        json.dump(items, f, indent=4)


def storeDB():
    with open("sentence_vectors.json", "r") as f:
        data = json.load(f)

    # Open CSV file to write
    with open("data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        
    metadata_keys = set()
    for meta in data.get("metadatas", []):
        if meta:
            metadata_keys.update(meta.keys())
    metadata_keys = list(metadata_keys)

    # Open CSV to write
    with open("data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        
        # Write header
        header = ["id", "document", "embedding"] + metadata_keys
        writer.writerow(header)
        
        # Write rows
        for i in range(len(data["ids"])):
            meta = data.get("metadatas", [None]*len(data["ids"]))[i] or {}
            row = [
                data["ids"][i],
                data.get("documents", [None]*len(data["ids"]))[i],
                data["embeddings"][i]
            ] + [meta.get(k, "") for k in metadata_keys]
            writer.writerow(row)


def makeQuery(query, top_k=5):
    with open("sentence_vectors.json", "r") as f:
        data = json.load(f)

    collection.add(
        ids=data["ids"],
        documents=data["documents"],
        embeddings=data["embeddings"]
    )

    embedded_query = [generate_embedding(query)]
    results = collection.query(
        query_embeddings=embedded_query,
        n_results=top_k
    )

    print("Top similar sentences:")
    for doc in results['documents'][0]:
        print("-", doc)

# Usage
# makeDB()
# storeDB()
# makeQuery("Autism is a spectrum.")

load()