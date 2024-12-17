import requests
from googlesearch import search
import os
import time

# Search query
query = "filetype:pdf cold spray yield strength modulus"

# Directory to save the PDFs
save_dir = "cold_spray_pdfs"
os.makedirs(save_dir, exist_ok=True)

# Function to download PDF
def download_pdf(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {save_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

# Function to perform search with rate limiting
def perform_search(query, num_results):
    results = []
    attempt = 0
    max_attempts = 5
    while len(results) < num_results and attempt < max_attempts:
        try:
            new_results = search(query, num_results=num_results - len(results), start=len(results))
            results.extend(new_results)
            time.sleep(2)  # Add delay between searches
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                attempt += 1
                backoff_time = 2 ** attempt
                print(f"Rate limited. Waiting for {backoff_time} seconds.")
                time.sleep(backoff_time)
            else:
                print(f"HTTP error: {e}")
                break
    return results

# Perform the search
num_results = 20
results = perform_search(query, num_results)

# Loop through the search results and download PDFs
for i, url in enumerate(results):
    if url.endswith(".pdf"):
        pdf_path = os.path.join(save_dir, f"document_{i+1}.pdf")
        download_pdf(url, pdf_path)
    else:
        print(f"Skipping non-PDF URL: {url}")

print("Finished downloading PDFs.")
