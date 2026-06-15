from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv
import os

load_dotenv()

# ==========================
# Azure OpenAI
# ==========================

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_KEY"),
    azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
    api_version=os.getenv("AOAI_API_VERSION")
)

# ==========================
# Foundry Agent Client
# ==========================

project_client = AIProjectClient(
    endpoint="https://memory-byters-openai.services.ai.azure.com/api/projects/memory-byters-openai-project",
    credential=DefaultAzureCredential(),
)

agent_client = project_client.get_openai_client()

# ==========================
# Query Classifier
# ==========================

def classify_query(query: str) -> str:

    response = client.responses.create(
        model="gpt-5-mini",
        input=f"""
                You are a query complexity classifier.

                Classify the user query as either:

                SIMPLE
                - Single lookup
                - Single fact retrieval
                - Basic summarization

                COMPLEX
                - Requires analysis
                - Requires comparison
                - Requires reasoning
                - Requires combining multiple sources
                - Requires decomposition
                - Cross-document reasoning
                - Cross-index reasoning
                - Multi-step investigation

                Return ONLY:

                SIMPLE

                or

                COMPLEX

                Query:
                {query}
                """
    )

    return response.output_text.strip()

# ==========================
# Agent Invocation
# ==========================

def call_agent(agent_name: str, version: str, query: str):

    response = agent_client.responses.create(
        input=query,
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": version,
                "type": "agent_reference"
            }
        }
    )

    return response.output_text

# ==========================
# Router
# ==========================

def route_query(query: str):

    classification = classify_query(query)

    print(f"\nClassification: {classification}\n")

    if classification == "SIMPLE":

        return call_agent(
            agent_name="ltm-rag-agent",
            version="6",      # change if your mini agent version differs
            query=query
        )

    return call_agent(
        agent_name="memory-byters-agent",
        version="3",
        query=query
    )

# ==========================
# Terminal Chat
# ==========================

while True:

    query = input("\nAsk> ")

    if query.lower() in ["exit", "quit"]:
        break

    answer = route_query(query)

    print("\nResponse:")
    print(answer)