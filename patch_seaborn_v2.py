import nbformat as nbf
import json

with open('analyze_mscs_data.ipynb', 'r') as f:
    nb = nbf.read(f, as_version=4)

for cell in nb.cells:
    if cell.cell_type == 'code':
        if 'sns.barplot(' in cell.source:
            cell.source = cell.source.replace("sns.barplot(x=hour_counts.index, y=hour_counts.values, color='coral')", "plt.bar(hour_counts.index, hour_counts.values, color='coral')")
        if 'sns.histplot(' in cell.source:
            cell.source = cell.source.replace("sns.histplot(posts[posts['score'] < 50]['score'], bins=50, ax=axes[0], color='purple')", "axes[0].hist(posts[posts['score'] < 50]['score'], bins=50, color='purple', edgecolor='white')")
            cell.source = cell.source.replace("sns.histplot(posts[posts['num_comments'] < 50]['num_comments'], bins=50, ax=axes[1], color='darkorange')", "axes[1].hist(posts[posts['num_comments'] < 50]['num_comments'], bins=50, color='darkorange', edgecolor='white')")

with open('analyze_mscs_data.ipynb', 'w') as f:
    nbf.write(nb, f)
