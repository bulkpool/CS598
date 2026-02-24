import nbformat as nbf

# Read the notebook
with open('clean_mscs_data.ipynb', 'r') as f:
    nb = nbf.read(f, as_version=4)

# Find the cell with stage 7
stage7_idx = -1
for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'markdown' and '## Stage 7' in cell.source:
        stage7_idx = i
        break

if stage7_idx != -1:
    # Insert new code cell
    code = """# Convert Unix timestamps to datetime
posts_step6['created_dt'] = pd.to_datetime(posts_step6['created_utc'], unit='s', utc=True)
comments_step6['created_dt'] = pd.to_datetime(comments_step6['created_utc'], unit='s', utc=True)

# Define date range: Aug 2023 - Jul 2025
start_date = pd.to_datetime('2023-08-01', utc=True)
end_date = pd.to_datetime('2025-07-31 23:59:59', utc=True)

# Filter by date range
posts_step7 = posts_step6[(posts_step6['created_dt'] >= start_date) & (posts_step6['created_dt'] <= end_date)].copy()
comments_step7 = comments_step6[(comments_step6['created_dt'] >= start_date) & (comments_step6['created_dt'] <= end_date)].copy()

print('AFTER date filter (Aug 2023 - Jul 2025):')
print(f'  Posts    — {len(posts_step6):>7,} → {len(posts_step7):>7,}   (removed {len(posts_step6)-len(posts_step7):,})')
print(f'  Comments — {len(comments_step6):>7,} → {len(comments_step7):>7,}   (removed {len(comments_step6)-len(comments_step7):,})')"""
    
    new_cell = nbf.v4.new_code_cell(code)
    nb.cells.insert(stage7_idx + 1, new_cell)
    
    # Save notebook
    with open('clean_mscs_data.ipynb', 'w') as f:
        nbf.write(nb, f)
    print("Notebook patched successfully!")
else:
    print("Stage 7 not found!")
