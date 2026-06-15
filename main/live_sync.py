import json
import os
import psycopg2
import select

from dotenv import load_dotenv
from openai import AzureOpenAI

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

load_dotenv()

# Azure OpenAI
#text-embedding-3-small
aoai_client = AzureOpenAI(
    azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
    api_key=os.getenv("OPENAI_KEY"),
    api_version=os.getenv("AOAI_API_VERSION")
)

# Azure Search

search_client = SearchClient(
    endpoint=os.getenv("SEARCH_ENDPOINT"),
    index_name=os.getenv("INDEX_NAME_SQL"),
    credential=AzureKeyCredential(
        os.getenv("SEARCH_KEY")
    )
)

# PostgreSQL

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)

conn.set_isolation_level(
    psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
)

cursor = conn.cursor()

cursor.execute("LISTEN employee_changes;")

print("Listening for employee changes...")

while True:

    if select.select([conn], [], [], 5) == ([], [], []):
        continue

    conn.poll()

    while conn.notifies:

        notify = conn.notifies.pop(0)

        employee_id = notify.payload

        print(
            f"\nEmployee changed: {employee_id}"
        )

        data_cursor = conn.cursor()

        data_cursor.execute(
            """
            SELECT
                employee_id,
                first_name,
                last_name,
                email,
                salary
            FROM employees
            WHERE employee_id=%s
            """,
            (employee_id,)
        )

        row = data_cursor.fetchone()

        if not row:
            continue

        employee_id, first_name, last_name, email, salary = row

        content = f"""
Employee ID: {employee_id}
First Name: {first_name}
Last Name: {last_name}
Email: {email}
Salary: {salary}
"""

        embedding_response = (
            aoai_client.embeddings.create(
                model=os.getenv("EMBEDDING_MODEL"),
                input=content
            )
        )

        embedding = (
            embedding_response
            .data[0]
            .embedding
        )

        document = {
            "id": str(employee_id),
            "employee_id": str(employee_id),
            "content": content,
            "content_vector": embedding
        }

        search_client.merge_or_upload_documents(
            [document]
        )

        print(
            f"Updated Azure Search "
            f"for employee {employee_id}"
        )