from enum import Enum

class DocumentScenarios(str, Enum):
    LEGAL_DESCRIPTIONS_AND_DISCREPANCIES = "Extract the legal descriptions and list the identified discrepancies!"
    SUMMARIZE_DOCUMENT = "Summarize the document!"

class DocumentScenarioInstructions:
    INSTRUCTIONS = {
        DocumentScenarios.LEGAL_DESCRIPTIONS_AND_DISCREPANCIES: (
            "Extract the legal descriptions from the document and list any identified discrepancies."
        ),
        DocumentScenarios.SUMMARIZE_DOCUMENT: (
            "Provide a concise summary of the document's content."
        ),
    }
