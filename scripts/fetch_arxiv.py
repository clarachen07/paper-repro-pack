#!/usr/bin/env python3
"""Fetch an arXiv paper for reproduction analysis: PDF, LaTeX source, extracted text.

Usage:
    python3 fetch_arxiv.py <arxiv-id-or-url> [--out DIR]

Accepts: 2106.09685, 2106.09685v3, cs/0301012,
         https://arxiv.org/abs/2106.09685, arxiv.org/pdf/2106.09685v2

Creates (--out, default ./repro-<id>/):
    paper.pdf    the paper
    paper.txt    extracted text (pdftotext if installed, else pypdf)
    source/      LaTeX e-print source unpacked (absent if the deposit has none)
    MAIN.tex     pointer file naming the main .tex, when identifiable

Stdlib only. Be polite to arXiv: one request per artifact, no retries storm.
"""
import argparse
import gzip
import io
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

HEADERS = {"User-Agent": "paper-repro-report/1.2 (personal research helper)"}


def parse_arxiv_id(raw: str) -> str:
    s = raw.strip()
    s = re.sub(r"^https?://", "", s)
    s = re.sub(r"^(www\.|export\.)?arxiv\.org/", "", s)
    s = re.sub(r"^(abs|pdf|src|e-print)/", "", s)
    s = re.sub(r"\.pdf$", "", s)
    s = s.strip("/")
    if re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", s):
        return s
    if re.fullmatch(r"[a-z-]+(\.[A-Z]{2})?/\d{7}(v\d+)?", s):
        return s
    raise SystemExit(f"error: cannot parse an arXiv id from {raw!r}")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def extract_text(pdf_path: Path, txt_path: Path) -> str:
    """Returns the extractor used, or '' on failure."""
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        try:
            subprocess.run(
                [pdftotext, "-layout", str(pdf_path), str(txt_path)],
                check=True, capture_output=True, timeout=300,
            )
            if txt_path.exists() and txt_path.stat().st_size > 0:
                return "pdftotext"
        except (subprocess.SubprocessError, OSError):
            pass
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return ""
    try:
        reader = PdfReader(str(pdf_path))
        text = "\n\n".join((page.extract_text() or "") for page in reader.pages)
        txt_path.write_text(text, encoding="utf-8")
        return "pypdf" if text.strip() else ""
    except Exception as e:  # noqa: BLE001 — extraction is best-effort
        print(f"[warn] pypdf extraction failed: {e}", file=sys.stderr)
        return ""


def unpack_source(data: bytes, dest: Path) -> str:
    """Unpack an arXiv e-print payload; returns a description of what it was."""
    dest.mkdir(parents=True, exist_ok=True)
    if data[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(dest)
        return "zip archive"
    if data[:2] == b"\x1f\x8b" or data[:4] == b"\x1f\x9d":
        try:
            with tarfile.open(fileobj=io.BytesIO(data)) as t:
                t.extractall(dest)
            return "tar archive (gz/bz2-compressed)"
        except tarfile.TarError:
            raw = gzip.decompress(data)
            guess = "main.tex" if b"\\documentclass" in raw or b"\\begin{" in raw else "source.bin"
            (dest / guess).write_bytes(raw)
            return f"single gzip-compressed file -> source/{guess}"
    (dest / "main.tex").write_bytes(data)
    return "uncompressed single file (assumed TeX) -> source/main.tex"


def find_main_tex(source_dir: Path) -> Optional[Path]:
    candidates = sorted(source_dir.rglob("*.tex"))
    for tex in candidates:
        try:
            if "\\documentclass" in tex.read_text(errors="ignore"):
                return tex
        except OSError:
            continue
    return candidates[0] if candidates else None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paper", help="arXiv id or URL")
    ap.add_argument("--out", default=None, help="output dir (default ./repro-<id>/)")
    args = ap.parse_args()

    pid = parse_arxiv_id(args.paper)
    out = Path(args.out or f"repro-{pid.replace('/', '-')}")
    out.mkdir(parents=True, exist_ok=True)
    print(f"paper id: {pid}\nwork dir: {out.resolve()}")

    pdf_path = out / "paper.pdf"
    data = None
    for host in ("https://arxiv.org", "https://export.arxiv.org"):
        try:
            data = fetch(f"{host}/pdf/{pid}")
            if data[:5] == b"%PDF-":
                break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                sys.exit(f"error: no paper {pid} on arXiv (404) — check the id")
            print(f"[warn] {host} -> HTTP {e.code}", file=sys.stderr)
        except urllib.error.URLError as e:
            print(f"[warn] {host} unreachable: {e.reason}", file=sys.stderr)
    if not data or data[:5] != b"%PDF-":
        sys.exit("error: could not download a valid PDF from arXiv")
    pdf_path.write_bytes(data)
    print(f"[ok] paper.pdf ({len(data) // 1024} KB)")

    extractor = extract_text(pdf_path, out / "paper.txt")
    if extractor:
        print(f"[ok] paper.txt (via {extractor})")
    else:
        print("[warn] no text extractor available — install poppler (pdftotext) "
              "or `pip install pypdf`, or read the PDF directly")

    try:
        src = fetch(f"https://arxiv.org/e-print/{pid}")
        kind = unpack_source(src, out / "source")
        n_tex = len(list((out / "source").rglob("*.tex")))
        print(f"[ok] source/ ({kind}; {n_tex} .tex files)")
        main_tex = find_main_tex(out / "source")
        if main_tex:
            (out / "MAIN.tex").write_text(str(main_tex.resolve()) + "\n")
            print(f"[ok] main .tex: {main_tex.relative_to(out)}")
    except urllib.error.HTTPError as e:
        print(f"[warn] no e-print source (HTTP {e.code}) — proceeding without LaTeX")
    except urllib.error.URLError as e:
        print(f"[warn] e-print download failed: {e} — proceeding without LaTeX")

    print("done.")


if __name__ == "__main__":
    main()
