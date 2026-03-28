# E-commerce Support Resolution Agent

A multi-agent RAG system for resolving customer support tickets using policy documents with strong controls against hallucination.

## 🎯 Overview

This system uses 4 specialized AI agents to process customer support tickets:
1. **Triage Agent** - Classifies issues and identifies missing information
2. **Policy Retriever Agent** - Finds relevant policies with citations
3. **Resolution Writer Agent** - Drafts customer responses
4. **Compliance/Safety Agent** - Ensures accuracy and safety

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key (or other LLM provider)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ecommerce-support-agent.git
cd ecommerce-support-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Setup

1. Create a `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
```

2. Run the system:
```bash
python src/main.py
```

## 📁 Project Structure

```
ecommerce-support-agent/
├── src/
│   ├── agents/              # Agent implementations
│   ├── ingestion/           # Document processing
│   ├── retrieval/           # Vector store & search
│   ├── orchestration/       # Agent coordination
│   └── main.py             # Entry point
├── data/
│   ├── policies/           # Policy documents
│   ├── test_cases/         # Test tickets
│   └── sources.md          # Data sources
├── evaluation/
│   ├── test_set.json       # Test cases
│   └── results.json        # Evaluation results
├── examples/               # Sample outputs
├── requirements.txt
└── README.md
```

## 🧪 Running Tests

```bash
python src/evaluation/run_evaluation.py
```

## 📊 Evaluation Results

- **Citation Coverage Rate**: TBD
- **Unsupported Claim Rate**: TBD
- **Correct Escalation Rate**: TBD

## 🛠️ Technology Stack

- **Framework**: CrewAI
- **Vector Store**: ChromaDB
- **Embeddings**: OpenAI text-embedding-3-small
- **LLM**: GPT-4
- **Language**: Python 3.9+

## 📝 License

MIT License
