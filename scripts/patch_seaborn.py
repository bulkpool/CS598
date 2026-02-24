import nbformat as nbf
import json

with open('analyze_mscs_data.ipynb', 'r') as f:
    nb = nbf.read(f, as_version=4)

for cell in nb.cells:
    if cell.cell_type == 'code':
        if 'import seaborn as sns\n' in cell.source:
            cell.source = cell.source.replace('import seaborn as sns\n', '')

with open('analyze_mscs_data.ipynb', 'w') as f:
    nbf.write(nb, f)
