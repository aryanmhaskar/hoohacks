from secret import API_KEY
from openai import OpenAI
from scraper import scrape_article
import re

YOUR_API_KEY = API_KEY

def format_bias_analysis(article_data):
    client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")
    
    system_prompt = """Analyze news articles using these methodologies:
1. Bias Scoring (-42 to +42 scale from Ad Fontes Media)
2. Factual Reliability (0-64 scale from Media Bias Chart)
3. Author Bias History (AllSides Media methodology)
4. Publisher Bias Rating (Ground News aggregation)

For each score, include 2-3 direct quotes from the text supporting the assessment. Recommend alternative articles using these sources:
- Far Right: Breitbart, Daily Wire
- Moderate Right: Wall Street Journal, The Hill
- Neutral: Reuters, Associated Press
- Moderate Left: NPR, Washington Post
- Far Left: Jacobin, The Intercept"""

    try:
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"""
                    Analyze this article:
                    Authors: {article_data['authors']}
                    Title: {article_data['title']}
                    Text: {article_data['text'][:3000]}...
                    """
                }
            ]
        )
        print(response)
        print(response.choices[0].message.content)
        return parse_response(response.choices[0].message.content)
    
    except Exception as e:
        return f"Analysis Error: {str(e)}"

def parse_response(response_text):
    pattern = r"""
    Political\sBias\sScore:\s*(-?\d+\.?\d*)
    Rationale:\s*(.*?)
    Factual\sCorrectness\sScore:\s*(\d+\.?\d*)
    Rationale:\s*(.*?)
    Author\sPolitical\sBias\sScore:\s*(-?\d+\.?\d*)
    Rationale:\s*(.*?)
    Publishing\sSite\sBias\sScore:\s*(-?\d+\.?\d*)
    Rationale:\s*(.*?)
    Far\sRight\sArticle\sRecommendation:\s*(.*?)
    Moderate\sRight\sArticle\sRecommendation:\s*(.*?)
    Neutral\sArticle\sRecommendation:\s*(.*?)
    Moderate\sLeft\sArticle\sRecommendation:\s*(.*?)
    Far\sLeft\sArticle\sRecommendation:\s*(.*?)
    """
    
    match = re.search(pattern, response_text, re.DOTALL|re.VERBOSE)
    
    if not match:
        return "Failed to parse analysis response"
    
    return {
        "Political Bias Score": float(match.group(1)),
        "Factual Correctness Score": float(match.group(3)),
        "Author Bias Score": float(match.group(5)),
        "Publisher Bias Score": float(match.group(7)),
        "Recommendations": {
            "Far Right": match.group(9).strip(),
            "Moderate Right": match.group(10).strip(),
            "Neutral": match.group(11).strip(),
            "Moderate Left": match.group(12).strip(),
            "Far Left": match.group(13).strip()
        }
    }

# Example usage
article_data = scrape_article("https://www.foxnews.com/us/feds-alert-tesla-global-day-action-after-nationwide-violence-leads-arrests")
print(article_data)
analysis = format_bias_analysis(article_data)
print(analysis)