import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os 

load_dotenv()
# Load environment variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Load model
model = SentenceTransformer("intfloat/e5-base-v2")

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cur = conn.cursor()

def search_faq(query, top_k=3):
    # Embed the query with correct prefix
    embedding = model.encode(f"query: {query}", normalize_embeddings=True)

    # Convert to PostgreSQL-compatible string
    embedding_str = "[" + ",".join([f"{x:.6f}" for x in embedding]) + "]"

    # Search using cosine similarity (vector extension uses <-> for distance)
    cur.execute(f"""
        SELECT question, answer, 1 - (embedding <#> %s) AS similarity
        FROM faqs
        ORDER BY embedding <#> %s
        LIMIT %s;
    """, (embedding_str, embedding_str, top_k))

    results = cur.fetchall()
    for i, (q, a, score) in enumerate(results, 1):
        print(f"\nResult {i} (Score: {score:.4f})")
        print(f"Q: {q}")
        print(f"A: {a}")

# Example usage
while not "exit" in (user_input := input("Enter your question (or type 'exit' to quit): ")).lower():
    search_faq(user_input)
