import azure.functions as func
import json
import os

from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

app = func.FunctionApp()

# =====================================================
# Azure OpenAI Client (Classifier)
# =====================================================

classifier_client = AzureOpenAI(
    api_key=os.getenv("OPENAI_KEY"),
    azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
    api_version=os.getenv("AOAI_API_VERSION")
)

# =====================================================
# Foundry Project Client
# =====================================================

project_client = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
)

agent_client = project_client.get_openai_client()

# =====================================================
# Query Classifier
# =====================================================

def classify_query(query: str) -> str:

    response = classifier_client.responses.create(
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

# =====================================================
# Agent Caller
# =====================================================

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

# =====================================================
# Router
# =====================================================

def route_query(query: str):

    classification = classify_query(query)

    if classification == "SIMPLE":

        answer = call_agent(
            agent_name="ltm-rag-agent",
            version="7",
            query=query
        )

        return {
            "classification": "SIMPLE",
            "agent": "ltm-rag-agent",
            "answer": answer
        }

    answer = call_agent(
        agent_name="memory-byters-agent",
        version="4",
        query=query
    )

    return {
        "classification": "COMPLEX",
        "agent": "memory-byters-agent",
        "answer": answer
    }

# =====================================================
# HTTP Endpoint
# =====================================================

@app.route(route="ask", auth_level=func.AuthLevel.ANONYMOUS)
def ask(req: func.HttpRequest) -> func.HttpResponse:

    try:

        body = req.get_json()

        query = body.get("query")

        if not query:
            return func.HttpResponse(
                json.dumps({"error": "query field missing"}),
                status_code=400,
                mimetype="application/json"
            )

        result = route_query(query)

        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:

        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )