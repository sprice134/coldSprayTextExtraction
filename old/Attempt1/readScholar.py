import scholarly

# Define search query
search_query = scholarly.search_pubs("cold spray additive manufacturing yield strength modulus")

# Loop through search results and download metadata
for i in range(5):
    pub = next(search_query)
    print(pub.bib['title'])
    # Use the DOI or URL to download the article if accessible

'''
from scholarly import scholarly

search_query = scholarly.search_pubs("cold spray additive manufacturing yield strength modulus")
# scholarly.pprint(next(search_query))
article = next(search_query)
articleBib = scholarly.bibtex(article)

print(article)
print(articleBib)
item = {'itemType': 'journalArticle'}
try:
    item['title'] = article['bib']['title']
except:
    print('title')
try:
    item['creators'] = [{'creatorType': 'author', 'firstName': a.split(' ')[0], 'lastName': ' '.join(a.split(' ')[1:])} for a in article['bib']['author']],
except:
    print('creator')
try:
    item['abstract'] = article['bib']['abstract']
except:
    print('abstract')
try:
    item['date'] = article['bib']['pub_year']
except:
    print('pub_year')
# try:
#     item['journal'] = articleBib['journal']
# except:
#     print('journal')
# try:
#     item['publisher'] = articleBib['publisher']
# except:
#     print('publisher')





# from scholarly import scholarly
# import requests
# from bs4 import BeautifulSoup
# import os

# # Define the directory to save the PDFs
# save_dir = "cold_spray_papers"
# os.makedirs(save_dir, exist_ok=True)

# # Define the search query
# search_query = scholarly.search_pubs("cold spray additive manufacturing yield strength modulus")

# # Loop through search results and download metadata and PDFs
# for i in range(2):
#     try:
#         pub = next(search_query)
#         print(pub)
#         title = pub['bib']['title']
#         url = pub['eprint_url']
#         print(url)
#         if url:
#             response = requests.get(url)
#             soup = BeautifulSoup(response.content, 'html.parser')
            
#             # Example for a PDF link in an anchor tag
#             pdf_link = soup.find('a', href=True, text='PDF')
#             if pdf_link:
#                 pdf_url = pdf_link['href']
#                 pdf_response = requests.get(pdf_url)
                
#                 # Save the PDF
#                 pdf_path = os.path.join(save_dir, f"{title[:50]}.pdf")  # Limiting title length for filename
#                 with open(pdf_path, 'wb') as f:
#                     f.write(pdf_response.content)
#                 print(f"Downloaded: {title}")
#             else:
#                 print(f"No PDF found for: {title}")
#         else:
#             print(f"No URL found for: {title}")
#     except StopIteration:
#         print("No more articles found")
#         break
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         continue
'''