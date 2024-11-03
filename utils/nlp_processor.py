import spacy

# Load the spaCy model once globally
nlp = spacy.load("en_core_web_sm")

def process_text(text):
    # Process the text with spaCy
    doc = nlp(text)
    
    # Extract relevant information
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]  # Using lemmas
    sentences = [sent.text.strip() for sent in doc.sents]
    entities = [(ent.text, ent.label_) for ent in doc.ents]  # Extract named entities

    return {
        'tokens': tokens,
        'sentences': sentences,
        'entities': entities  # Add named entities to the output
    }
