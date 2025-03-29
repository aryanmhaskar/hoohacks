import requests
from newspaper import Article
from bs4 import BeautifulSoup
import random

USER_AGENTS = [
    'Googlebot-News',
    'Googlebot/2.1 (+http://www.google.com/bot.html)',
    'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'
]

ARCHIVE_SERVICES = [
    'https://web.archive.org/save/',
    'https://archive.ph/submit/'
]

def scrape_article(url):
    try:
        # Attempt direct access with search engine user-agent
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 403:
            return handle_paywall(url)
            
        article = Article(url)
        article.download(input_html=response.text)
        article.parse()
        
        return format_output(
            authors=article.authors,
            title=article.title,
            text=article.text
        )
        
    except Exception as e:
        return {'error': str(e)}

def handle_paywall(url):
    try:
        # Try web archives
        for archive in ARCHIVE_SERVICES:
            archived_url = f"{archive}{url}"
            response = requests.get(archived_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return format_output(
                    authors=extract_authors(soup),
                    title=extract_title(soup),
                    text=extract_text(soup)
                )
                
        # Fallback to raw HTML parsing
        response = requests.get(url, headers={'User-Agent': random.choice(USER_AGENTS)})
        soup = BeautifulSoup(response.content, 'html.parser')
        
        return format_output(
            authors=extract_authors(soup),
            title=extract_title(soup),
            text=extract_text(soup)
        )
        
    except Exception as e:
        return {'error': str(e)}

def extract_authors(soup):
    # Common author selectors
    selectors = [
        {'itemprop': 'author'}, 
        {'class': 'byline-author'},
        {'rel': 'author'}
    ]
    for selector in selectors:
        authors = soup.find_all(**selector)
        if authors:
            return [a.get_text(strip=True) for a in authors]
    return []

def extract_title(soup):
    # Extract title from <title> tag or Open Graph metadata
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title['content']:
        return og_title['content']
    
    title_tag = soup.find('title')
    return title_tag.get_text(strip=True) if title_tag else "Unknown Title"

def extract_text(soup):
    # Common content containers
    containers = [
        {'class': 'article-content'},
        {'itemprop': 'articleBody'},
        {'id': 'main-content'}
    ]
    for container in containers:
        content = soup.find(**container)
        if content:
            return content.get_text(strip=True)
    return soup.get_text()

def format_output(authors, title, text):
    # Format the output as requested
    formatted_output = f"""
Authors: {authors}
Title: {title}
Text: {text}
"""
    return formatted_output

# Example Usage
url = "https://www.foxnews.com/us/feds-alert-tesla-global-day-action-after-nationwide-violence-leads-arrests"
result = scrape_article(url)
print(result)