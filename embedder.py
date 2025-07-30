from sentence_transformers import SentenceTransformer
import psycopg2
import hashlib
import json

from dotenv import load_dotenv
import os 

load_dotenv()
# Load environment variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Load the model
model = SentenceTransformer("intfloat/e5-base-v2")

# Function to hash answers
def hash_text(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

# Example FAQs
with open('faqs_parsed.json', 'r') as f:
    faqs = json.load(f)

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cur = conn.cursor()
print("Connected to PostgreSQL database.")

# Step 1: Create table if it doesn't exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS faqs (
        id SERIAL PRIMARY KEY,
        question TEXT UNIQUE,
        answer TEXT,
        answer_hash TEXT,
        embedding VECTOR(768)
    );
""")
conn.commit()

# Step 2: Insert/update logic
for faq in faqs:
    question = faq["question"]
    answer = faq["answer"]
    answer_hash = hash_text(answer)

    # Check if question exists
    cur.execute("SELECT id, answer_hash FROM faqs WHERE question = %s", (question,))
    result = cur.fetchone()

    if result:
        faq_id, existing_hash = result
        if existing_hash == answer_hash:
            print(f"✅ Already up-to-date: {question}")
            continue
        else:
            print(f"🔄 Updating: {question}")
            embedding = model.encode(f"question: {question} answer: {answer}", normalize_embeddings=True).tolist()
            cur.execute(
                "UPDATE faqs SET answer = %s, answer_hash = %s, embedding = %s WHERE id = %s",
                (answer, answer_hash, embedding, faq_id)
            )
    else:
        print(f"➕ Inserting new: {question}")
        embedding = model.encode(f"question: {question} answer: {answer}", normalize_embeddings=True).tolist()
        cur.execute(
            "INSERT INTO faqs (question, answer, answer_hash, embedding) VALUES (%s, %s, %s, %s)",
            (question, answer, answer_hash, embedding)
        )

conn.commit()
cur.close()
conn.close()
