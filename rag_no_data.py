from openai import OpenAI
from dotenv import load_dotenv

"""
Create a .env file with OPENAI_API_KEY=your-api-key for the code below to work.
"""

load_dotenv()

def get_stock_prices():
    # Initialize the client
    client = OpenAI()

    # available_models = client.models.list()
    # for model in available_models:
    #     print(model.id)
    
    # Define the query
    query = "Give me only the current stock prices for Apple, Amazon, Tesla, and VTI as numbers, no additional text. Make a possible guess even if you do not have access to real-time stock prices."
    
    # Request completion using the chat completions endpoint
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": query}
        ],
        temperature=0,
    )
    
    # Parse the response
    return response.choices[0].message.content.strip()

# Get stock prices
stock_prices = get_stock_prices()
print(stock_prices)