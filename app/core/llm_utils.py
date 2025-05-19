import requests
import os
from dotenv import load_dotenv
import re
from typing import List

from tenacity import retry, stop_after_attempt, wait_exponential
from transformers import pipeline  #  Import for combine_summaries

load_dotenv()

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HEADERS = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}

def clean_text(text: str) -> str:
    """Remove PDF artifacts and normalize text"""
    text = re.sub(r'\s+', ' ', text)  # Fix broken spacing
    text = re.sub(r'http\S+|www\S+|DOI:\s*\S+', '', text)  # Remove URLs/DOIs
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)  # Keep only readable chars
    
    return text.strip()

def chunk_text(text: str, max_words: int = 400) -> List[str]:
    """Split text into word-aware chunks (conservative for token limits)"""
    words = text.split()
    return [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def summarize_chunk(chunk: str) -> str:
    """Summarize a single text chunk with retry logic"""
    response = requests.post(
        API_URL,
        headers=HEADERS,
        json={
            "inputs": chunk,
            "parameters": {
                "max_length": 130,
                "min_length": 30,
                "do_sample": False
            }
        },
        timeout=20
    )
    if not response.ok:
        raise ValueError(f"API Error {response.status_code}: {response.text}")
    return response.json()[0]['summary_text']

def combine_summaries(summaries: List[str]) -> str:
    """Combines multiple summaries into a coherent whole."""

    if not summaries:
        return "No summaries to combine."
    if len(summaries) == 1:
        return summaries[0]

    combine_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")  #  Or try "google/pegasus-xsum"
    combined_summary = combine_summarizer(summaries, truncation=True, max_length=500)[0]['summary_text']  #  Adjust max_length as needed
    return combined_summary

def summarize_text(text: str) -> str:
    try:
        # Step 1: Clean and prepare text
        cleaned = clean_text(text)
        
        # Step 2: Handle short texts directly
        if len(cleaned.split()) <= 500:
            return summarize_chunk(cleaned)
            
        # Step 3: Process long texts in chunks
        chunks = chunk_text(cleaned)
        summaries = []
        
        for chunk in chunks:
            try:
                summaries.append(summarize_chunk(chunk))
            except Exception as e:
                print(f"Failed on chunk: {str(e)}")
                continue
        
        # Step 4: Combine the summaries
        final_summary = combine_summaries(summaries)
        return final_summary
        
    except Exception as e:
        return f"Critical Error: {str(e)}"