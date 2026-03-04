import os.path
import pandas
import spacy
import re
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
import os

# --- SETUP NLP ---
nlp = spacy.load("en_core_web_sm")
custom_stop_words = [
    # Hiring / Generic
    "job", "description", "role", "seek", "position", "candidate", "ideal",
    "opportunity", "join", "client", "company", "new", "type", "remote",
    "experience", "work", "year", "skill", "require", "requirement", "include",
    "need", "strong", "ability", "knowledge", "responsible",

    # HR / Benefits
    "pay", "benefit", "salary", "range", "employee", "disability", "equal",
    "time", "base", "status",

    # Vague Verbs
    "provide", "focus", "drive", "collaborate", "support", "build", "help",
    "create", "maintain", "perform",

    # Generic Tech Context (Too broad to be useful)
    "solution", "system", "environment", "platform", "product", "service",
    "technology", "technical", "application", "industry", "high", "software",
    "engineer", "engineering", "development", "develop",

    # NEW: Recruiting & Process
    "interview", "recruiter", "prospect", "candidate", "select", "review",
    "meet", "touch", "region", "status", "fill", "join", "process", "aspect",

    # NEW: Corporate Fluff & Adjectives
    "impact", "fast", "pace", "inspire", "excite", "excited", "successful",
    "dynamic", "demanding", "challenge", "varied", "culture", "passion",
    "mission", "critical", "commercial", "good", "excellent", "solid",
    "expert", "proficiently", "minimum", "related", "specific", "wide",
    "array", "proven", "track", "record", "strong", "deep", "outcome",
    "real", "thinker", "acuman", "acumen", "important", "fundamental",

    # NEW: Benefits & Legal
    "insurance", "medical", "life", "retirement", "tax", "free", "saving",
    "plan", "healthcare", "incentive", "compensation", "eligible",
    "discretionary", "bonus", "bachelor", "degree", "discipline", "stem",
    "accordance", "applicable", "law", "legal", "compliance", "regulatory",
    "addition", "program", "fund", "funding", "settlement", "investor",

    # NEW: Generic Verbs/Nouns
    "look", "know", "prove", "manage", "solve", "participate", "align",
    "increase", "maximize", "iterate", "define", "spec", "change", "flex",
    "course", "pre", "gen", "desk", "partner", "team", "task", "problem",
    "dissect", "return", "efficiency", "research", "analysis", "power",

    # Generic Nouns
    "skill", "skills", "talent", "level", "following", "access",
    "aspect", "impact", "prospect", "outcome", "change", "course",
    "desk", "gen", "spec", "pre", "market", "interview", "seniority",

    "https", "http", "com", "www", "career", "careers", "apply",
    "website", "location", "locations", "email", "contact",
    "toast", "toasttab", "restaurant"
]

# Update Spacy's default stop words
for word in custom_stop_words:
    lex = nlp.vocab[word]
    lex.is_stop = True

# --- CLEANING FUNCTION ---
def clean_text(text):
    """
    Function to return cleaned token using nlp
    :param text: str
    :return: object
    """

    text = text.lower()

    # Remove URLs (http/https/www)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'www\S+', '', text)

    # 3. Remove Email Addresses
    text = re.sub(r'\S+@\S+', '', text)

    doc = nlp(text)

    allowed_pos = ["NOUN", "PROPN"]
    clean_tokens = []

    for token in doc:
        lemma = token.lemma_.lower()

        if(
            not token.is_stop
            and not token.is_punct
            and not token.like_num
            and token.pos_ in allowed_pos
            and lemma not in custom_stop_words
            and len(lemma) > 2
        ):
            clean_tokens.append(lemma)

    return " ".join(clean_tokens)

def clean_text_for_embeddings(text) -> str:
    """
    Cleaning function for semantic model
    """

    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"http\\S+", " ", text)
    text = re.sub(r"www\\S+", " ", text)
    text = re.sub(r"\\S+@\\S+", " ", text)
    text = re.sub(r"\\s+", " ", text).strip()

    return text

# ---- THE MATCHER -----
class JobMatcher:
    """
    Class to implement the job matching logic using TF-IDF
    """

    def __init__(self):
        # Load the model only when the class is initialized
        self.tfidf: TfidfVectorizer
        self.df: pandas.DataFrame

        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "models", "model.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model artifact not found at {model_path}. Run train.py first.")

        with open(model_path, "rb") as fd:
            loaded_data = pickle.load(fd)
            self.tfidf = loaded_data[0]
            self.tfidf_matrix = loaded_data[1]
            self.df = loaded_data[2]

        # Get the vocabulary
        self.feature_names = np.array(self.tfidf.get_feature_names_out())

    @staticmethod
    def combine_user_fields(user_profile:dict) -> str:
        """
        Helper function to merge structured user fields into a single text
        blocks.
        Args:
            user_profile: dict

        Returns: str
        """
        fields = [
            user_profile.get("target_roles", ""),
            user_profile.get("skills", ""),
            user_profile.get("experience_level", "")
        ]

        results = []
        for f in fields:
            if isinstance(f, list):
                for item in f:
                    results.append(str(item))
            else:
                results.append(str(f))

        return " ".join(results)

    def get_missing_skills(self, user_vector, job_idx):
        """
        Identifies high value keywords present in the Job but missing from the
        User Vector
        Args:
            user_vector: ndarray array of shape
            job_idx: int

        Returns: list
        """

        # Get the vector for the specific job
        job_vector = self.tfidf_matrix[job_idx].toarray().flatten()
        user_vector_dense = user_vector.toarray().flatten()

        # Find indices where Job > 0 but the User == 0
        missing_indices = np.where((job_vector > 0) & (user_vector_dense == 0))[0]

        # Sort the importance
        # We want the heaviest missing words, not just any missing word.
        # Sort indices by job_vector weight descending.
        sorted_missing = sorted(missing_indices, key=lambda i: job_vector[
            i], reverse=True)

        # Convert top 5 indices back to words
        top_missing_words = self.feature_names[sorted_missing[:5]].tolist()

        return top_missing_words

    def recommend(self, user_profile:dict, top_n=10):
        """
        Class method to implement cosine similarity logic to compare the
        "User Vector" against the "Job Vectors" and output a raw match score
        Args:
            user_profile: dict
            top_n: int

        Returns: dict
        """

        # Pre-processing
        user_text = self.combine_user_fields(user_profile)

        # Clean the User Input
        cleaned_text = clean_text(user_text)

        # Convert the User Input to Numbers (Vector)
        user_vector = self.tfidf.transform([cleaned_text])

        # Calculate the cosine similarity
        similarities = cosine_similarity(user_vector, self.tfidf_matrix).flatten()

        # Get Top N Matches
        top_indices = similarities.argsort()[-top_n:][::-1]

        # Format Results
        results = []
        for index in top_indices:
            score = similarities[index]

            # Filter: Only return if there is some relevancy
            if score < 0.05:
                continue

            job_row = self.df.iloc[index]

            # Find missing skills
            missing = self.get_missing_skills(user_vector, index)

            results.append({
                "job_id": str(job_row.get("_id")),
                "title": job_row.get("title", "Unknown"),
                "company": job_row.get("company", "Unknown"),
                "score": round(score, 2),
                "missing_skills": missing
            })

        return results

class SemanticJobMatcher:
    """
    Class to implement the job matching logic using TF-IDF
    """

    def __init__(self):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(current_dir, "models", "semantic_model.pkl")

        if not os.path.exists(base_path):
            raise FileNotFoundError(f"Model artifact not found at "
                                    f"{base_path}. Run train.py first.")

        with open(base_path, "rb") as fd:
            data = pickle.load(fd)            
            # Access by keys instead of unpacking by position
            self.job_embeddings = data.get("embeddings")
            self.df = data.get("df")
            # If you saved job_ids, you can grab them too
            self.job_ids = data.get("job_ids")

        print("✅ Semantic Matcher initialized successfully.")
        
    @staticmethod
    def get_missing_skills_basic(user_skills: list, job_skills:
    list) -> list:
        """
        Compares user skills against the job's structured skills list.
        Returns no inferred gaps when the job has no structured skills.
        """

        if isinstance(user_skills, str):
            user_skills = [user_skills]
        elif not isinstance(user_skills, list):
            user_skills = []

        user_set = {
            str(skill).strip().lower()
            for skill in user_skills
            if str(skill).strip()
        }

        if not isinstance(job_skills, list) or not job_skills:
            return []

        missing = []
        seen = set()

        for skill in job_skills:
            normalized = str(skill).strip().lower()
            if not normalized:
                continue
            if normalized in user_set:
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            missing.append(normalized)

        return missing[:5]

    @staticmethod
    def salary_matches(job_row, user_min, user_max):
        """
        To find the jobs which match the user criteria for salary range
        """
        if user_min in (None, "") and user_max in (None, ""):
            return True

        salary_range = job_row.get("salary_range") or {}
        if not isinstance(salary_range, dict):
            salary_range = {}

        job_min = salary_range.get("min")
        job_max = salary_range.get("max")

        if job_min in (None, "") and job_max in (None, ""):
            return False

        if job_min in (None, ""):
            job_min = job_max
        if job_max in (None, ""):
            job_max = job_min

        job_min = float(job_min)
        job_max = float(job_max)

        user_min = float(user_min) if user_min not in (None, "") else None
        user_max = float(user_max) if user_max not in (None, "") else None

        if user_min is not None and user_max is not None:
            return job_max >= user_min and job_min <= user_max
        if user_min is not None:
            return job_max >= user_min
        return job_min <= user_max


    def recommend(self, user_preferences: dict, top_n=5):
        """

        Args:
            user_preferences:
            top_n:

        Returns:
        """

        user_skills = user_preferences.get("skills", [])
        if isinstance(user_skills, str):
            user_skills = [user_skills]
        elif not isinstance(user_skills, list):
            user_skills = []

        target_roles = user_preferences.get("target_roles", [])
        if isinstance(target_roles, str):
            target_roles = [target_roles]
        elif not isinstance(target_roles, list):
            target_roles = []

        user_min = user_preferences.get("salary_min")
        user_max = user_preferences.get("salary_max")

        eligible_indices = [
            idx for idx, job_row in self.df.iterrows()
            if self.salary_matches(job_row, user_min, user_max)
        ]
        if not eligible_indices:
            return []

        filtered_embeddings = self.job_embeddings[eligible_indices]

        user_text = " ".join(target_roles + user_skills)
        # Clean user text
        cleaned_user_text = clean_text_for_embeddings(user_text)
        # Encode user input
        user_vector = self.encoder.encode(cleaned_user_text)

        # Calculate the cosine similarities
        similarities = util.cos_sim(user_vector, filtered_embeddings)[
            0].cpu().numpy()

        # Rank Results
        top_indices = similarities.argsort()[-top_n:][::-1]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score < 0.20:
                continue

            original_idx = eligible_indices[idx]
            job_row = self.df.iloc[original_idx]

            job_skills = job_row.get("skills_required", [])
            missing = self.get_missing_skills_basic(user_skills, job_skills)

            results.append({
                "job_id": str(job_row.get("_id")),
                "title": job_row.get("title", "Unknown"),
                "company": job_row.get("company", "Unknown"),
                "location": job_row.get("location", "Remote / Not Listed"),
                "url": job_row.get("source_url") or "#",
                "salary_range": job_row.get("salary_range", {"min": None, "max": None}),
                "score": round(score, 2),
                "missing_skills": missing
            })

        return results