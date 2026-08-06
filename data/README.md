# Pilot Corpus

This directory records the first pilot corpus for the time-aware university-regulation RAG experiment.

## Local raw files

Raw HTML, HWP, HWPX, DOCX, and PDF files are stored under `data/raw/`. That directory is intentionally excluded from Git because redistribution conditions may differ by source and attachment. The files can be reproduced from `source_manifest.csv`.

## Corpus scope

The pilot corpus contains:

- Current Gyeongsang National University rules.
- Graduate School Academic Operation Regulations from 2024 and 2026.
- Current Graduate School Degree Conferral Regulations.
- Graduate School Curriculum Operation Guidelines.
- General Graduate School Thesis Qualification Examination Guidelines.
- Research Ethics Regulations.
- Thesis writing guidelines and Korean/English templates.
- The spring 2026 thesis-review notice and attached plan.
- The fall 2026 master's alternative-achievement notice, criteria, and forms.

The 2024 and 2026 versions of the Graduate School Academic Operation Regulations are intentionally retained together. They form the first version-conflict test case.

## Collection date

The files listed in the manifest were collected on August 6, 2026 (Asia/Seoul).

## Integrity

`source_manifest.csv` records the SHA-256 digest and byte size of every local raw file. These values should be recalculated whenever a source is downloaded again. A changed digest does not by itself prove that the regulation changed because a website may modify markup without modifying the provision text. Provision-level normalization and comparison are therefore required in the processing stage.

## Evidence policy

- A promulgated regulation is treated as normative evidence for its effective period.
- A university notice is treated as semester-specific operational evidence.
- A writing template or form is treated as explanatory or procedural material.
- Historical regulations remain searchable only for questions whose reference date falls within their effective period or for explicit amendment-history questions.
