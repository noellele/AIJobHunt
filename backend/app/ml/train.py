import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from .logic import clean_text, clean_text_for_embeddings
from .mongo_ingestion_utils import get_sync_jobs_collection
import os

# Get the absolute path to the current directory 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Create the directory if it doesn't exist
os.makedirs(MODEL_DIR, exist_ok=True)

# Define the full path to use in pickle.dump()
MODEL_PATH = os.path.join(MODEL_DIR, "semantic_model.pkl")

def fetch_jobs_data() -> pd.DataFrame:
    """
    Fetches the jobs data from MongoDB
    """

    print("Connecting to MongoDB via Utility...")
    collections = get_sync_jobs_collection()

    # Fetch every document in the collection
    jobs_cursor = collections.find({})

    jobs_list = list(jobs_cursor)
    if not jobs_list:
        raise ValueError("No jobs found in the database. Run ingestion first.")

    df = pd.DataFrame(jobs_list)
    df['processed_text'] = df['description'].apply(clean_text)
    return df

def build_model():
    """
    Docstring for build_model
    """

    # Load Data
    df = fetch_jobs_data()
    print(f"Loaded {len(df)} jobs. Training models...")

    # Clean Data
    df['processed_text'] = df['description'].apply(clean_text)

    # Perform TD-IDF Vectorizer
    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85,
        sublinear_tf=True
    )

    # Fit the model
    tfidf_matrix = tfidf.fit_transform(df['processed_text'])

    # Save the model
    print("Saving to model.pkl")
    with open("models/model.pkl", "wb") as f:
        pickle.dump((tfidf, tfidf_matrix, df), f)

    print("Done!")

def build_semantic_model():
    """
    Function to train the data on sentence-transformer
    Returns:
    """

    # Load Data
    df = fetch_jobs_data()
    print(f"Loaded {len(df)} jobs. Training models...")

    # Clean Data
    df['processed_text'] = df['description'].apply(clean_text_for_embeddings)

    # Load the sentence-transformer lightweight Hugging Face Model
    print("Loading Sentence Transformer...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Encode the job into dense vectors
    print("Encoding job descriptions (this may take a moment)...")

    job_embeddings = model.encode(df['processed_text'].tolist(),
                                  show_progress_bar=True)
    data_to_save = {
        "embeddings": job_embeddings,
        "df": df,
        "job_ids": df['_id'].astype(str).tolist()
    }

    # Save the artifacts
    print("Saving semantic_model.pkl...")
    with open(MODEL_PATH, "wb") as fd:
        pickle.dump(data_to_save, fd)

    print("Semantic Model built successfully!")

if __name__ == "__main__":
    #build_model()
    build_semantic_model()