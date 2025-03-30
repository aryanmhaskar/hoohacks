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
    1. Bias Scoring (-42 to +42 scale from Ad Fontes Media, ensure the sign is used and left is in the negative range)
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
    Author: [Rationale]
    Article: [Article Text]
    “

    Split responses with "--SPLIT--", for example: Political Bias Score: -10--SPLIT--Rationale: The article presents a relatively balanced view of the issue, but leans slightly left in its framing. For example, it states "School used to be lauded as the best days of our lives — but those in Year 12 feel more like they're in a relentless competition that only the strongest can survive." This framing suggests criticism of the current educational system and competition, which aligns more with left-leaning perspectives. The author also expresses concern about the pressure on students, stating "When I talk to teens about how they feel about their final years of schooling, I can't help but think something, somewhere, has gone terribly wrong."--SPLIT--Factual Correctness Score: 50--SPLIT--...etc
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
            "farLeftArticle": None,
            "author": None,
            "article": None
        }

        print(raw_response)
        split_response = raw_response.split("--SPLIT--")
        print(split_response)

        # Adjusted regex to properly separate the sections and capture each section without overlapping
        political_bias_score = split_response[0]
        if political_bias_score:
            analysis_data["politicalBiasScore"] = political_bias_score
        
        political_bias_rationale = split_response[1]
        if political_bias_rationale:
            analysis_data["politicalBiasRationale"] = political_bias_rationale

        factual_correctness_score = split_response[2]
        if factual_correctness_score:
            analysis_data["factualCorrectnessScore"] = factual_correctness_score
        
        factual_correctness_rationale = split_response[3]
        if factual_correctness_rationale:
            analysis_data["factualCorrectnessRationale"] = factual_correctness_rationale

        author_bias_score = split_response[4]
        if author_bias_score:
            analysis_data["authorBiasScore"] = author_bias_score
        
        author_bias_rationale = split_response[5]
        if author_bias_rationale:
            analysis_data["authorBiasRationale"] = author_bias_rationale

        publishing_bias_score = split_response[6]
        if publishing_bias_score:
            analysis_data["publishingBiasScore"] = publishing_bias_score
        
        publishing_bias_rationale = split_response[7]
        if publishing_bias_rationale:
            analysis_data["publishingBiasRationale"] = publishing_bias_rationale

        if publishing_bias_rationale:
            analysis_data["author"] = article_content['authors']

        article = split_response[14]
        if publishing_bias_rationale:
            analysis_data["article"] = article

        # # Extract article recommendations
        # far_right_article = re.search(r"Far Right Article Recommendation: (https?://[^\s]+)", raw_response)
        # if far_right_article:
        #     analysis_data["farRightArticle"] = far_right_article.group(1)

        # moderate_right_article = re.search(r"Moderate Right Article Recommendation: (https?://[^\s]+)", raw_response)
        # if moderate_right_article:
        #     analysis_data["moderateRightArticle"] = moderate_right_article.group(1)

        # neutral_article = re.search(r"Neutral Article Recommendation: (https?://[^\s]+)", raw_response)
        # if neutral_article:
        #     analysis_data["neutralArticle"] = neutral_article.group(1)

        # moderate_left_article = re.search(r"Moderate Left Article Recommendation: (https?://[^\s]+)", raw_response)
        # if moderate_left_article:
        #     analysis_data["moderateLeftArticle"] = moderate_left_article.group(1)

        # far_left_article = re.search(r"Far Left Article Recommendation: (https?://[^\s]+)", raw_response)
        # if far_left_article:
        #     analysis_data["farLeftArticle"] = far_left_article.group(1)

        # Return the structured response as JSON
        return jsonify({
            "aiResponse": analysis_data
        })

    except Exception as e:
        return jsonify({"error": f"Analysis Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
