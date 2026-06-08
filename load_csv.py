import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


# Read CSV
df = pd.read_csv("employees.csv")

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="enterprise_rag",
    user="postgres",
    password=POSTGRES_PASSWORD
)
 
cursor = conn.cursor()
 
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO employees
        (
            employee_id,
            first_name,
            last_name,
            email,
            salary
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (employee_id)
        DO NOTHING
    """,
    (
        int(row["EMPLOYEE_ID"]),
        row["FIRST_NAME"],
        row["LAST_NAME"],
        row["EMAIL"],
        float(row["SALARY"])
    ))
 
conn.commit()
 
print(f"Inserted {len(df)} rows")
 
cursor.close()
conn.close()