from __future__ import annotations

import hashlib
import re
import shutil
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd
from bs4 import BeautifulSoup
from pypdf import PdfReader


def find_repo_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "data" / "source_manifest.csv").exists():
            return candidate
    raise FileNotFoundError("Could not find data/source_manifest.csv")


def load_manifest(repo_root: Path) -> pd.DataFrame:
    return pd.read_csv(repo_root / "data" / "source_manifest.csv", keep_default_na=False)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def signature(path: Path) -> str:
    return path.read_bytes()[:8].hex(" ")


def download_sources(
    manifest: pd.DataFrame,
    repo_root: Path,
    *,
    force: bool = False,
) -> pd.DataFrame:
    """Download missing source files and verify each file against the manifest."""
    records: list[dict[str, object]] = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; GNU-RAG-research/1.0)"}

    for row in manifest.itertuples(index=False):
        target = repo_root / "data" / row.local_path
        target.parent.mkdir(parents=True, exist_ok=True)
        status = "existing"
        error = ""

        valid_existing = (
            target.exists()
            and target.stat().st_size == int(row.bytes)
            and sha256(target) == row.sha256
        )

        if force or not valid_existing:
            temporary = target.with_suffix(target.suffix + ".part")
            try:
                request = urllib.request.Request(row.download_url, headers=headers)
                with urllib.request.urlopen(request, timeout=60) as response, temporary.open("wb") as output:
                    shutil.copyfileobj(response, output)
                if temporary.stat().st_size != int(row.bytes):
                    raise ValueError("downloaded size differs from manifest")
                if sha256(temporary) != row.sha256:
                    raise ValueError("downloaded SHA-256 differs from manifest")
                temporary.replace(target)
                status = "downloaded"
            except Exception as exc:
                temporary.unlink(missing_ok=True)
                status = "error"
                error = f"{type(exc).__name__}: {exc}"

        exists = target.exists()
        records.append(
            {
                "file": row.local_path,
                "status": status,
                "exists": exists,
                "size_ok": exists and target.stat().st_size == int(row.bytes),
                "sha256_ok": exists and sha256(target) == row.sha256,
                "error": error,
            }
        )
    return pd.DataFrame(records)


def validate_sources(manifest: pd.DataFrame, repo_root: Path) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for row in manifest.itertuples(index=False):
        path = repo_root / "data" / row.local_path
        exists = path.exists()
        records.append(
            {
                "file": row.local_path,
                "exists": exists,
                "size_ok": exists and path.stat().st_size == int(row.bytes),
                "sha256_ok": exists and sha256(path) == row.sha256,
                "signature": signature(path) if exists else "",
            }
        )
    return pd.DataFrame(records)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_html(path: Path) -> str:
    soup = BeautifulSoup(path.read_bytes(), "html.parser")
    for node in soup(["script", "style", "noscript"]):
        node.decompose()
    return normalize_text(soup.get_text(" ", strip=True))


def extract_pdf(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    text = " ".join(page.extract_text() or "" for page in reader.pages)
    return normalize_text(text), len(reader.pages)


def extract_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    return normalize_text(" ".join(root.itertext()))


def extract_hwpx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        section_names = sorted(
            name
            for name in archive.namelist()
            if name.lower().startswith("contents/section") and name.lower().endswith(".xml")
        )
        text: list[str] = []
        for name in section_names:
            text.extend(ET.fromstring(archive.read(name)).itertext())
    return normalize_text(" ".join(text))


def extract(path: Path) -> tuple[str, str, int | None]:
    suffix = path.suffix.lower()
    if suffix == ".html":
        return extract_html(path), "extracted", None
    if suffix == ".pdf":
        text, pages = extract_pdf(path)
        return text, "extracted", pages
    if suffix == ".docx":
        return extract_docx(path), "extracted", None
    if suffix == ".hwpx":
        return extract_hwpx(path), "extracted", None
    if suffix == ".hwp":
        return "", "binary HWP validated; conversion required", None
    return "", f"unsupported extension: {suffix}", None


def extract_sources(manifest: pd.DataFrame, repo_root: Path) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for row in manifest.itertuples(index=False):
        path = repo_root / "data" / row.local_path
        text = ""
        status = "missing"
        pages = None
        error = ""
        if path.exists():
            try:
                text, status, pages = extract(path)
            except Exception as exc:
                status = "failed"
                error = f"{type(exc).__name__}: {exc}"
        records.append(
            {
                "file": row.local_path,
                "extraction": status,
                "pages": pages,
                "text_chars": len(text),
                "preview": text[:140],
                "error": error,
            }
        )
    return pd.DataFrame(records)


def unique_articles(text: str) -> set[str]:
    # The official HTML currently decodes article labels either as Korean or legacy mojibake.
    return set(re.findall(r"(?:제|Á¦)\d+(?:조|Á¶)(?:의\d+|ÀÇ\d+)?", text))
