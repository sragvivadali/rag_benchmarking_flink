from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# Load the Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

app = FastAPI()

class TextRequest(BaseModel):
    text: str

@app.post("/embed")
async def generate_embedding(request: TextRequest):
    try:
        embedding = model.encode(request.text).tolist()
        return {"embedding": embedding}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))