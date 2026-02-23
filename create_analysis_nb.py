import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# Markdown cell: Introduction
intro_md = """# r/MSCS Dataset Analysis
This notebook performs various analyses on the cleaned `r_MSCS_posts_clean.jsonl` and `r_MSCS_comments_clean.jsonl` (or via the post_clean/comments_clean dataframes from the previous notebook).
In this notebook, we focus on:
1. **Sentiment Analysis over time**
2. **Linguistic Markers to identify international applicants**
"""
nb.cells.append(nbf.v4.new_markdown_cell(intro_md))

# Code cell: Imports and Loading Data
imports_code = """import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from datetime import datetime
import json

# Setup plot style
plt.style.use('seaborn-v0_8-darkgrid')
pd.set_option('display.max_colwidth', None)

# Assuming data is available as CSVs or JSONL. For demonstration, we'll read the original and filter, or just load if saved.
# Since we didn't save the pandas dataframes explicitly as CSVs in the previous notebook, let's load from the raw and apply the clean logic quickly, OR we can just run the previous notebook's outputs.
# For simplicity, let's re-run the core cleaning steps here so this notebook is standalone.
def load_jsonl(path):
    records = []
    with open(path) as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

raw_posts = load_jsonl('r_MSCS_posts.jsonl')
raw_comments = load_jsonl('r_MSCS_comments.jsonl')

posts = pd.DataFrame(raw_posts)
comments = pd.DataFrame(raw_comments)

# Quick clean
SENTINEL_VALUES = {'[deleted]', '[removed]', '[deleted by user]'}
posts = posts[~posts['selftext'].isin(SENTINEL_VALUES)].copy()
posts['selftext'] = posts['selftext'].fillna('')
comments = comments[~comments['body'].isin(SENTINEL_VALUES) & (comments['body'].fillna('').str.strip() != '')].copy()

# Date filter
posts['created_dt'] = pd.to_datetime(posts['created_utc'], unit='s', utc=True)
comments['created_dt'] = pd.to_datetime(comments['created_utc'], unit='s', utc=True)
start_date = pd.to_datetime('2023-08-01', utc=True)
end_date = pd.to_datetime('2025-07-31 23:59:59', utc=True)

posts = posts[(posts['created_dt'] >= start_date) & (posts['created_dt'] <= end_date)]
comments = comments[(comments['created_dt'] >= start_date) & (comments['created_dt'] <= end_date)]

print(f"Loaded {len(posts)} posts and {len(comments)} comments.")"""
nb.cells.append(nbf.v4.new_code_cell(imports_code))

# Markdown cell: Sentiment Analysis
sentiment_md = """## 1. Sentiment Analysis Over Time
We will use NLTK's VADER SentimentIntensityAnalyzer to calculate the sentiment of posts and comments over time."""
nb.cells.append(nbf.v4.new_markdown_cell(sentiment_md))

# Code cell: Sentiment calculation
sentiment_code = """import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon', quiet=True)

sid = SentimentIntensityAnalyzer()

# Calculate sentiment for posts
# Use title + selftext
posts['full_text'] = posts['title'].fillna('') + ". " + posts['selftext'].fillna('')
posts['sentiment_score'] = posts['full_text'].apply(lambda text: sid.polarity_scores(text)['compound'])

# Group by month
posts['month'] = posts['created_dt'].dt.to_period('M')
monthly_sentiment = posts.groupby('month')['sentiment_score'].mean()

plt.figure(figsize=(12, 5))
monthly_sentiment.plot(color='blue', marker='o')
plt.title('Average Post Sentiment Over Time in r/MSCS')
plt.xlabel('Month')
plt.ylabel('Average Compound Sentiment Score')
plt.axhline(0, color='red', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('sentiment_over_time.png', dpi=150)
plt.show()"""
nb.cells.append(nbf.v4.new_code_cell(sentiment_code))

# Markdown cell: Linguistic Markers
ling_md = """## 2. Linguistic Markers (Identifying User Origins/Demographics)
The MSCS subreddit has a large demographic of international students, particularly from India. 
We can look for specific linguistic markers such as:
* **"Tier 1" / "Tier 2" / "Tier 3"** - commonly used to describe undergraduate colleges in India.
* **"CGPA" or "GPA: X/10"** - vs the standard US 4.0 scale.
* **"B.Tech" or "BE"** - Bachelor of Technology/Engineering.
* **"Lakhs" / "Crores" or "INR"** - Indian currency units."""
nb.cells.append(nbf.v4.new_markdown_cell(ling_md))

# Code cell: Linguistic markers extraction
ling_code = """# Define explicit regex patterns for markers
tier_pattern = re.compile(r'tier\\s*[1-3]', re.IGNORECASE)
cgpa_pattern = re.compile(r'cgpa|\\b\\d\\.\\d+\\s*/\\s*10\\b', re.IGNORECASE)
degree_pattern = re.compile(r'b\\.?tech\\b|b\\.?e\\.?\\b', re.IGNORECASE)
currency_pattern = re.compile(r'\\blakhs?\\b|\\blacs?\\b|\\bcrores?\\b|\\binr\\b', re.IGNORECASE)

def has_indian_markers(text):
    if not isinstance(text, str): return False
    return bool(tier_pattern.search(text) or cgpa_pattern.search(text) or degree_pattern.search(text) or currency_pattern.search(text))

posts['is_international_indian'] = posts['full_text'].apply(has_indian_markers)

intl_count = posts['is_international_indian'].sum()
total_count = len(posts)
print(f"Found {intl_count} posts ({intl_count/total_count*100:.1f}%) with linguistic markers indicating international/Indian applicants.")

# Compare Sentiment: International vs General
avg_sentiment_intl = posts[posts['is_international_indian']]['sentiment_score'].mean()
avg_sentiment_other = posts[~posts['is_international_indian']]['sentiment_score'].mean()

print(f"Average sentiment (International/Indian): {avg_sentiment_intl:.3f}")
print(f"Average sentiment (Other/Unidentified): {avg_sentiment_other:.3f}")

# Plotting the proportion over time
monthly_intl = posts.groupby('month')['is_international_indian'].mean() * 100

plt.figure(figsize=(12, 5))
monthly_intl.plot(color='green', marker='s')
plt.title('Percentage of Posts with International (Indian) Linguistic Markers Over Time')
plt.xlabel('Month')
plt.ylabel('Percentage of Posts (%)')
plt.tight_layout()
plt.savefig('intl_markers_over_time.png', dpi=150)
plt.show()"""
nb.cells.append(nbf.v4.new_code_cell(ling_code))

with open('analyze_mscs_data.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Analysis notebook created successfully.")
