# Setup Instructions

## Step 1: Environment Setup

### 1.1 Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Unix/MacOS
python -m venv venv
source venv/bin/activate
```

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.3 Configure Environment Variables

1. Copy `.env.example` to `.env`:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Unix/MacOS
```

2. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Step 2: Build Vector Store

Run the ingestion pipeline to process policy documents and build the vector store:

```bash
python src/ingestion/pipeline.py
```

This will:
- Load all 12 policy documents from `data/policies/`
- Split them into chunks (~800 characters each)
- Generate embeddings using OpenAI
- Store in ChromaDB at `./chroma_db/`

Expected output:
```
============================================================
Starting Document Ingestion Pipeline
============================================================

[Step 1/3] Loading policy documents...
Loaded 12 policy documents

[Step 2/3] Chunking documents...
Created XXX chunks from 12 documents

[Step 3/3] Adding chunks to vector store...
Successfully added XXX chunks to vector store
Total documents in collection: XXX

============================================================
Ingestion Pipeline Complete!
============================================================
```

## Step 3: Test Retrieval

Verify the vector store is working:

```bash
python test_retrieval.py
```

This will run sample queries and show retrieved policy sections.

## Step 4: Run the Agent System

(Coming next - after agents are implemented)

```bash
python src/main.py
```

## Troubleshooting

### Issue: "No module named 'chromadb'"
**Solution**: Make sure you've installed dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "OPENAI_API_KEY not found"
**Solution**: 
1. Create `.env` file from `.env.example`
2. Add your actual OpenAI API key

### Issue: "Policies directory not found"
**Solution**: Make sure you're running commands from the project root directory where `data/policies/` exists.

### Issue: ChromaDB errors
**Solution**: Delete the `chroma_db/` directory and run ingestion again:
```bash
# Windows
rmdir /s chroma_db
# Unix/MacOS
rm -rf chroma_db

python src/ingestion/pipeline.py
```

## Next Steps

After successful setup:
1. ✅ Vector store built
2. ⏭️ Implement agents (Triage, Retriever, Resolution, Compliance)
3. ⏭️ Create orchestration system
4. ⏭️ Add test cases and evaluation
