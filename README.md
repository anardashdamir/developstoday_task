# Cocktail Advisor RAG System
## Notes:
- This task requires additional time to improve performance. First, we need a better embedding model to enhance the quality of vector representations. Alternatively, we could use a BM25 retriever or create one-hot encoded vectors using an LLM again, though this approach is not cost-efficient. My initial choice was to use an encoder model, but it has failed to retrieve data accurately. To address this, the model needs fine-tuning to better identify or differentiate cocktails. One of the most effective fine-tuning methods in this domain is Multiple Negatives Ranking with a custom Batch sampler(No similar drinks in the same batch). However, as mentioned earlier, this process requires more time.

## 🛠️ Prerequisites

- Python 3.8+
- [Together AI API Key](https://together.ai/) for LLM access
- [Pinecone API Key](https://www.pinecone.io/) for vector database

## 📦 Installation

1. **Clone the repository**

```bash
git clone https://github.com/anardashdamir/developstoday_task.git
cd developstoday_task
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

1. **Enviroment**
I have pushed .env to as you don't have my pinecode api key.

2. **Create necessary directories**



## 🚀 Running the Application


### Start the development server

```bash
uvicorn main:app
```
The API will be available at http://localhost:8000
