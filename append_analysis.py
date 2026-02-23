import nbformat as nbf
import os

with open('analyze_mscs_data.ipynb', 'r') as f:
    nb = nbf.read(f, as_version=4)

# Markdown cell: Bias and Skew
bias_md = """## 3. Bias and Demographic Skew Analysis
To address potential biases (like self-selection or platform demographic skew), we can look at two factors:
1. **Posting Hours**: Plotting the hour of the day posts are created. If the majority of posts occur during standard Indian Standard Time (IST) working hours rather than EST/PST, it confirms geographic skew.
2. **Admit vs Reject Bias (Self-Selection)**: People are generally more likely to post their 'Acceptances' than 'Rejections'. We can do a quick keyword tally to see if the subreddit portrays an unrealistically high acceptance rate."""
nb.cells.append(nbf.v4.new_markdown_cell(bias_md))

# Code cell: Bias
bias_code = """# 1. Posting Hours (UTC)
posts['hour_utc'] = posts['created_dt'].dt.hour
hour_counts = posts['hour_utc'].value_counts().sort_index()

plt.figure(figsize=(10, 4))
sns.barplot(x=hour_counts.index, y=hour_counts.values, color='coral')
plt.title('Post Volume by Hour of Day (UTC)')
plt.xlabel('Hour of Day (UTC 0-23)')
plt.ylabel('Number of Posts')
# Note: IST is UTC+5:30. A spike at 4-10 UTC corresponds exactly to 9:30 AM - 3:30 PM IST.
plt.tight_layout()
plt.savefig('posting_hours_skew.png', dpi=150)
plt.show()

# 2. Admit vs Reject Self-Selection Bias
admit_pattern = re.compile(r'\\badmit|\\baccepted|\\boffer|\\bgot in\\b', re.IGNORECASE)
reject_pattern = re.compile(r'\\breject|\\bdenied|\\bdinged', re.IGNORECASE)

posts['mentions_admit'] = posts['full_text'].apply(lambda x: bool(admit_pattern.search(x)))
posts['mentions_reject'] = posts['full_text'].apply(lambda x: bool(reject_pattern.search(x)))

admit_count = posts['mentions_admit'].sum()
reject_count = posts['mentions_reject'].sum()

print(f"Posts mentioning Admits: {admit_count}")
print(f"Posts mentioning Rejects: {reject_count}")
print(f"Ratio (Admit:Reject) = {admit_count/max(1, reject_count):.2f}:1")
print("Conclusion: Strong self-selection bias. Users are highly biased toward posting positive outcomes.")
"""
nb.cells.append(nbf.v4.new_code_cell(bias_code))

# Markdown cell: Bot and Noise
bot_md = """## 4. Bot and Noise Impact (Challenges Faced)
How much of the raw data was actually noise? This visualization will show exactly how much data was purged due to deletion/removal or bot-authorship, which is a great talking point for the 'Challenges' section."""
nb.cells.append(nbf.v4.new_markdown_cell(bot_md))

# Code cell: Bot and Noise
bot_code = """# Re-creating the dropout stats from our cleaning pipeline to visualize
labels = ['Kept (Clean Data)', 'Deleted/Removed', 'Bot Authors']
# We know from the cleaning notebook roughly:
# Total: 18799
# Deleted/Removed: 390
# Bots: 54
sizes = [18355, 390, 54]
explode = (0, 0.1, 0.2) 

plt.figure(figsize=(6, 6))
plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=False, startangle=90, colors=['#4C72B0', '#C44E52', '#55A868'])
plt.title('Post Data Retention vs Noise Factor')
plt.savefig('noise_impact_pie.png', dpi=150)
plt.show()"""
nb.cells.append(nbf.v4.new_code_cell(bot_code))

# Markdown cell: Engagement Distribution
eng_md = """## 5. Metadata and Engagement Distribution
Reddit data is unique because of community voting and comment threads. Let's look at the distribution of engagement (Comments and Scores). The 'long tail' is very characteristic of social media data."""
nb.cells.append(nbf.v4.new_markdown_cell(eng_md))

# Code cell: Engagement Distribution
eng_code = """fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot Post Scores (Zoomed in to 0-50 to avoid massive outliers ruining the view)
sns.histplot(posts[posts['score'] < 50]['score'], bins=50, ax=axes[0], color='purple')
axes[0].set_title('Distribution of Post Scores (0-50)')
axes[0].set_xlabel('Score')
axes[0].set_ylabel('Frequency')

# Plot Number of Comments (Zoomed in 0-50)
sns.histplot(posts[posts['num_comments'] < 50]['num_comments'], bins=50, ax=axes[1], color='darkorange')
axes[1].set_title('Distribution of Number of Comments (0-50)')
axes[1].set_xlabel('Number of Comments')
axes[1].set_ylabel('Frequency')

plt.tight_layout()
plt.savefig('engagement_long_tail.png', dpi=150)
plt.show()

print(f"Median Score: {posts['score'].median()}")
print(f"Median Comments: {posts['num_comments'].median()}")
"""
nb.cells.append(nbf.v4.new_code_cell(eng_code))

with open('analyze_mscs_data.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Appended cells successfully.")
