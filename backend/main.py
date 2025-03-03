import os
from dotenv import load_dotenv
from typing import Optional, List
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader, APIKey
import graphene
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import sqlite3
from datetime import datetime
import asyncio


load_dotenv()


app = FastAPI(title="Multilingual Sentiment Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


API_KEY = os.environ.get("API_KEY", "default_api_key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
    )


model_cache = {}

async def get_sentiment_analyzer():
    if "analyzer" not in model_cache:
        hf_token = os.environ.get("HF_AUTH_TOKEN", None)
        if hf_token is None:
            print("Warning: HF_AUTH_TOKEN not set. If the model is private, this will cause an error.")
        
        # Model per the docs:
        model_name = "tabularisai/multilingual-sentiment-analysis"
        
        # Load the model/tokenizer with auth token and explicitly apply softmax
        model = AutoModelForSequenceClassification.from_pretrained(model_name, use_auth_token=hf_token)
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)
        model_cache["analyzer"] = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            function_to_apply="softmax"
        )
    return model_cache["analyzer"]

# Initialize database
def init_db():
    conn = sqlite3.connect('sentiment_history.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sentiment_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        sentiment TEXT NOT NULL,
        score REAL NOT NULL,
        timestamp TEXT NOT NULL,
        language TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Save prediction to database
def save_prediction(text, sentiment, score, language=None):
    conn = sqlite3.connect('sentiment_history.db')
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO sentiment_analysis (text, sentiment, score, timestamp, language) VALUES (?, ?, ?, ?, ?)",
        (text, sentiment, score, timestamp, language)
    )
    conn.commit()
    conn.close()

# Get predictions from database
def get_predictions(limit=10):
    conn = sqlite3.connect('sentiment_history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, sentiment, score, timestamp, language FROM sentiment_analysis ORDER BY id DESC LIMIT ?", (limit,))
    results = cursor.fetchall()
    conn.close()
    
    predictions = []
    for row in results:
        predictions.append({
            'id': row[0],
            'text': row[1],
            'sentiment': row[2],
            'score': row[3],
            'timestamp': row[4],
            'language': row[5]
        })
    return predictions



class LabelScore(graphene.ObjectType):
    label = graphene.String()
    score = graphene.Float()

class SentimentResult(graphene.ObjectType):
    sentiment = graphene.String()
    score = graphene.Float()
    language = graphene.String()
    allScores = graphene.List(LabelScore)

class SentimentHistoryItem(graphene.ObjectType):
    id = graphene.Int()
    text = graphene.String()
    sentiment = graphene.String()
    score = graphene.Float()
    timestamp = graphene.String()
    language = graphene.String()

class Query(graphene.ObjectType):
    history = graphene.List(SentimentHistoryItem, limit=graphene.Int(default_value=10))
    
    async def resolve_history(self, info, limit):
        return get_predictions(limit)

class AnalyzeSentiment(graphene.Mutation):
    class Arguments:
        text = graphene.String(required=True)

    result = graphene.Field(SentimentResult)

    async def mutate(self, info, text):
        if not text.strip():
            return AnalyzeSentiment(
                result=SentimentResult(
                    sentiment="neutral",
                    score=0.5,
                    language=None,
                    allScores=[]
                )
            )
            
        if len(text) > 10000:
            text = text[:10000]
            
        analyzer = await get_sentiment_analyzer()

        def get_best_label(dist):
            best = max(dist, key=lambda x: x["score"])
            return best["label"], best["score"]

        all_scores_aggregated = []
        
        if len(text) > 512:
            chunks = [text[i:i+512] for i in range(0, len(text), 512)]
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            total_score = 0.0
            for chunk in chunks:
                dist = analyzer(chunk, return_all_scores=True)[0]
                label, score = get_best_label(dist)
                total_score += score
                all_scores_aggregated = dist  # store the last chunk's distribution
                if label in ["LABEL_2", "POSITIVE", "positive", "pos", "Very Positive"]:
                    positive_count += 1
                elif label in ["LABEL_0", "NEGATIVE", "negative", "neg", "Very Negative"]:
                    negative_count += 1
                elif label in ["LABEL_1", "NEUTRAL", "neutral"]:
                    neutral_count += 1
                else:
                    neutral_count += 1

            if positive_count > negative_count and positive_count > neutral_count:
                final_sentiment = "positive"
            elif negative_count > positive_count and negative_count > neutral_count:
                final_sentiment = "negative"
            else:
                final_sentiment = "neutral"
            final_score = total_score / len(chunks) if chunks else 0.5
        else:
            dist = analyzer(text, return_all_scores=True)[0]
            all_scores_aggregated = dist
            label, final_score = get_best_label(dist)
            if label in ["LABEL_2", "POSITIVE", "positive", "pos", "Very Positive"]:
                final_sentiment = "positive"
            elif label in ["LABEL_0", "NEGATIVE", "negative", "neg", "Very Negative"]:
                final_sentiment = "negative"
            elif label in ["LABEL_1", "NEUTRAL", "neutral"]:
                final_sentiment = "neutral"
            else:
                final_sentiment = "neutral"

        label_scores = [
            LabelScore(label=item["label"], score=float(item["score"]))
            for item in all_scores_aggregated
        ]

        language = None
        save_prediction(text, final_sentiment, final_score, language)

        return AnalyzeSentiment(
            result=SentimentResult(
                sentiment=final_sentiment,
                score=final_score,
                language=language,
                allScores=label_scores
            )
        )

class Mutation(graphene.ObjectType):
    analyze_sentiment = AnalyzeSentiment.Field()

class Subscription(graphene.ObjectType):
    dummy = graphene.String(default_value="No subscriptions implemented")

schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)

graphql_app = GraphQLApp(schema=schema, on_get=make_graphiql_handler())
app.mount("/graphql", graphql_app)

@app.post("/api/graphql")
async def protected_graphql(api_key: APIKey = Depends(get_api_key)):
    return {"message": "Authentication successful"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    init_db()
    asyncio.create_task(get_sentiment_analyzer())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
