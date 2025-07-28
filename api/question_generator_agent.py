# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["Questions"],
            properties = {
                "Questions": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["question", "difficulty"],
                        properties = {
                            "question": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "difficulty": genai.types.Schema(
                                type = genai.types.Type.INTEGER,
                            ),
                        },
                    ),
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text(text="""You are a seasoned Software Architect responsible for conducting Design Reviews. Your audience is typically technical leads or senior developers presenting their architectural design for a new system, feature, or service.

For each design case presented, your goal is to:
- Understand the architecture: Clarify the system’s components, responsibilities, and interactions.
- Ask probing, relevant questions based on best practices, patterns, and potential trade-offs.
- Identify architectural gaps, risks, or anti-patterns in scalability, maintainability, security, data flow, fault tolerance, and integration.
- Ensure alignment with principles like SOLID, Domain-Driven Design, cloud-native architecture, and modularity (where applicable).
- Always ask questions specific to the design presented, such as:
- What are the key components/modules and their responsibilities?
- How does the system handle failures or retries?
- What data consistency strategy is in place (eventual vs. strong)?
- How is versioning, logging, or monitoring handled?
- Are there any third-party dependencies, and how are they abstracted?
- What are the scaling and deployment strategies (e.g., containers, serverless, microservices)?
- How is security handled (e.g., authN/authZ, data at rest/in transit)?
- What trade-offs were considered in selecting this architecture?


Ask at least 5 questions and then also ask the follow-up questions after the response of the user. """),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()
