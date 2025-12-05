# financial_news_intel/core/ner_model.py

import spacy
from spacy.language import Language
from typing import List, Dict, Any, Optional

# --- IMPORTANT CHANGE ---
# Import the model name from the central configuration file
from .config import SPACY_MODEL_NAME
# --- END CHANGE ---


class NERModel:
    """
    A singleton class to manage the spaCy language model instance.
    This ensures the large model is loaded only once at startup.
    """
    def __init__(self, model_name: str = SPACY_MODEL_NAME):
        self.model_name = model_name
        self._nlp: Optional[Language] = None

    def get_nlp(self) -> Language:
        """Loads and returns the spaCy NLP pipeline."""
        if self._nlp is None:
            try:
                print(f"Loading spaCy NER model: {self.model_name}...")
                # Disable unnecessary pipeline components for faster loading/processing
                self._nlp = spacy.load(
                    self.model_name, 
                    disable=["parser", "tagger", "attribute_ruler", "lemmatizer"]
                )
                print("spaCy NER model loaded.")
            except OSError:
                # Reminder for the user if they forgot the download step
                print(f"Error: spaCy model '{self.model_name}' not found. Did you run:")
                print("    python -m spacy download en_core_web_md")
                raise
        return self._nlp

# Global instance for easy import across agents
ner_model = NERModel()

def extract_entities(text: str) -> List[Dict[str, str]]:
    """
    Extracts relevant Named Entities from a given text.
    """
    nlp = ner_model.get_nlp()
    doc = nlp(text)
    
    # Entity types most relevant to financial news
    FINANCIAL_ENTITY_LABELS = {"ORG", "GPE", "PERSON", "NORP", "LOC", "PRODUCT", "MONEY"}
    
    entities = []
    for ent in doc.ents:
        if ent.label_ in FINANCIAL_ENTITY_LABELS:
             entities.append({
                "entity": ent.text.strip(),
                "label": ent.label_
            })
            
    return entities