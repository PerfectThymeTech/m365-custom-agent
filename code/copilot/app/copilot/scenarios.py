from enum import Enum


class DocumentScenarios(str, Enum):
    LEGAL_DESCRIPTIONS_AND_DISCREPANCIES = (
        "Extract the legal descriptions and list the identified discrepancies!"
    )
    SUMMARIZE_DOCUMENT = "Summarize the document!"


class DocumentScenarioInstructions:
    INSTRUCTIONS = {
        DocumentScenarios.LEGAL_DESCRIPTIONS_AND_DISCREPANCIES: (
            """
            # Objective
            Extract legal descriptions from the provided document and identify any discrepancies present.

            # Instructions
            - You must extract all legal descriptions found within the document.
            - Identify and list any discrepancies related to the legal descriptions.
            - Only list on the discrepancies that pertain to legal descriptions and similarities.
            - Solve this step by step to ensure accuracy.

            # Steps to Follow

            1. Locate legal descriptions
            - Carefully read through the entire document to locate legal descriptions.

            2. Extract legal descriptions
            - For each legal description found, extract the complete text and note its location within the document

            3. Identify discrepancies
            - Analyze the extracted legal descriptions to identify any discrepancies or inconsistencies.
            - Discrepancies could include conflicting information, missing details, or any other irregularities.

            4. Create response
            - Create a response according to the response format below.

            # Response Format
            - Provide the results in markdown format.
            - First list all extracted legal descriptions under a section titled "Extracted Legal Descriptions".
              - Each legal description must be presented as a bullet point.
              - Only include the key points of each legal description and avoid unnecessary details.
            - Then, list all identified discrepancies under a section titled "Identified Discrepancies".
              - Present each discrepancy as a numbered list item.
              - Provide a brief explanation for each discrepancy identified.
              - Paraphrase the discrepancies to ensure clarity and avoid direct copying from the document.
            """
        ),
        DocumentScenarios.SUMMARIZE_DOCUMENT: (
            """
            # Objective
            Provide a concise summary of the provided document.

            # Instructions
            - Read through the entire document carefully.
            - Identify the main points and key information presented in the document.
            - Create a summary that captures the essence of the document in a clear and concise manner.
            - Ensure the summary is easy to understand and free of jargon.

            # Response Format
            - Provide the summary in markdown format.
            - The summary must be presented as a series of bullet points.
            - Each bullet point should highlight a key aspect or main point from the document.
            - Avoid including unnecessary details or lengthy explanations.
            - Ensure the summary is well-organized and logically structured.
            """
        ),
    }
