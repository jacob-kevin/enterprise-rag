from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

endpoint = "https://memory-byters-openai.services.ai.azure.com/api/projects/memory-byters-openai-project"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()

response = openai_client.responses.create(
    input="Who is Jacob?",
    extra_body={
        "agent_reference": {
            "name": "memory-byters-agent",
            "version": "3",
            "type": "agent_reference"
        }
    }
)

print("\n=== RESPONSE ===\n")
print(response.output_text)