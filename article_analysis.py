from secret import API_KEY
from openai import OpenAI
from scraper import scrape_article

YOUR_API_KEY = API_KEY

messages = [
    {
        "role": "system",
        "content": (
            """
You are a bot designed to help users become aware of political bias in the news media. You will receive input data including the title/source of the article, the authors of the article, and the text of the article. Analyze the language of the article, and score it from 10L to 10R where 10L is extremely far left (liberal), 10R is extremely far right (conservative), and 0 is overall neutral article. Analyze the factual correctness of the article and score it from 0 to 10. Assign the authors based on their history and background a score on how much they politically lean. Assign the publishing site a score on political bias based on history. Then recommend articles on the same topic, but from a more diverse array of political bias (let's say the article was very far right leaning, provide a moderate right article, a neutral article, moderate left, and extremely far left).
You will receive inputs in the following format: “
Authors: [Author1, Author 2, Author n]
Title: [Title] 
Text: [Text}
“
All of your outputs will be in the following format, your response to the chat should not have any extraneous words outside of this format: “
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
        ),
    },
    {   
        "role": "user",
        "content": (
            scrape_article("https://www.foxnews.com/us/feds-alert-tesla-global-day-action-after-nationwide-violence-leads-arrests")
        ),
    },
]

client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")

# chat completion without streaming
response = client.chat.completions.create(
    model="sonar-pro",
    messages=messages,
)
print(response)

# chat completion with streaming
response_stream = client.chat.completions.create(
    model="sonar-pro",
    messages=messages,
    stream=True,
)
for response in response_stream:
    print(response)