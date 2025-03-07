from openai import OpenAI
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os
import time
from datetime import datetime, timezone

load_dotenv(override=True)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

openai_client = OpenAI()

def get_stock_prices_with_rag(ticker_symbol): 
    model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index("vector-db-index")
    
    timestamp = int(datetime.now(timezone.utc).timestamp()) - (15 * 60)
    dt_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc)

    # date = datetime.fromtimestamp(timestamp, tz=timezone.utc).date()

    query = f"What is the current stock price of {ticker_symbol} at date_time_utc {dt_utc}?"
    query_embedding = model.encode(query).tolist()
    
    # Search Pinecone for relevant documents
    search_results = index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True
    )

    # Extract contexts from search results
    contexts = []
    for result in search_results.matches:
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
    start_time = time.time()

    tickers = ["AAPL", "TSLA", "AMZN", "VTI"]
    for ticker in tickers:
        stock_price = get_stock_prices_with_rag(ticker)
        print(f"{ticker} result: {stock_price}")

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTotal time taken: {total_time:.2f} seconds")