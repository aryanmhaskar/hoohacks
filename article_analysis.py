from secret import API_KEY
from openai import OpenAI

YOUR_API_KEY = "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"

messages = [
    {
        "role": "system",
        "content": (
            "I am going to give you the text from an article. I will also give you the names of the author(s) of the articles. Figure out where the article was published (FOX, CNN, etc.). Analyze the language of the text of the article- and score it on political bias (10L for extremely left [liberal], 10R for extremely right [conservative]). Analyze the factual correctness of the article and score it 0 to 10. Assign the authors (based on their history and background) a score on how much they politically lean. Assign the publishing site a score on political bias based on history. Provide all these scores individually, provide reasoning with quotes from the article for why the scores were made. Then provide an overall score for the article on how much it is politically biased (and whether it is left or right). Then recommend articles on the same topic, but from a more diverse array of political bias (let's say the article was very far right leaning, provide a moderate right article, a neutral article, moderate left, and extremely far left)."
        ),
    },
    {   
        "role": "user",
        "content": (
            "How many stars are in the universe?"
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