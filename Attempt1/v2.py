import requests
from bs4 import BeautifulSoup

url = 'https://example.com/journal-articles'
response = requests.get(url)
print(response)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all links to PDF articles
pdf_links = soup.find_all('a', href=True)
pdf_urls = [link['href'] for link in pdf_links if link['href'].endswith('.pdf')]

# Download PDFs
for pdf_url in pdf_urls:
    pdf_response = requests.get(pdf_url)
    with open(pdf_url.split('/')[-1], 'wb') as pdf_file:
        pdf_file.write(pdf_response.content)
