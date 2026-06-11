from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_ENDPOINT=os.getenv("OPENAI_ENDPOINT")
OPENAI_KEY=os.getenv("OPENAI_KEY")
AOAI_API_VERSION=os.getenv("AOAI_API_VERSION")



client = AzureOpenAI(
    api_key=OPENAI_KEY,
    azure_endpoint=OPENAI_ENDPOINT,
    api_version=AOAI_API_VERSION,
)

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

            Return ONLY:
            SIMPLE

            or

            COMPLEX

            Query:
            {query}
            """
    )

    return response.output_text.strip()

print(classify_query("Who is Jacob?"))

print(
    classify_query(
        "Compare onboarding policies with employee information and identify affected employees."
    )
)