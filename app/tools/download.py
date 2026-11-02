"""Download documents linked from the URLs in a seed file.

Run from the repository root:
    python -m app.tools.download urls.txt
"""

import csv
import hashlib
import re
import sys
import time
from collections import deque
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests

RAW = Path("data/raw")
MANIFEST = Path("data/manifest.csv")
DELAY = 2
MAX_PAGES = 1000
HEADERS = {"User-Agent": "GridGuideDatasetDownloader/1.0"}
DOCUMENT_EXTENSIONS = {".csv", ".doc", ".docx", ".json", ".pdf", ".xls", ".xlsx", ".xml", ".zip"}


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self.links.extend(value for key, value in attrs if key.lower() == "href" and value)


def normalise(url):
    return urldefrag(url.strip())[0]


def is_document(url, content_type):
    suffix = Path(urlparse(url).path.lower()).suffix
    return suffix in DOCUMENT_EXTENSIONS or "pdf" in content_type.lower()


def filename(url):
    name = Path(urlparse(url).path).name or "index.html"
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name[:180]


def allowed(url, robots):
    parsed = urlparse(url)
    root = f"{parsed.scheme}://{parsed.netloc}"
    if root not in robots:
        parser = RobotFileParser(f"{root}/robots.txt")
        try:
            parser.read()
        except OSError:
            parser = None
        robots[root] = parser
    return robots[root] is None or robots[root].can_fetch(HEADERS["User-Agent"], url)


def main(list_file="urls.txt"):
    with open(list_file, encoding="utf-8") as handle:
        seeds = [
            normalise(line)
            for line in handle
            if line.strip() and not line.lstrip().startswith("#")
        ]
    if any(urlparse(url).scheme not in {"http", "https"} for url in seeds):
        raise ValueError("urls.txt must contain only HTTP(S) URLs")

    RAW.mkdir(parents=True, exist_ok=True)
    manifest_exists = MANIFEST.exists()
    downloaded = set()
    if manifest_exists:
        with MANIFEST.open(newline="", encoding="utf-8") as handle:
            downloaded = {row["source_url"] for row in csv.DictReader(handle)}

    hosts = {urlparse(url).netloc.lower() for url in seeds}
    queue, queued, visited = deque(seeds), set(seeds), set()
    robots = {}
    with MANIFEST.open("a", newline="", encoding="utf-8") as handle:
        log = csv.writer(handle)
        if not manifest_exists:
            log.writerow(["file", "source_url", "downloaded_on", "bytes", "sha256"])
        with requests.Session() as session:
            session.headers.update(HEADERS)
            while queue and len(visited) < MAX_PAGES:
                url = queue.popleft()
                visited.add(url)
                if not allowed(url, robots):
                    print("blocked by robots.txt:", url)
                    continue
                try:
                    response = session.get(url, timeout=30)
                    response.raise_for_status()
                except requests.RequestException as error:
                    print(f"failed: {url} ({error})", file=sys.stderr)
                    continue

                content_type = response.headers.get("Content-Type", "")
                if url not in downloaded and is_document(url, content_type):
                    path = RAW / filename(url)
                    if path.exists():
                        path = RAW / f"{path.stem}_{len(downloaded)}{path.suffix}"
                    path.write_bytes(response.content)
                    digest = hashlib.sha256(response.content).hexdigest()
                    log.writerow([path, url, date.today().isoformat(), len(response.content), digest])
                    handle.flush()
                    downloaded.add(url)
                    print("saved", path)

                if "html" in content_type.lower():
                    parser = LinkParser()
                    parser.feed(response.text)
                    for link in parser.links:
                        child = normalise(urljoin(url, link))
                        if (
                            urlparse(child).scheme in {"http", "https"}
                            and urlparse(child).netloc.lower() in hosts
                            and child not in queued
                        ):
                            queue.append(child)
                            queued.add(child)
                time.sleep(DELAY)

    print(f"visited {len(visited)} pages; downloaded {len(downloaded)} file(s)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "urls.txt")
