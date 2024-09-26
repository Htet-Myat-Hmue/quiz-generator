from transformers import pipeline
from utils.nlp_processor import process_text
import random

def generate_questions(text):
    # Process text using NLP
    processed_data = process_text(text)
    
    # # Debug: Check processed data
    # print("Processed Data:", processed_data)  # Debugging line

    formatted_questions = []

    # Generate multiple-choice questions
    questions_input = "generate questions: " + " ".join(processed_data['tokens'])
    mc_question = pipeline("text2text-generation", model="valhalla/t5-small-qg-hl")(questions_input, max_length=50, num_return_sequences=1)
    
    if mc_question:
        mc_question_text = mc_question[0]['generated_text'].strip()
        print("Generated MC Question:", mc_question_text)  # Debugging line
        if mc_question_text:  # Only add if not empty
            formatted_questions.append(mc_question_text)

    # Generate true/false questions
    for sentence in processed_data['sentences']:
        statement = sentence.strip()
        # Only add meaningful statements
        if statement and len(statement.split()) > 5:  # Simple filter to avoid too short statements
            tf_question = f"{statement} True or False?"
            print("Generated True/False Question:", tf_question)  # Debugging line
            formatted_questions.append(tf_question)

    # Generate fill-in-the-blank questions
    for sentence in processed_data['sentences']:
        words = sentence.split()
        if len(words) > 3:  # Ensure there are enough words to create a blank
            blank_index = random.randint(0, len(words) - 1)
            blank_sentence = ' '.join(words[:blank_index] + ['____'] + words[blank_index + 1:])
            print("Generated Fill-in-the-Blank Question:", blank_sentence)  # Debugging line
            formatted_questions.append(blank_sentence)

    # Return only unique questions
    unique_questions = list(set(formatted_questions))
    # print("Unique Questions:", unique_questions)  # Debugging line

    # Return questions in desired format
    return [{"question": question} for question in unique_questions if question]
