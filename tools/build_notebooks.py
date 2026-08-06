from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"


def markdown(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str):
    return nbf.v4.new_code_cell(text.strip())


BOOTSTRAP = """
from pathlib import Path
import sys

for candidate in (Path.cwd().resolve(), *Path.cwd().resolve().parents):
    if (candidate / 'data' / 'source_manifest.csv').exists():
        REPO_ROOT = candidate
        break
else:
    raise FileNotFoundError('Could not find data/source_manifest.csv')

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from IPython.display import display
from src.pilot_corpus import load_manifest

manifest = load_manifest(REPO_ROOT)
print(f'Manifest entries: {len(manifest)}')
"""


specs = {
    "00_download_sources.ipynb": [
        markdown("""
# 00. Download Source Documents

Download only missing or invalid source files from the official URLs recorded in the manifest. Existing valid files are reused. Every downloaded file is checked by byte size and SHA-256.

No LLM, API key, or paid token is required.
"""),
        code(BOOTSTRAP + "\nfrom src.pilot_corpus import download_sources"),
        code("""
download_result = download_sources(manifest, REPO_ROOT)
display(download_result)

assert download_result['exists'].all(), 'One or more source files are missing.'
assert download_result['size_ok'].all(), 'One or more source sizes differ from the manifest.'
assert download_result['sha256_ok'].all(), 'One or more source hashes differ from the manifest.'
assert not (download_result['status'] == 'error').any(), 'One or more downloads failed.'

print(download_result['status'].value_counts().to_string())
print('All source documents are ready.')
"""),
    ],
    "01_validate_sources.ipynb": [
        markdown("""
# 01. Validate Source Integrity

Validate file presence, byte size, SHA-256, and file signatures independently from downloading.

No LLM, API key, or paid token is required.
"""),
        code(BOOTSTRAP + "\nfrom src.pilot_corpus import validate_sources"),
        code("""
validation = validate_sources(manifest, REPO_ROOT)
display(validation)

summary = {
    'files present': int(validation['exists'].sum()),
    'size checks passed': int(validation['size_ok'].sum()),
    'SHA-256 checks passed': int(validation['sha256_ok'].sum()),
}
display(summary)

assert validation['exists'].all(), 'One or more raw files are missing.'
assert validation['size_ok'].all(), 'One or more file sizes differ from the manifest.'
assert validation['sha256_ok'].all(), 'One or more SHA-256 digests differ from the manifest.'
print('All integrity assertions passed.')
"""),
    ],
    "02_extract_source_text.ipynb": [
        markdown("""
# 02. Extract Source Text

Extract text from HTML, PDF, DOCX, and HWPX documents and show only short previews. The legacy binary HWP file is signature-validated in Notebook 01 and is clearly marked as requiring a separate converter.

No LLM, API key, or paid token is required.
"""),
        code(BOOTSTRAP + "\nfrom src.pilot_corpus import extract_sources"),
        code("""
extraction = extract_sources(manifest, REPO_ROOT)
display(extraction[['file', 'extraction', 'pages', 'text_chars']])

summary = {
    'text extraction succeeded': int((extraction['extraction'] == 'extracted').sum()),
    'legacy HWP conversion required': int(extraction['extraction'].str.contains('conversion required').sum()),
    'extraction failures': int((extraction['extraction'] == 'failed').sum()),
}
display(summary)

assert not (extraction['extraction'] == 'failed').any(), 'One or more extractors failed.'
print('Supported source formats were extracted successfully.')
"""),
        code("""
display(extraction.loc[extraction['text_chars'] > 0, ['file', 'text_chars', 'preview']])
"""),
    ],
    "03_compare_regulation_versions.ipynb": [
        markdown("""
# 03. Compare Regulation Versions

Run the first time-aware corpus test by comparing the normalized official 2024 and 2026 Graduate School Academic Operation Regulation texts. This is a corpus-level check, not yet a provision-level legal diff.

No LLM, API key, or paid token is required.
"""),
        code(BOOTSTRAP + "\nimport pandas as pd\nfrom src.pilot_corpus import extract_html, unique_articles"),
        code("""
old_path = REPO_ROOT / 'data' / 'raw' / 'law_go_kr' / '02_graduate_academic_operation_2024.html'
current_path = REPO_ROOT / 'data' / 'raw' / 'law_go_kr' / '03_graduate_academic_operation_current_2026.html'

old_text = extract_html(old_path)
current_text = extract_html(current_path)
old_articles = unique_articles(old_text)
current_articles = unique_articles(current_text)

comparison = pd.DataFrame([{
    '2024_text_chars': len(old_text),
    '2026_text_chars': len(current_text),
    '2024_unique_articles': len(old_articles),
    '2026_unique_articles': len(current_articles),
    'articles_only_in_2024': ', '.join(sorted(old_articles - current_articles)),
    'articles_only_in_2026': ', '.join(sorted(current_articles - old_articles)),
    'exact_text_equal': old_text == current_text,
}])
display(comparison)

assert old_text != current_text, 'The historical and current source texts unexpectedly match.'
print('The official versions are distinct and ready for a temporal-retrieval experiment.')
"""),
    ],
}


NOTEBOOKS.mkdir(exist_ok=True)
for name, cells in specs.items():
    notebook = nbf.v4.new_notebook(cells=cells)
    notebook.metadata.kernelspec = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook.metadata.language_info = {"name": "python", "version": "3"}
    nbf.write(notebook, NOTEBOOKS / name)
    print(f"Wrote {name}")
