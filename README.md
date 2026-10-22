# GridGuide

GridGuide is a bilingual AI assistant that helps power-grid engineers and power traders find and understand Indian electricity regulations. It uses regulatory documents published by the Central Electricity Regulatory Commission (CERC) to provide relevant answers in English or Hindi, with references to the original clauses.

## Problem

Power-grid engineers and power traders often need to refer to lengthy regulatory documents to clarify rules related to scheduling, deviation charges and grid operations. Finding the correct clause can be time-consuming, especially when regulations are amended or the user prefers Hindi while the official documents are in English. GridGuide aims to make this information easier to find and understand by providing clear answers supported by relevant regulatory references.

## Who it is for

- Shift engineers at State Load Despatch Centres handling electricity scheduling.
- Power traders who need to understand and verify applicable grid regulations.

## Signature feature

A bilingual answer card that provides an explanation in Hindi or English alongside the exact English regulatory clause and its reference.

## Hardest problem (my interview story)

The main technical challenge is cross-language retrieval: finding the correct English regulatory clauses when users ask questions in Hindi. GridGuide aims to address this using multilingual embeddings and retrieval evaluation, while presenting the relevant source clause alongside the answer.

## Dataset

| Source | Link | Documents | Pages | Licence / terms |
|---|---|---|---|---|
| Central Electricity Regulatory Commission (CERC) | [cercind.gov.in](https://cercind.gov.in/) | Indian Electricity Grid Code and relevant regulations and amendments | To be recorded during ingestion | Officially published regulatory documents; verify the applicable terms for each document |

**Target dataset:** At least 800 pages of relevant regulatory material. Actual document and page counts will be updated as the dataset is collected and processed.

## 10 real questions

The initial evaluation questions cover grid-code requirements, scheduling, deviation settlement and related regulations.

See [`docs/QUESTIONS.md`](docs/QUESTIONS.md) for the question set.

## Run it

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements-dev.txt
```

### 3. Configure environment variables

macOS/Linux:

```bash
cp .env.example .env
```

Windows:

```powershell
copy .env.example .env
```

Add the required configuration values to `.env` as specified by the project.

### 4. Start the application

```bash
uvicorn app.main:app --reload
```

### 5. Check the health endpoint

```bash
curl http://localhost:8000/health
```

## Live link

To be added in Week 2 after deployment.

## Project status

GridGuide is being developed as a 12-week project, progressing from a regulation-focused retrieval-augmented generation (RAG) application to a supervised AI agent that can prepare responses with supporting regulatory references.

