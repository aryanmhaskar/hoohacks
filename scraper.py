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
        
        return {
            'authors': article.authors,
            'publisher': extract_publisher(url, response.text),
            'text': article.text,
            'bypass_method': 'Direct access'
        }
        
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
                return {
                    'authors': extract_authors(soup),
                    'publisher': extract_publisher(url, response.text),
                    'text': extract_text(soup),
                    'bypass_method': f'Archive: {archive}'
                }
                
        # Fallback to raw HTML parsing
        response = requests.get(url, headers={'User-Agent': random.choice(USER_AGENTS)})
        soup = BeautifulSoup(response.content, 'html.parser')
        
        return {
            'authors': extract_authors(soup),
            'publisher': extract_publisher(url, response.text),
            'text': extract_text(soup),
            'bypass_method': 'HTML parsing fallback'
        }
        
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

def extract_publisher(url, html):
    # Get from Open Graph or domain name
    soup = BeautifulSoup(html, 'html.parser')
    og_publisher = soup.find('meta', property='og:site_name')
    return og_publisher['content'] if og_publisher else url.split('//')[-1].split('/')[0]

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

result = scrape_article('https://www.foxnews.com/us/feds-alert-tesla-global-day-action-after-nationwide-violence-leads-arrests')
print(result)