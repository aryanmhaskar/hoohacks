import joblib

# Load the trained model
model = joblib.load("political_bias_classifier.pkl")

def predict_bias(text):
    prediction = model.predict([text])[0]
    return prediction

# Example Usage
article = "The new policies focus on healthcare and climate reform."
print("Predicted Bias:", predict_bias(article))