import pandas as pd
import re
import nltk
import joblib
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Download NLTK resources
nltk.download('stopwords')
nltk.download('wordnet')

# Load Dataset
df = pd.read_csv("Political_Bias.csv")

# Debugging: Check if data is loaded properly
print("🔹 First 5 rows of the dataset:\n", df.head())
print("🔹 Column names:", df.columns)

# Ensure correct column names (modify if needed)
expected_columns = ["Bias", "Text"]
if not all(col in df.columns for col in expected_columns):
    print("⚠ Column names might be incorrect! Adjusting...")
    df.columns = expected_columns  # Try renaming columns if they are missing

# Debugging: Check dataset size
print("🔹 Dataset shape before preprocessing:", df.shape)

# Convert labels to 'Democrat' and 'Republican'
def convert_labels(bias):
    bias = str(bias).lower()
    if "left" in bias:
        return "Democrat"
    elif "right" in bias:
        return "Republican"
    return None  # Remove "Center" articles

df["Bias"] = df["Bias"].apply(convert_labels)
df = df.dropna()  # Remove Center articles

# Debugging: Check dataset after label conversion
print("🔹 Dataset shape after label conversion:", df.shape)

# Text Preprocessing
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if pd.isnull(text):  # Handle NaN values
        return ""
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\W+', ' ', text)  # Remove special characters
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return " ".join(words)

df["Processed_Text"] = df["Text"].apply(preprocess_text)

# Debugging: Check if text preprocessing worked
print("🔹 First 5 processed texts:\n", df["Processed_Text"].head())

# Ensure we still have data after preprocessing
if df.empty:
    raise ValueError("❌ ERROR: Dataset is empty after preprocessing. Check CSV file or preprocessing steps!")

# Splitting Data
X_train, X_test, y_train, y_test = train_test_split(df["Processed_Text"], df["Bias"], test_size=0.2, random_state=42)

# Debugging: Check data split
print(f"🔹 Training samples: {len(X_train)}, Testing samples: {len(X_test)}")

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer(ngram_range=(1,2), max_df=0.9, min_df=5, max_features=5000)

# Model Pipeline
model = Pipeline([
    ("tfidf", vectorizer),
    ("classifier", LogisticRegression(max_iter=1000))
])

# Hyperparameter Tuning
param_grid = {
    "classifier__C": [0.1, 1, 10],  # Regularization strength
    "classifier__penalty": ["l2"]  # Ridge regularization
}

grid_search = GridSearchCV(model, param_grid, cv=5, scoring="accuracy", verbose=1, n_jobs=-1)
grid_search.fit(X_train, y_train)

# Get Best Model
best_model = grid_search.best_estimator_

# Evaluate Model
y_pred = best_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("✅ Best Model Accuracy:", round(accuracy * 100, 2), "%")
print("🔹 Classification Report:\n", classification_report(y_test, y_pred))

# Save Model
joblib.dump(best_model, "political_bias_classifier.pkl")
print("✅ Model saved as 'political_bias_classifier.pkl'")
