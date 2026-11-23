from models import Medikament, Laborwert, ArztbriefErgebnis
from pathlib import Path
from extractor import MedicalExtractor

file_path = Path("arztbriefe/02_dekompensierte_herzinsuffizienz.txt")
text = file_path.read_text(encoding="utf-8")


# Example usage of the MedicalExtractor class

extractor = MedicalExtractor(model_name="llama3.1")

print("Extracting medical information...")

ergebnis = extractor.extract_medical_info(text)
print(ergebnis.model_dump_json(indent=2))

