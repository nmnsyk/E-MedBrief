from ollama import chat
from models import ArztbriefErgebnis


class MedicalExtractor:
    def __init__(self, model_name: str = "llama3.1"):
        self.model_name = model_name


    def extract_medical_info(self, text: str) -> ArztbriefErgebnis:
        user_prompt = f"""You are a medical information extraction assistant.

    Extract the following information from the German medical report:
    - Confirmed diagnoses
    - Discharge medications (name, dosage, schema)
    - Laboratory values (name, value, unit)

    Rules:
    - Extract only information explicitly mentioned in the text.
    - Do not include suspected or ruled-out diagnoses.
    - Do not invent missing information.
    - Use empty lists if a category contains no information.
    - For laboratory values, separate the numeric value
    from its unit.
    - The "wert" field must contain only the measured value.
    - The "einheit" field must contain only the unit.
    - Example: "CRP: 86 mg/l" ->
        wert: "86", einheit: "mg/l".
    
    Medical report:
    {text}
     """
        response = chat(
            model=self.model_name,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            format=ArztbriefErgebnis.model_json_schema(),
              options={"temperature": 0}
        )

        arztbrief_ergebnis = ArztbriefErgebnis.model_validate_json(
            response.message.content
        )
        return arztbrief_ergebnis


    
        