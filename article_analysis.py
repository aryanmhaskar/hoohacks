from openai import OpenAI
from scraper import scrape_article

API_KEY = "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"
YOUR_API_KEY = API_KEY

def format_bias_analysis(article_data):
    client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")
    
    system_prompt = """Analyze news articles using these methodologies:
1. Bias Scoring (-42 to +42 scale from Ad Fontes Media)
2. Factual Reliability (0-64 scale from Media Bias Chart)
3. Author Bias History (AllSides Media methodology)
4. Publisher Bias Rating (Ground News aggregation)

For each score, include 2-3 direct quotes (each one being 3 sentences long) from the text supporting the assessment. Recommend alternative articles using these sources:
- Far Right: Breitbart, Daily Wire
- Moderate Right: Wall Street Journal, The Hill
- Neutral: Reuters, Associated Press
- Moderate Left: NPR, Washington Post
- Far Left: Jacobin, The Intercept

All of your outputs will be in the following format, your response to the chat should not have any extraneous words outside of this format ENSURE That every rational includes quotes from the article that are MULTIPLE SENTENCES long. Find the article links using deep research, do not put fake/dummy links: “
Political Bias Score: [Score]
Rationale: [Rationale WITH quotes]
Factual Correctness Score: [Score]
Rationale: [Rationale WITH quotes]
Author Political Bias Score: [Score]
Rationale: [Rationale WITH quotes]
Publishing Site Bias Score: [Score]
Rationale: [Rationale WITH quotes]
Far Right Article Recommendation: [article link]
Moderate Right Article Recommendation: [article link]
Neutral Article Recommendation: [article link]
Moderate Left Article Recommendation: [article link]
Far Left Article Recommendation: [article link]
“

"""

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
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Analysis Error: {str(e)}"

# Example usage
article_data = scrape_article("https://www.foxnews.com/media/seattle-city-councilmember-introduces-resolution-acknowledge-failure-defund-police-movement")
print(article_data)
analysis = format_bias_analysis(article_data)
print(analysis)