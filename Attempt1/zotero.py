from scholarly import scholarly
from pyzotero import zotero

# Your Zotero API credentials
ZOTERO_USER_ID = 'sprice134'
ZOTERO_API_KEY = '14509860'
LIBRARY_TYPE = 'user'  # could be 'group' if using group library

# Initialize Zotero client
zot = zotero.Zotero(ZOTERO_USER_ID, LIBRARY_TYPE, ZOTERO_API_KEY)

# Search query
query = 'cold spray yield strength modulus speed3D'

# Perform the search
search_results = scholarly.search_pubs(query)

# Retrieve the top 50 results
articles = []
for i, result in enumerate(search_results):
    if i >= 50:
        break
    articles.append(result)

# Add articles to Zotero
for i, article in enumerate(articles, start=1):
    # Prepare the item data
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
    # Add the item to Zotero
    zot.create_items([item])

print("Articles added to Zotero")
