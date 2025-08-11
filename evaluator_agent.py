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

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(
                    mime_type="application/pdf",
                    data=base64.b64decode(
                        """Place you file here"""
                    ),
                ),
                types.Part.from_text(text="""Here are the problem description and probing questions in a sentence-based format.

Problem Description: The problem description is \"What is probability?\".

Probing Questions and Answers
Question 1: The paper mentions various CNN architectures (AlexNet, VGG, ResNet, etc.). Can you elaborate on the specific trade-offs considered when choosing a particular architecture for a given application, particularly concerning computational cost, accuracy, and memory footprint?

Answer 1: When choosing a CNN architecture, developers must balance the fundamental trade-off between accuracy, computational cost, and memory footprint, a dilemma illustrated by the evolution from early models like AlexNet, to the deeper but computationally expensive and memory-heavy VGG, and finally to advanced architectures like ResNet, which achieved superior accuracy by using innovative skip connections to train extremely deep networks while simultaneously being far more efficient in both computation and memory than its predecessors.

Question 2: The review discusses several techniques to address the vanishing gradient problem (ReLU, batch normalization). How do these techniques fundamentally differ in their approach, and what are the potential drawbacks of each?

Answer 2: ReLU fundamentally differs from batch normalization in its approach to the vanishing gradient problem; ReLU is a non-linear activation function that prevents gradients from becoming zero for positive inputs, but it can suffer from the 'dying ReLU' problem. In contrast, batch normalization stabilizes learning by normalizing layer inputs, which can be computationally intensive and may behave differently during inference.

Question 3: The document mentions data augmentation as a solution to overfitting. Beyond the techniques listed (flipping, cropping, rotation), what other augmentation strategies are particularly effective for medical image analysis, and why? (Consider domain-specific transformations)

Answer 3: Beyond flipping, cropping, and rotation, other highly effective data augmentation strategies for medical image analysis include elastic deformation, which simulates natural tissue shape variations, and noise injection, which enhances model robustness to imaging artifacts. Additionally, using Generative Adversarial Networks (GANs) to synthesize new, realistic images can significantly expand the training set while preserving crucial domain-specific characteristics.

Question 4: The paper discusses model compression techniques. Considering the computational tools (CPU, GPU, FPGA) also outlined, how does the choice of hardware influence the selection of an appropriate model compression strategy?

Answer 4: The choice of hardware heavily influences model compression strategies: for CPUs, which are less parallel, pruning and quantization are favored to reduce operations and memory; for GPUs, which excel at parallel processing, knowledge distillation is highly effective; and for FPGAs, with their custom hardware, specialized hardware-aware pruning and custom-bitwidth quantization can be used to optimize for specific logic and memory resources.

Question 5: The review touches upon the importance of explainable AI (XAI). How can XAI techniques be integrated into the DL pipeline to enhance trust and transparency in sensitive applications like medical diagnosis, and what specific XAI methods are most suitable for CNNs?

Answer 5: XAI techniques can be integrated into the DL pipeline post-training to provide explanations for a model's predictions, thereby enhancing trust and transparency in sensitive applications like medical diagnosis. Specific XAI methods suitable for CNNs include gradient-based visualization techniques like Grad-CAM and LIME, which highlight influential parts of an image, and attention mechanisms that reveal the regions the model focuses on.

Question 6: The paper mentions several applications in healthcare, including disease diagnosis and image analysis. How can you ensure the security and privacy of patient data when deploying these DL models, especially when training and inference are performed in a cloud environment?

Answer 6: To ensure the security and privacy of patient data when deploying DL models in the cloud, it's essential to apply data anonymization before uploading, use secure communication protocols like SSL/TLS for data transfer, enforce strict access control policies, and consider advanced techniques like homomorphic encryption, which allows computations on encrypted data without decryption.

Question 7: How can the concept of federated learning address challenges related to data privacy and availability in medical image analysis, allowing for collaborative model training across different hospitals or institutions without sharing raw data?

Answer 7: Federated learning addresses data privacy challenges by enabling collaborative model training across different institutions without sharing raw data. Instead of transmitting patient data to a central server, each institution trains a local model, and only the model updates are sent to be aggregated, preserving data privacy while still leveraging a larger, more diverse dataset for robust training.

Question 8: Given the increasing model complexity, what strategies can be employed to optimize memory bandwidth and reduce latency when deploying CNNs on edge devices for real-time applications, such as mobile health monitoring?

Answer 8: To optimize memory bandwidth and reduce latency for real-time CNN applications on edge devices, one can employ strategies such as model quantization, which reduces the precision of weights and activations; pruning, which removes redundant connections; and hardware-aware network architecture search to find efficient model designs. Additionally, using optimized inference frameworks and hardware accelerators can significantly boost performance.

Question 9: The paper explores various CNN architectures and their applications. Can you discuss the ethical considerations surrounding the use of these technologies, especially regarding potential biases in datasets and algorithmic fairness?

Answer 9: The use of CNNs in healthcare raises ethical concerns regarding potential biases in datasets and algorithmic fairness, as unrepresentative data can lead to models that underperform or misdiagnose certain patient demographics. Addressing these issues requires ensuring dataset diversity, implementing fairness metrics to monitor and mitigate bias, and using XAI to maintain transparency and accountability in the model's decision-making process.

 \"problemDescription\": \"What is probability?\",

    \"proposedArchitecture\": \"A new architecture\",

    \"designTradeoffs\": \"No design tradeoff\",

    \"scalibilty\": \"Low\",

    \"securityMeasures\": \"None\",

    \"maintainability\": \"None\",

"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="""{
  \"designReviewScore\": {
    \"detailedFeedbackSummary\": \"The candidate displays a decent understanding of CNN architectures and related concepts but lacks depth in crucial areas. Their grasp of trade-offs is superficial, often glossing over important considerations in applying DL to real-world scenarios. There is a need for a significant improvement in understanding and accounting for the ethical implications, and demonstrating ownership of their proposed design, and seriously consider specific mitigation strategies to improve the trustworthiness of deployed systems. Overall, the candidate provided responses that indicate foundational knowledge of deep learning, however, fell short in demonstrating technical depth, system-level thinking, and practical considerations essential for architect-level contributions.\",
    \"ownership\": 2,
    \"systemDesign\": 2,
    \"technicalDepth\": 3,
    \"tradeoff\": 2
  }
}"""),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["designReviewScore"],
            properties = {
                "designReviewScore": genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    required = ["technicalDepth", "systemDesign", "tradeoff", "ownership", "detailedFeedbackSummary"],
                    properties = {
                        "technicalDepth": genai.types.Schema(
                            type = genai.types.Type.INTEGER,
                        ),
                        "systemDesign": genai.types.Schema(
                            type = genai.types.Type.INTEGER,
                        ),
                        "tradeoff": genai.types.Schema(
                            type = genai.types.Type.INTEGER,
                        ),
                        "ownership": genai.types.Schema(
                            type = genai.types.Type.INTEGER,
                        ),
                        "detailedFeedbackSummary": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                    },
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text(text="""You are a senior software architect performing a rigorous evaluation of a candidate’s architectural design and their ability to reason through system design problems under technical scrutiny. The candidate has submitted a design review document and responded to multiple technical and follow-up questions.

Your task is to:

Critically analyze their design approach

Evaluate the depth and practicality of their responses

Provide clear, unbiased scores

Offer actionable feedback to help the candidate improve

Evaluation Dimensions (with Actions and Expectations)
Evaluate the candidate across the following 4 categories. Assign scores (1–5 scale, integer) and justify each with targeted, candid observations. Then compute an overall score (float out of 5), and provide a comprehensive feedback summary.

1. Technical Depth (technicalDepth)
Objective:
Assess the candidate’s understanding of technical concepts and their ability to apply them to real-world system constraints.

Consider:

Do they demonstrate deep knowledge of technologies, protocols, patterns (e.g., CAP theorem, caching strategies, async comms)?

Do they appropriately handle concerns like data consistency, failure handling, service contracts?

Are they using tools or design primitives in ways that are aligned with scale, security, or throughput goals?

Action-Oriented Scoring Guideline:

5 – Demonstrates architect-level mastery and anticipates edge cases.

3 – Solid grasp but relies on generic knowledge or lacks specificity.

1 – Uses buzzwords without practical application.

2. System Design (systemDesign)
Objective:
Evaluate the structure, modularity, and scalability of the system presented.

Consider:

How are responsibilities split between components?

Is the architecture resilient, scalable, and change-tolerant?

Did the candidate define clear boundaries (e.g., APIs, services, data domains)?

Are deployment and operational considerations included (e.g., containers, CDNs, orchestration)?

Action-Oriented Scoring Guideline:

5 – Clean, extensible, and production-ready system decomposition.

3 – Good structure but missing clarity on interactions or integrations.

1 – Monolithic or naive structure with unclear component logic.

3. Tradeoff Reasoning (tradeoff)
Objective:
Assess the candidate’s ability to identify, evaluate, and communicate architectural trade-offs.

Consider:

Do they present alternatives with clarity and defend their decisions?

Are trade-offs around consistency, latency, cost, or complexity well addressed?

Can they explain why they made each design decision?

Action-Oriented Scoring Guideline:

5 – Consistently balances multiple priorities with solid justifications.

3 – Recognizes trade-offs but decisions are shallow or one-dimensional.

1 – Makes choices without discussing any downside or mitigation.

4. Ownership & Accountability (ownership)
Objective:
Gauge the candidate’s ownership of their design and adaptability to feedback.

Consider:

Did they take full accountability for choices made?

Did they clearly articulate improvement areas or technical risks?

Did they defend decisions without being dismissive, and revise when challenged?

Action-Oriented Scoring Guideline:

5 – Shows maturity, openness to critique, and proactive problem solving.

3 – Accepts some flaws, but lacks initiative or conviction.

1 – Defensive, vague, or unaware of system weaknesses."""),
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
