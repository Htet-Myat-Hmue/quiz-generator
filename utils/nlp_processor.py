import spacy

def process_text(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    # Extract tokens and sentences
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    sentences = [sent.text for sent in doc.sents]
    
    return {
        'tokens': tokens,
        'sentences': sentences  # Make sure to include this key
    }
