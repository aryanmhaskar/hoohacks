

import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from scraper import scrape_article  # Import the scraper function

# Set up the OpenAI API key
API_KEY = "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"
YOUR_API_KEY = API_KEY

app = Flask(__name__)

# Configure CORS for all origins (adjust as needed)
CORS(app, origins=["http://127.0.0.1:5500", "*"])

@app.route("/chat", methods=["POST"])
def format_bias_analysis():
    article_data = request.json
    url = article_data.get("url")
    
    if not url:
        return jsonify({"error": "No article URL provided."}), 400

    # Scrape the article data (authors, title, text) using the scraper function
    article_content = scrape_article(url)
    
    # Check if scraping was successful
    if "error" in article_content:
        return jsonify({"error": article_content["error"]}), 500

    # Prepare the system prompt for AI analysis
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

    All of your outputs will be in the following format, your response to the chat should not have any extraneous words outside of this format ENSURE That every rationale includes quotes from the article that are MULTIPLE SENTENCES long. Find the article links using deep research, do not put fake/dummy links:
    “
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

    # Call the OpenAI API to analyze the scraped article
    try:
        client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")
        
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=[{
                "role": "system",
                "content": system_prompt
            }, {
                "role": "user",
                "content": f"""
                Analyze this article:
                Authors: {article_content['authors']}
                Title: {article_content['title']}
                Text: {article_content['text'][:3000]}...
                """
            }]
        )

        # Parse the response into the structured format
        raw_response = response.choices[0].message.content.strip()

        # Use regex to extract the required data from the raw response
        analysis_data = {
            "politicalBiasScore": None,
            "politicalBiasRationale": None,
            "factualCorrectnessScore": None,
            "factualCorrectnessRationale": None,
            "authorBiasScore": None,
            "authorBiasRationale": None,
            "publishingBiasScore": None,
            "publishingBiasRationale": None,
            "farRightArticle": None,
            "moderateRightArticle": None,
            "neutralArticle": None,
            "moderateLeftArticle": None,
            "farLeftArticle": None
        }

        # Regular expressions to extract each score and rationale
        political_bias_score = re.search(r"Political Bias Score: ([-+]?\d+)", raw_response)
        if political_bias_score:
            analysis_data["politicalBiasScore"] = political_bias_score.group(1)
        
        political_bias_rationale = re.search(r"Rationale: (.*?)Factual Correctness Score:", raw_response, re.DOTALL)
        if political_bias_rationale:
            analysis_data["politicalBiasRationale"] = political_bias_rationale.group(1).strip()

        factual_correctness_score = re.search(r"Factual Correctness Score: ([-+]?\d+)", raw_response)
        if factual_correctness_score:
            analysis_data["factualCorrectnessScore"] = factual_correctness_score.group(1)
        
        factual_correctness_rationale = re.search(r"Rationale: (.*?)Author Political Bias Score:", raw_response, re.DOTALL)
        if factual_correctness_rationale:
            analysis_data["factualCorrectnessRationale"] = factual_correctness_rationale.group(1).strip()

        author_bias_score = re.search(r"Author Political Bias Score: ([-+]?\d+)", raw_response)
        if author_bias_score:
            analysis_data["authorBiasScore"] = author_bias_score.group(1)
        
        author_bias_rationale = re.search(r"Rationale: (.*?)Publishing Site Bias Score:", raw_response, re.DOTALL)
        if author_bias_rationale:
            analysis_data["authorBiasRationale"] = author_bias_rationale.group(1).strip()

        publishing_bias_score = re.search(r"Publishing Site Bias Score: ([-+]?\d+)", raw_response)
        if publishing_bias_score:
            analysis_data["publishingBiasScore"] = publishing_bias_score.group(1)
        
        publishing_bias_rationale = re.search(r"Rationale: (.*?)Far Right Article Recommendation:", raw_response, re.DOTALL)
        if publishing_bias_rationale:
            analysis_data["publishingBiasRationale"] = publishing_bias_rationale.group(1).strip()

        # Extract article recommendations
        far_right_article = re.search(r"Far Right Article Recommendation: (https?://[^\s]+)", raw_response)
        if far_right_article:
            analysis_data["farRightArticle"] = far_right_article.group(1)

        moderate_right_article = re.search(r"Moderate Right Article Recommendation: (https?://[^\s]+)", raw_response)
        if moderate_right_article:
            analysis_data["moderateRightArticle"] = moderate_right_article.group(1)

        neutral_article = re.search(r"Neutral Article Recommendation: (https?://[^\s]+)", raw_response)
        if neutral_article:
            analysis_data["neutralArticle"] = neutral_article.group(1)

        moderate_left_article = re.search(r"Moderate Left Article Recommendation: (https?://[^\s]+)", raw_response)
        if moderate_left_article:
            analysis_data["moderateLeftArticle"] = moderate_left_article.group(1)

        far_left_article = re.search(r"Far Left Article Recommendation: (https?://[^\s]+)", raw_response)
        if far_left_article:
            analysis_data["farLeftArticle"] = far_left_article.group(1)

        # Return the structured response as JSON
        return jsonify({
            "aiResponse": analysis_data
        })

    except Exception as e:
        return jsonify({"error": f"Analysis Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
