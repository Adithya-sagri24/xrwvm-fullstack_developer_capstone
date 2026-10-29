import requests
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")

# Global in-memory list for reviews posted in current server session
ADDED_REVIEWS = []


def _load_dealers():
    path = (
        Path(__file__).resolve().parent.parent /
        "database" / "data" / "dealerships.json"
    )
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("dealerships", [])
    return []


def _load_reviews():
    path = (
        Path(__file__).resolve().parent.parent /
        "database" / "data" / "reviews.json"
    )
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("reviews", [])
    return []


def get_request(endpoint, **kwargs):
    params = ""
    if (kwargs):
        for key, value in kwargs.items():
            params = params + key + "=" + value + "&"
    request_url = backend_url + endpoint + "?" + params
    print("GET from {} ".format(request_url))
    try:
        response = requests.get(request_url, timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception:
        print("Network exception occurred, using fallback data")

    # Cloud fallback when microservice on port 3030 is unreachable
    if endpoint == "/fetchDealers":
        return _load_dealers()
    elif endpoint.startswith("/fetchDealers/"):
        state = endpoint.replace("/fetchDealers/", "").strip().lower()
        dealers = _load_dealers()
        return [
            d for d in dealers
            if d.get("state", "").lower() == state
        ]
    elif endpoint.startswith("/fetchDealer/"):
        try:
            d_id = int(endpoint.replace("/fetchDealer/", "").strip())
            dealers = _load_dealers()
            for d in dealers:
                if d.get("id") == d_id:
                    return d
        except Exception:
            return None
    elif endpoint.startswith("/fetchReviews/dealer/"):
        try:
            d_id = int(endpoint.replace("/fetchReviews/dealer/", "").strip())
            all_reviews = ADDED_REVIEWS + _load_reviews()
            return [
                r for r in all_reviews
                if r.get("dealership") == d_id
            ]
        except Exception:
            return []
    return []


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + "analyze/" + text
    try:
        response = requests.get(request_url, timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    # Built-in sentiment analysis fallback
    try:
        from nltk.sentiment import SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(text)
        pos = float(scores['pos'])
        neg = float(scores['neg'])
        neu = float(scores['neu'])
        res = "positive"
        if neg > pos and neg > neu:
            res = "negative"
        elif neu > neg and neu > pos:
            res = "neutral"
        return {"sentiment": res}
    except Exception:
        lower = text.lower()
        pos_words = [
            'good', 'great', 'fantastic', 'nice', 'best', 'love', 'amazing'
        ]
        neg_words = ['bad', 'poor', 'terrible', 'worst', 'horrible']
        if any(w in lower for w in pos_words):
            return {"sentiment": "positive"}
        if any(w in lower for w in neg_words):
            return {"sentiment": "negative"}
        return {"sentiment": "neutral"}


def post_review(data_dict):
    request_url = backend_url + "/insert_review"
    try:
        response = requests.post(request_url, json=data_dict, timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Network exception occurred: {e}")

    # Fallback to in-memory store
    new_review = {
        "id": len(ADDED_REVIEWS) + 1000,
        "name": data_dict.get("name", "Anonymous"),
        "dealership": data_dict.get("dealership"),
        "review": data_dict.get("review"),
        "purchase": data_dict.get("purchase", True),
        "purchase_date": data_dict.get("purchase_date"),
        "car_make": data_dict.get("car_make"),
        "car_model": data_dict.get("car_model"),
        "car_year": data_dict.get("car_year"),
    }
    ADDED_REVIEWS.insert(0, new_review)
    return {"status": 200, "message": "Review inserted", "review": new_review}
