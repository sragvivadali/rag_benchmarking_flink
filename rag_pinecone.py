from openai import OpenAI
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os

load_dotenv(override=True)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def get_stock_prices_with_rag(ticker_symbol):
    # Initialize the clients
    openai_client = OpenAI()
    
    # Load the same embedding model as your Flask app
    model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    
    # Initialize Pinecone
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index("vector-db-index")
    
    # Create query embedding
    query = f"What is the current stock price of {ticker_symbol}?"
    query_embedding = model.encode(query).tolist()
    
    # Search Pinecone for relevant documents
    # Add filter to only retrieve documents related to the specific ticker symbol
    search_results = index.query(
        vector=query_embedding,
        top_k=4,
        include_metadata=True
    )

    # Extract contexts from search results
    contexts = []
    for result in search_results.matches:
        # print(result)
        if hasattr(result, 'metadata') and 'text' in result.metadata:
            contexts.append(result.metadata['text'])
    
    # If no matching documents found
    if not contexts:
        return f"No information found for {ticker_symbol} stock price."
    
    # Combine contexts into a single string
    context_text = "\n".join(contexts)
    # print(f"Context found for {ticker_symbol}: {len(contexts)} documents")
    
    # Define the query with context for OpenAI
    prompt = f"""
    Context information about {ticker_symbol} stock prices:
    {context_text}
    
    Based on the above information, what is the current or most recent stock price for {ticker_symbol}? 
    If there are multiple prices mentioned, provide the most recent one.
    Provide answer in the following format: The current price for TIcKER is $PRICE.
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides accurate stock price information based only on the provided context."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
    )
    
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    tickers = ["AAPL", "TSLA", "AMZN", "VTI"]
    for ticker in tickers:
        stock_price = get_stock_prices_with_rag(ticker)
        print(f"{ticker} result: {stock_price}")