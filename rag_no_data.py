from openai import OpenAI
from dotenv import load_dotenv
import time
import requests
import re
import psutil
import statistics
import os

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

def fetch_stock_data(symbol, api_token="demo"):
    url = f"https://eodhd.com/api/real-time/{symbol}?api_token={api_token}&fmt=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("close")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stock data for {symbol}: {e}")
        return None

def extract_price(text):
    match = re.search(r"\$([\d,]+\.\d+)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None

def get_cpu_usage():
    return psutil.cpu_percent(interval=0.1)

def get_memory_usage():
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)

if __name__ == "__main__":
    tickers = ["AAPL.US", "TSLA.US", "AMZN.US", "VTI.US"]

    total_time = 0
    total_percentage_error = 0
    num_iterations = 5
    
    cpu_readings = []
    memory_readings_mb = []
    
    print(f"{'Iteration':<10}{'Ticker':<10}{'LLM Price':<15}{'Real Price':<15}{'Diff':<15}{'Error %':<10}{'CPU %':<10}{'Memory (MB)':<12}")
    print("-" * 100)

    for i in range(num_iterations):
        iteration_start = time.time()
        print(f"\nIteration {i+1}:")
        
        iteration_percentage_error = 0
        iteration_cpu_readings = []
        iteration_memory_readings = []
        
        for ticker in tickers:
            cpu_before = get_cpu_usage()
            memory_before = get_memory_usage()
            
            rag_statement = get_stock_prices_with_rag_no_data(ticker)
            rag_stock_price = extract_price(rag_statement)
            real_stock_price = fetch_stock_data(ticker)
            
            cpu_after = get_cpu_usage()
            memory_after = get_memory_usage()
            
            avg_cpu = (cpu_before + cpu_after) / 2
            avg_memory = (memory_before + memory_after) / 2
            
            iteration_cpu_readings.append(avg_cpu)
            iteration_memory_readings.append(avg_memory)
            cpu_readings.append(avg_cpu)
            memory_readings_mb.append(avg_memory)

            price_diff = abs(rag_stock_price - real_stock_price)
            percentage_error = (price_diff / real_stock_price) * 100

            iteration_percentage_error += percentage_error

            print(f"{i+1:<10}{ticker:<10}${rag_stock_price:<13.2f}${real_stock_price:<13.2f}"
                  f"${price_diff:<13.2f}{percentage_error:<10.2f}{avg_cpu:<10.2f}{avg_memory:<12.2f}")
        
        iteration_end = time.time()
        iteration_time = iteration_end - iteration_start
        total_time += iteration_time
        total_percentage_error += (iteration_percentage_error / len(tickers))

        avg_iteration_cpu = statistics.mean(iteration_cpu_readings)
        avg_iteration_memory = statistics.mean(iteration_memory_readings)
        
        print(f"\nIteration {i+1} Summary:")
        print(f"Time: {iteration_time:.2f} seconds")
        print(f"Avg Percent Diff: {iteration_percentage_error / len(tickers):.2f}%")
        print(f"Avg CPU Usage: {avg_iteration_cpu:.2f}%")
        print(f"Avg Memory Usage: {avg_iteration_memory:.2f} MB")

    avg_time_per_iteration = total_time / num_iterations
    avg_percent_diff = total_percentage_error / num_iterations
    avg_cpu_usage = statistics.mean(cpu_readings)
    avg_memory_usage = statistics.mean(memory_readings_mb)
    max_cpu_usage = max(cpu_readings)
    max_memory_usage = max(memory_readings_mb)

    print(f"\n{'='*50}")
    print(f"BENCHMARK SUMMARY")
    print(f"{'='*50}")
    print(f"Total time taken: {total_time:.2f} seconds")
    print(f"Average time per iteration: {avg_time_per_iteration:.2f} seconds")
    print(f"Overall average percent difference: {avg_percent_diff:.2f}%")
    print(f"\nCPU USAGE STATS:")
    print(f"Average CPU Usage: {avg_cpu_usage:.2f}%")
    print(f"Maximum CPU Usage: {max_cpu_usage:.2f}%")
    print(f"\nMEMORY USAGE STATS:")
    print(f"Average Memory Usage: {avg_memory_usage:.2f} MB")
    print(f"Maximum Memory Usage: {max_memory_usage:.2f} MB")