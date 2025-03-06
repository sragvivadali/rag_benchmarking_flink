from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

app = Flask(__name__)
# model = SentenceTransformer("all-MiniLM-L6-v2")
model = SentenceTransformer("BAAI/bge-large-en-v1.5")

# Initialize the Pinecone client
load_dotenv()
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)

# Connect to your existing index
index = pc.Index("vector-db-index")

@app.route("/embed", methods=["POST"])
def embed_text():
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    embedding = model.encode(text).tolist()
    
    # Convert ID to string to ensure it's the correct type for Pinecone
    vector_id = str(data["id"])
    
    # Store in Pinecone with string ID
    index.upsert(vectors=[(vector_id, embedding)])

    return jsonify({"embedding": embedding})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
