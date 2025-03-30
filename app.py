from flask import Flask, request, render_template, redirect, url_for
import scraper  # Import your scraper.py module

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Your submission page

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form['url']  # Get the URL from the form
    result = scraper.scrape_article(url)  # Scrape the article
    
    if 'error' in result:
        return render_template('analyze.html', error=result['error'])
    
    # Pass scraped data to the analyze.html template
    return render_template('analyze.html', 
                      authors=result.get('authors'),
                      title=result.get('title'),
                      text=result.get('text'),
                      political_bias=result.get('political_bias'),
                      factual_correctness=result.get('factual_correctness'),
                      author_bias=result.get('author_bias'),
                      publishing_bias=result.get('publishing_bias'),
                      publication_name=result.get('publication_name'))


if __name__ == '__main__':
    app.run(debug=True)