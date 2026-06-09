import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
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
LIMIT 5
""")
 
rows = cursor.fetchall()
 
for row in rows:
 
    employee_id, first_name, last_name, email, salary = row
 
    content = f"""
Employee {employee_id}.
Name: {first_name} {last_name}.
Email: {email}.
Salary: {salary}.
"""
 
    document = {
        "id": str(employee_id),
        "employee_id": str(employee_id),
        "content": content
    }
 
    print(document)
    print("-" * 50)
 
cursor.close()
conn.close()