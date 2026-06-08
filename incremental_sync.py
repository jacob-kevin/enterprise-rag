import json
import os
from dotenv import load_dotenv
 
import psycopg2
 
from openai import AzureOpenAI
 
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
 
 
# ==================================
# Load ENV
# ==================================
 
load_dotenv()
 
AOAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
AOAI_KEY = os.getenv("OPENAI_KEY")
AOAI_API_VERSION = os.getenv("AOAI_API_VERSION")
 
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")

INDEX_NAME = os.getenv("INDEX_NAME_SQL")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# ==================================
# Azure OpenAI Client
# ==================================
 
aoai_client = AzureOpenAI(
    azure_endpoint=AOAI_ENDPOINT,
    api_key=AOAI_KEY,
    api_version=AOAI_API_VERSION
)
 
 
# ==================================
# Azure Search Client
# ==================================
 
search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_KEY)
)
 
 
# ==================================
# Read Sync State
# ==================================
 
with open("sync_state.json", "r") as f:
    sync_state = json.load(f)
 
last_sync_time = sync_state["last_sync_time"]
 
print(f"\nLast Sync Time: {last_sync_time}")
 
 
# ==================================
# PostgreSQL Connection
# ==================================
 
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="enterprise_rag",
    user="postgres",
    password=POSTGRES_PASSWORD
)
 
cursor = conn.cursor()
 
 
# ==================================
# Get Changed Employees
# ==================================
 
cursor.execute(
    """
    SELECT
        employee_id,
        first_name,
        last_name,
        email,
        salary,
        last_modified
    FROM employees
    WHERE last_modified > %s
    ORDER BY last_modified
    """,
    (last_sync_time,)
)
 
rows = cursor.fetchall()
 
print(f"Changed Rows Found: {len(rows)}")
 
 
# ==================================
# Build Documents + Embeddings
# ==================================
 
documents = []
 
for row in rows:
 
    (
        employee_id,
        first_name,
        last_name,
        email,
        salary,
        last_modified
    ) = row
 
    content = f"""
Employee ID: {employee_id}
First Name: {first_name}
Last Name: {last_name}
Email: {email}
Salary: {salary}
"""
 
    embedding_response = aoai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=content
    )
 
    embedding = embedding_response.data[0].embedding
    print(f"Embedding Length = {len(embedding)}")
    print(embedding[:5])
 
    document = {
        "id": str(employee_id),
        "employee_id": str(employee_id),
        "content": content,
        "content_vector": embedding
    }
 
    documents.append(document)
 
print(f"Documents Prepared: {len(documents)}")
 
 
# ==================================
# Upload To Azure Search
# ==================================
 
if documents:
 
    result = search_client.merge_or_upload_documents(
        documents=documents
    )
 
    print(f"Uploaded: {len(result)} documents")
 
else:
 
    print("No changes found. Nothing uploaded.")
 
 
# ==================================
# Update Sync State
# ==================================
 
cursor.execute("""
SELECT MAX(last_modified)
FROM employees
""")
 
latest_timestamp = cursor.fetchone()[0]
 
if latest_timestamp:
 
    with open("sync_state.json", "w") as f:
        json.dump(
            {
                "last_sync_time": latest_timestamp.isoformat()
            },
            f,
            indent=4
        )
 
    print(
        f"New Sync Time Saved: "
        f"{latest_timestamp.isoformat()}"
    )
 
 
# ==================================
# Cleanup
# ==================================
 
cursor.close()
conn.close()
 
print("\nSync completed successfully.")
 