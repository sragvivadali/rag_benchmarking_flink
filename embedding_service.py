from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import os
from pinecone import Pinecone
from dotenv import load_dotenv
from datetime import datetime, timezone
import json

app = Flask(__name__)
model = SentenceTransformer("BAAI/bge-large-en-v1.5")

load_dotenv(override=True)
pinecone_api_key = os.getenv("PINECONE_API_KEY")
print(f"Loaded API Key: {pinecone_api_key}")
pc = Pinecone(api_key=pinecone_api_key)

index = pc.Index("vector-db-index")

@app.route("/embed", methods=["POST"])
def embed_text():
    data = request.json
    text = data.get("text", "")

    data_dict = json.loads(text)

    if "timestamp" in data_dict:
        dt_utc = datetime.fromtimestamp(data_dict["timestamp"], tz=timezone.utc)
        data_dict["date_time_utc"] = dt_utc.isoformat()

    text = json.dumps(data_dict, indent=4)

    print(text)

    if not text:
        return jsonify({"error": "No text provided"}), 400

    embedding = model.encode(text).tolist()
    
    vector_id = str(data["id"])
    
    metadata = {
        "text": text
    }

    response = index.upsert(
        vectors=[
            {
                "id": vector_id, 
                "values": embedding, 
                "metadata": metadata
            }
        ],
    )

    return jsonify({"embedding": embedding})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)