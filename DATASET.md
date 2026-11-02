# Dataset

Run the downloader from the repository root:

```powershell
python -m app.tools.download .\urls.txt
```

Source files are stored in `data/raw/`. The manifest records each source URL,
file size, checksum, and download date. Review licensing terms for each file.

## Source

| Field | Detail |
|---|---|
| Publisher | Central Electricity Regulatory Commission (CERC) |
| URL | [cercind.gov.in](https://cercind.gov.in/) |
| Licence / terms | Officially published regulatory documents; publicly available on the CERC website. Verify the applicable terms for each document before use. |
| Personal data | None — all documents are regulations, orders, and explanatory memoranda. |
| robots.txt | Respected by the downloader (2-second delay, same-site only). |

## Size

| Metric | Count |
|---|---|
| Total files downloaded | 733 |
| PDF files | 730 |
| Other (DOCX etc.) | 3 |
| Total size on disk | ~427 MB |
| Key regulation pages counted | 557+ pages across 10 core documents |

Minimum target: 800+ pages. Page count across all 730 PDFs will be measured in Week 3
during the parsing and chunking step.

## Key documents

| File | Source URL | Pages | Document type |
|---|---|---|---|
| `Draft-IEGC-07062022.pdf` | cercind.gov.in/Regulations/Draft-IEGC-07062022.pdf | 188 | Indian Electricity Grid Code (draft 2022) |
| `OA.pdf` | cercind.gov.in | 200 | Open Access Regulations |
| `D_GNA.pdf` | cercind.gov.in | 67 | General Network Access Regulations |
| `GNA.pdf` | cercind.gov.in | 37 | GNA Regulations (notification) |
| `DR_IEGC-2ndAmnd.pdf` | cercind.gov.in | 22 | IEGC 2nd Amendment |
| `EM-DSMRegulations.pdf` | cercind.gov.in | 18 | DSM Regulations Explanatory Memorandum |

Full manifest: `data/manifest.csv` (every file, URL, date, size, SHA-256).

## Sample files

Two representative files are committed to `data/sample/` for review:

- `data/sample/Draft-IEGC-07062022.pdf` — the main Grid Code draft (188 pages)
- `data/sample/OA.pdf` — Open Access Regulations (200 pages)

## How to rebuild data/raw/

```powershell
# From the repository root
python -m app.tools.download .\urls.txt
```

The downloader skips files already in the manifest, so re-running is safe.
