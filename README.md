# 🧠 FAQ Semantic Search with pgvector + Sentence Transformers

This project is a semantic search system for FAQs using PostgreSQL with pgvector, sentence embeddings from `intfloat/e5-base-v2`, and efficient batch processing and retrieval.

---

## 🚀 Features

- Stores FAQ data with semantic embeddings in PostgreSQL
- Uses `pgvector` for fast similarity search
- Automatically inserts/updates FAQs if changed
- Embeds only the **questions** (OpenAI style)
- Cached transformer model for fast startup and inference
- Batch embedding support for scalability

---

## 🏗️ Tech Stack

- 🧠 [SentenceTransformers](https://www.sbert.net/) (`intfloat/e5-base-v2`)
- 🐘 PostgreSQL with `pgvector` extension
- 🐍 Python with `psycopg2` and `sentence-transformers`

