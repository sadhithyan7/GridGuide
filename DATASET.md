# Dataset

Run the downloader from the repository root:

```powershell
python -m app.tools.download .\urls.txt
```

Source files are stored in `data/raw/`. The manifest records each source URL,
file size, checksum, and download date. Review licensing terms for each file.

| File | Source URL | Pages | Licence / terms | Downloaded on |
|---|---|---|---|---|
| See `data/manifest.csv` | CERC links from [`urls.txt`](urls.txt) | To be measured | Verify terms for each document | In manifest |

Full data lives in `data/raw/` (not committed). A 2–3 file sample is in `data/sample/`.
