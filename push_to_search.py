import psycopg2
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import os
from dotenv import load_dotenv

load_dotenv()
# Azure AI Search
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
INDEX_NAME = os.getenv("INDEX_NAME_SQL")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_KEY)
)

# PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="enterprise_rag",
    user="postgres",
    password=POSTGRES_PASSWORD
)
 
cursor = conn.cursor()
 
cursor.execute("""
SELECT
    employee_id,
    first_name,
    last_name,
    email,
    salary
FROM employees
""")
 
rows = cursor.fetchall()
 
documents = []
 
for row in rows:
 
    employee_id, first_name, last_name, email, salary = row
 
    content = f"""
Employee ID: {employee_id}
Name: {first_name} {last_name}
Email: {email}
Salary: {salary}
"""
 
    documents.append({
        "id": str(employee_id),
        "employee_id": str(employee_id),
        "content": content
    })
 
print(f"Preparing {len(documents)} documents...")
 
result = search_client.upload_documents(documents)
 
print("Upload complete")
print(result)
 
cursor.close()
conn.close()