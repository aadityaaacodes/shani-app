import chromadb
from sentence_transformers import SentenceTransformer
import json

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="semanticSentences")

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
def generate_embedding(text):
    return(model.encode(text))

with open("dataChunks.json", "r") as file:
        sentences = json.load(file)
        sentences=sentences[:20]

def makeVectors():
    vectors = [generate_embedding(sentence) for sentence in sentences]
    ids = [f"id_{i+1}" for i in range(len(sentences))]
    return(vectors, ids)


def makeDB():
    sentence_vectors, sentence_ids = makeVectors()

    collection.upsert(
        ids=sentence_ids,
        documents=sentences, 
        embeddings=sentence_vectors
    )

    items = collection.get(
        include=["metadatas", "documents", "embeddings"]
    )

    items["embeddings"] = [embedding.tolist() for embedding in items["embeddings"]]
    with open("sentence_vectors.json", "w") as f:
        json.dump(items, f, indent=4)


def makeQuery(query):
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
        n_results=5
    )
    print("Top 5 similar sentences:")
    # print(results)
    for doc in results['documents'][0]:
        print("-", doc)


makeQuery(query = "Russia is unsafe.")


# makeVectors()


# makeDB()