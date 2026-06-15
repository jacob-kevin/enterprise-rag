import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv
from openai import AzureOpenAI

# =========================
# Load Environment Variables
# =========================

load_dotenv()

SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
INDEX_NAME = os.getenv("INDEX_NAME_PDF")

OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
OPENAI_KEY = os.getenv("OPENAI_KEY")
GPT_DEPLOYMENT = 'gpt-5-mini'

# =========================
# Azure AI Search Client
# =========================

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_KEY),
)

# =========================
# Azure OpenAI Client
# =========================

aoai_client = AzureOpenAI(
    api_key=OPENAI_KEY,
    azure_endpoint=OPENAI_ENDPOINT,
    api_version="2024-02-15-preview",
)

print("--- RUNNING DIAGNOSTIC CHECK ---")
print(f"Endpoint:   {OPENAI_ENDPOINT}")
print(f"Deployment: {GPT_DEPLOYMENT}")
print("Testing request structure...")

# =========================
# Main Loop
# =========================

while True:
    query = input("\nAsk a question (or type 'exit'): ")

    if query.lower() == "exit":
        break

    # Search Azure AI Search
    results = search_client.search(search_text=query, top=5)

    context = ""
    citations = []

    for result in results:
        chunk = result.get("chunk", "")

        # Depending on your index this could be:
        # title
        # parent_id
        # metadata_storage_name
        source = (
            result.get("title") or result.get("parent_id") or "Unknown Source"
        )

        context += f"\n\n{chunk}"
        citations.append(source)

    # Generate answer using GPT
    response = aoai_client.chat.completions.create(
        model=GPT_DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an enterprise knowledge assistant.\n\n"
                    "Answer ONLY from the provided context.\n\n"
                    "If the answer is not present in the context, say:\n"
                    "'I could not find that information in the indexed "
                    "documents.'"
                ),
            },
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{query}"},
        ],
        
        temperature=1,
    )

    answer = response.choices[0].message.content

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)

    print("\nSOURCES")
    print("=" * 80)

    for source in set(citations):
        print(f"- {source}")
