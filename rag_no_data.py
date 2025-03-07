from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv(override=True)

openai_client = OpenAI()

def get_stock_prices_with_rag_no_data(ticker_symbol):
    prompt = f"""
    Please provide the most recent stock price for {ticker_symbol} in the exact format below:
    The most recent stock price for TICKER was $PRICE.
    Do not provide any extra information, explanation, or guesses.
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,
    )
    
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    start_time = time.time()

    tickers = ["AAPL", "TSLA", "AMZN", "VTI"]
    for ticker in tickers:
        stock_price = get_stock_prices_with_rag_no_data(ticker)
        print(f"{ticker} result: {stock_price}")

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTotal time taken: {total_time:.2f} seconds")
