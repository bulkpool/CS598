# r/MSCS Data Cleaning Pipeline (In-Depth Presentation Notes)

**Slide Title Idea:** Preparing the Data: From Raw JSONL to Analysis-Ready Metrics

*When presenting the data cleaning section of your Methodological Expo, you should walk the audience through the sequential pipeline we built. This step-by-step approach clearly demonstrates how you mitigated the specific challenges associated with Reddit data (noise, bots, formatting). The following notes provide an IN-DEPTH explanation of the technical "How" and analytical "Why" behind each step.*

---

### Step 1: Loading & Column Selection
*   **The Technical "How":** We started with two distinct JSONL datasets (`r_MSCS_posts.jsonl` and `r_MSCS_comments.jsonl`), representing over 18,000 posts and 133,000 comments. The raw JSON objects returned by the Reddit API contain upwards of 115 distinct metadata fields per post (e.g., `author_flair_css_class`, `gildings`, `awarders`). We wrote a pandas projection to strictly subset this down to only 8 essential columns: `id`, `author`, `title`, `selftext` (body), `score`, `num_comments`, `permalink`, and `created_utc`.
*   **The Analytical "Why":** Reddit's raw API dumps are notoriously bloated with rendering and UI state metadata that are completely irrelevant for Data-Driven research tracks. By stripping these columns immediately upon instantiating our pandas DataFrames, we drastically reduced the memory footprint, sped up processing times, and forced the scope of our methodology to focus purely on temporal and NLP-based dimensions.

### Step 2 & 3: Purging Deleted/Removed Content (Noise Reduction)
*   **The Technical "How":** We iterated through the `selftext` and `body` fields, identifying and dropping any rows where the content exactly matched the sentinel values: `[deleted]`, `[removed]`, or `[deleted by user]`. We also purged comments that were entirely empty or consisted solely of whitespace. (Note: We intentionally retained posts with empty `selftext` if they contained a valid `title`, as "Title-only" questions are standard behavior).
*   **The Analytical "Why":** This mitigates a massive source of data contamination. On r/MSCS, users frequently scrub their profile evaluation posts after receiving advice to protect their identity. Alternatively, Reddit moderators aggressively remove posts that violate formatting rules. If we did not purge these "empty husks", our NLP algorithms (like TF-IDF or VADER) would interpret `[deleted]` as the most frequent and heavily weighted term in the corpus, completely ruining any topic modeling or sentiment validity.

### Step 4: Bot & Automation Filtering
*   **The Technical "How":** We constructed a discrete list of `KNOWN_BOTS` (such as `AutoModerator` and `RemindMeBot`). We checked every `author` name against this exact-match list, and then applied a broadly scoped regex filter to catch any author containing the substrings "bot" or "robot" (e.g., lowercase conversion check). All matching rows were dropped.
*   **The Analytical "Why":** Bot actions create artificial spikes in engagement metrics. For example, `AutoModerator` frequently posts automated sticky comments outlining subreddit rules on every single post. If these were left in the dataset, "Please read the wiki" would mathematically appear as the most "engaged" discussion topic. Removing bots ensures our analysis strictly reflects authentic human behavior and concerns.

### Step 5: Deduplication
*   **The Technical "How":** We executed `drop_duplicates` on the DataFrames, using the unique base-36 alphanumeric Reddit `id` as the primary key constraint to identify overlaps.
*   **The Analytical "Why":** Data collection pipelines (especially REST API paginators) are inherently flaky. Network timeouts, rate limits, or overlapping time-windows during pagination frequently lead to duplicate rows being appended to output JSONL files. This step guarantees data integrity, ensuring every post and comment is counted exactly once when we calculate our final descriptive statistics.

### Step 6: Text Normalization
*   **The Technical "How":** We built a customized `normalize_text` pipeline using compiled regular expressions. This function applied four transformations:
    1.  Stripped out raw HTTP/HTTPS URLs entirely.
    2.  Collapsed Markdown link syntax (e.g., converting `[Check this out](https://...)` to simply `Check this out`).
    3.  Removed non-breaking spaces (e.g., replacing `&nbsp;` with standard whitespace).
    4.  Collapsed excessive contiguous newlines characters down to standard paragraph breaks.
*   **The Analytical "Why":** Raw internet text is incredibly noisy. URLs, in particular, completely break standard NLP tokenizers (like BERT or NLTK) because the models attempt to parse the URL fragments as words. Normalizing the text creates a clean, standardized corpus suitable for VADER sentiment scoring and N-gram tracking, ensuring our models evaluate the *meaning* of the text rather than its *formatting*.

### Step 7: Timestamp Parsing & Date Bounding
*   **The Technical "How":** We utilized `pd.to_datetime` to convert the raw Unix Epoch integers (`created_utc`) into timezone-aware pandas `Datetime` objects (`created_dt`). Finally, we applied a strict boolean mask: `posts_clean = posts_clean[(posts_clean['created_dt'] >= '2023-08-01') & (posts_clean['created_dt'] <= '2025-07-31')]`.
*   **The Analytical "Why":** Unix timestamps are essentially meaningless integers for seasonal or temporal analysis. Converting them allowed us to cleanly group the data by month (to track sentiment volume over time) and by hour (to prove Indian geographic skew). Bounding the dates establishes a rigorous, scientifically valid study window. It ensures our analysis focuses exclusively on the complete 'Fall 2024 / Fall 2025' admission cycles, preventing any partial or irrelevant historical data from skewing our seasonal trends.

---

## The Columns: What We Kept, What We Dropped, and Why

*During your presentation, you should justify your Column Selection step (Stage 1). The raw Reddit API returns over 100 metadata fields per post. We ruthlessly narrowed this down to just 8 core columns. Here is the explanation you can use to justify the remaining features.*

### 1. `id` and `permalink` (The Identifiers)
*   **What it is:** The unique base-36 alphanumeric string representing the specific post (e.g., `15f3g0b`) and its routing URL.
*   **Why it's necessary:** 
    *   **Deduplication:** The `id` is the mathematically rigorous key we use to drop duplicated rows caused by scraper pagination overlap. 
    *   **Traceability:** It allows us to perfectly trace an anonymized row of data back to the actual live Reddit post if manual validation is needed.

### 2. `author` (The Social Node)
*   **What it is:** The string username of the individual who posted.
*   **Why it's necessary:** 
    *   **Bot Purging:** Allowed us to filter out purely automated accounts like `AutoModerator`.
    *   **Network Analysis:** Required if we wanted to build a graph-network of users to identify "expert advisors" vs "information seekers" in the community.
    *   **Engagement Tracking:** Allowed us to identify the "Top Authors" by post frequency.

### 3. `title` and `selftext` / `body` (The NLP Corpus)
*   **What it is:** The central text of the post submission (Title + Body) or the comment.
*   **Why it's necessary:** This is the absolute core of the dataset. This text corpus is what powers all of our NLP modeling:
    *   **Topic Modeling:** We need these raw strings to run LDA/BERTopic to identify structural themes (e.g. "Visa Issues" vs "Profile Evaluation").
    *   **Sentiment Analysis:** VADER algorithms parse the syntax within these columns to output our month-over-month stress/joy metrics.
    *   **Demographic Extraction:** Allowed us to run regex mapping to find markers like "CGPA" or "B.Tech" to confidently classify users as International applicants.

### 4. `created_utc` / `created_dt` (The Temporal Anchor)
*   **What it is:** The exact millisecond timestamp the post was submitted.
*   **Why it's necessary:** Without this, the dataset is completely static. The timestamp allows us to map all of our derived metrics (Sentiment, Post Volume, International Demographics) across the strict August 2023 - July 2025 timeline. It also permitted us to map the hours of the day (UTC) to prove the Indian Standard Time geographic skew.

### 5. `score` and `num_comments` (The Engagement Metrics)
*   **What it is:** The net upvote/downvote differential of the post, and the total count of comments underneath it.
*   **Why it's necessary:** 
    *   **Long-Tail Distribution:** Reddit is crowd-sourced. These columns prove the structural reality of our dataset: a massive "long tail" where the vast majority of posts receive <3 upvotes, but highly critical posts (e.g., "Fall 2024 Decisions are Out") go viral. 
    *   **Algorithmic Weighting:** These columns can theoretically be used to natively cross-weight the validity of our topic models (i.e., treating highly upvoted topics with greater algorithmic significance than ignored topics).

### What We Intentionally Dropped (And Why)
*   The raw JSON objects contained dozens of features like `author_flair_text`, `thumbnail_url`, `awarders`, `subreddit_type`, `is_video`, etc. 
*   **The Justification:** Data sparsity and scope constraint. Almost 98% of these fields contained strict `null` values or pertained purely to internal web-rendering physics (like CSS identifiers for badges). Retaining these columns would have exponentially blown up the RAM overhead required to load the DataFrames without supplying any statistically significant signal for our core temporal or linguistic tracking goals.
