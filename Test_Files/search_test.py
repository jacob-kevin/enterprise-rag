import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

load_dotenv()

SEARCH_ENDPOINT=os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY=os.getenv("SEARCH_KEY")
INDEX_NAME=os.getenv("INDEX_NAME")

client = SearchClient(
    endpoint = SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_KEY)
)

query = input("WRITE YOUR QUERY:::")

results = client.search(search_text=query, top=5)

print("\nTOP RESULTS\n")
print("="*50)

for i,result in enumerate(results, start=1):
    print("Result ",i)
    print("-"*50)

    for key, value in result.items():
        if key != "text_vector":
            print(key,":",value)

    print()