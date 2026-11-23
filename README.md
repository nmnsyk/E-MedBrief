# E-MedBrief

**AI-powered medical information extraction from German discharge letters**

E-MedBrief is a Python-based MVP that uses a local Large Language Model (LLM) to extract important medical information from German discharge letters (*Arztbriefe*).
Medical reports often contain long texts and complex medical terminology, making it difficult to quickly find relevant information.
E-MedBrief addresses this problem by automatically extracting **diagnoses, discharge medications, and laboratory results** and presenting them in a clear, structured format.
The goal is to make medical information easier to find and review, without manually searching through the entire document.

## Features

- **AI-powered extraction** – Automatically extracts relevant medical information from German medical reports.
- **Structured output** – Organizes diagnoses, medications (name, dosage, schedule), and laboratory results (name, value, unit).
- **Local LLM** – Uses Llama 3.1 through Ollama to process text locally.
- **Data validation** – Uses Pydantic to validate the structure of the extracted information.
- **User-friendly interface** – Displays results in a simple Streamlit web application.
- **JSON export** – Allows users to download the extracted information as a JSON file.

## How It Works

E-MedBrief follows a simple extraction pipeline:

```text
German Medical Report (Arztbrief)
               |
               v
       Streamlit Interface
               |
               v
       MedicalExtractor
               |
               v
       Llama 3.1 (Ollama)
               |
               v
       Pydantic Validation
               |
               v
    Structured Medical Data
               |
               v
     Web Interface / JSON
```

The user enters a medical report into the web application. The text is then sent to the locally running Llama 3.1 model.

The LLM extracts the requested information and returns structured JSON data. Pydantic validates the response before the results are displayed in the web interface.

To reduce incorrect extractions, the prompt instructs the model to use only information explicitly mentioned in the report and to exclude suspected or ruled-out diagnoses.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Llama 3.1 | Medical information extraction |
| Ollama | Local LLM execution |
| Pydantic | Structured output and data validation |
| Streamlit | Interactive web interface |
| HTML / CSS | Frontend styling |

## Project Structure

```text
E-MedBrief/
├── app.py
├── extractor.py
├── models.py
├── main.py
├── arztbriefe/
├── gold_standard_v1.json
├── requirements.txt
└── README.md
```

### Main Files

**`app.py` – Web Application**

The Streamlit frontend. Users can enter medical reports, start the analysis, view extracted information, and download JSON results.

**`extractor.py` – LLM Integration**

Contains the `MedicalExtractor` class. It communicates with Llama 3.1 through Ollama, defines the extraction instructions, and validates the model response.

**`models.py` – Data Models**

Defines the Pydantic models used to structure the extracted information:

- `Medikament` – Name, dosage, and administration schedule
- `Laborwert` – Laboratory parameter, value, and unit
- `ArztbriefErgebnis` – Complete extraction result

**`main.py` – Testing**

A simple Python script for testing the extraction process with an example medical report, without starting the web interface.

### Test Data

The `arztbriefe/` directory contains 20 fictional German medical reports used for testing.

The `gold_standard_v1.json` file contains reference data prepared for evaluating extraction quality.

## Getting Started

### Requirements

Before running the application, install:

- Python 3.10 
- Ollama
- Llama 3.1 (via Ollama)

### Run the Application

**1. Clone the repository**

```bash
git clone https://github.com/nmnsyk/E-MedBrief.git
cd E-MedBrief
```

**2. Install Python dependencies**

```bash
python -m pip install -r requirements.txt
```

**3. Download the Llama 3.1 model**

```bash
ollama pull llama3.1
```

**4. Start the application**

Make sure Ollama is running, then execute:

```bash
python -m streamlit run app.py
```

The application is available at `http://localhost:8501`.

## Example Output

For a fictional medical report, E-MedBrief may generate the following structured JSON:

```json
{
  "diagnosen": [
    "Arterielle Hypertonie"
  ],
  "medikamente": [
    {
      "name": "Amlodipin",
      "dosis": "5 mg",
      "schema": "1-0-0"
    }
  ],
  "laborwerte": [
    {
      "name": "CRP",
      "wert": "12,5",
      "einheit": "mg/l"
    }
  ]
}
```

## Future Improvements

The current version focuses on building a working end-to-end medical information extraction system.

Planned improvements include:

- Evaluating extraction quality using the fictional medical reports
- Calculating precision, recall, and F1-score
- Improving extraction accuracy and error handling
- Adding references to the original text for extracted information

## Limitations and Disclaimer

E-MedBrief is an educational prototype developed as a personal portfolio project.

- The application extracts and organizes information but does not explain medical terms or provide medical advice.
- Pydantic validates the JSON structure, not the medical accuracy of the extracted information.
- LLM responses may contain incorrect or missing information.
- The project uses fictional medical reports for development and testing. It has not been validated for processing real patient data.

**E-MedBrief is not intended for clinical decision-making, diagnosis, or treatment.**

---

*Developed as a personal portfolio project to explore Large Language Models, medical NLP, structured information extraction, and local AI applications.*
