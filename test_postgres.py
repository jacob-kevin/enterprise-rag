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
 
cursor.execute("SELECT * FROM employees")
 
rows = cursor.fetchall()
 
for row in rows:
    print(row)
 
cursor.close()
conn.close()    