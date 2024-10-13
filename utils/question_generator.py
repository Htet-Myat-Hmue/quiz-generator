from transformers import pipeline
from utils.nlp_processor import process_text
import random
import spacy
import asyncio

# Load the spaCy model once globally
nlp = spacy.load("en_core_web_sm")

def is_valid_answer(word):
    """Check if the word is not a stop word."""
    return not nlp.vocab[word.lower()].is_stop

async def generate_mcqs(question_answering_pipeline, processed_data, text, num_questions):
    """Generate multiple-choice questions asynchronously using BERT."""
    formatted_questions_with_answers = []
    unique_mc_questions = set()

    while len(unique_mc_questions) < num_questions:  
        if processed_data['tokens']:
            token = random.choice(processed_data['tokens'])
            question = f"What is {token}?"  # Simple question logic
            if question not in unique_mc_questions:  # Ensure unique questions
                unique_mc_questions.add(question)

                answer = await asyncio.to_thread(question_answering_pipeline, question=question, context=text)
                correct_answer = answer.get('answer', None)

                if correct_answer and is_valid_answer(correct_answer):
                    false_answers = [word for word in processed_data['tokens'] if is_valid_answer(word) and word != correct_answer]
                    random.shuffle(false_answers)
                    
                    false_answers = [word for word in false_answers if word]  # Remove any blanks
                    false_answers = false_answers[:3]  # Get up to 3 false answers

                    choices = false_answers + [correct_answer]
                    random.shuffle(choices)  # Shuffle choices

                    formatted_questions_with_answers.append({
                        "question": question,
                        "choices": [choice for choice in choices if choice],  # Ensure no blanks in choices
                        "answer": correct_answer
                    })

    return formatted_questions_with_answers
async def generate_true_false(processed_data, num_questions):
    """Generate true/false questions based on sentences."""
    formatted_questions_with_answers = []
    
    for sentence in processed_data['sentences']:
        if len(formatted_questions_with_answers) >= num_questions:
            break
            
        statement = sentence.strip()
        if statement and len(statement.split()) > 5:
            tf_question = f"{statement} True or False?"
            formatted_questions_with_answers.append({
                "question": tf_question,
                "answer": "True" if random.choice([True, False]) else "False"
            })

    return formatted_questions_with_answers

async def generate_fill_in_blank(processed_data, num_questions):
    """Generate fill-in-the-blank questions based on sentences."""
    formatted_questions_with_answers = []
    
    for sentence in processed_data['sentences']:
        if len(formatted_questions_with_answers) >= num_questions:
            break
            
        words = sentence.split()
        if len(words) > 3:
            blank_index = random.randint(0, len(words) - 1)
            blank_word = words[blank_index]
            if is_valid_answer(blank_word):
                blank_sentence = ' '.join(words[:blank_index] + ['____'] + words[blank_index + 1:])
                formatted_questions_with_answers.append({
                    "question": blank_sentence,
                    "answer": blank_word
                })

    return formatted_questions_with_answers

async def generate_questions_with_answers(text, quiz_type="mixed", num_questions=3):
    """Generate various types of questions based on the input text."""
    # Process text using NLP
    processed_data = process_text(text)

    # Create the question answering pipeline using DistilBERT
    question_answering_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

    formatted_questions_with_answers = []

    # Determine question limits based on the selected quiz type
    if quiz_type == "mcq":
        mcq_questions = await generate_mcqs(question_answering_pipeline, processed_data, text, num_questions)
        formatted_questions_with_answers.extend(mcq_questions)

    elif quiz_type == "true_false":
        tf_questions = await generate_true_false(processed_data, num_questions)
        formatted_questions_with_answers.extend(tf_questions)

    elif quiz_type == "fill_blank":
        fill_blank_questions = await generate_fill_in_blank(processed_data, num_questions)
        formatted_questions_with_answers.extend(fill_blank_questions)

    elif quiz_type == "mixed":
        mcq_limit = num_questions // 3  # Aim for 1/3 of the total questions to be MCQs
        tf_limit = num_questions // 3     # Aim for 1/3 of the total questions to be True/False
        fill_blank_limit = num_questions - mcq_limit - tf_limit  # Fill in the rest

        # Ensure no negative limits
        mcq_limit = max(1, mcq_limit)  # Ensure at least 1 question if possible
        tf_limit = max(1, tf_limit)     # Ensure at least 1 question if possible
        fill_blank_limit = max(1, fill_blank_limit)  # Ensure at least 1 question if possible

        mcq_questions = await generate_mcqs(question_answering_pipeline, processed_data, text, mcq_limit)
        formatted_questions_with_answers.extend(mcq_questions)

        tf_questions = await generate_true_false(processed_data, tf_limit)
        formatted_questions_with_answers.extend(tf_questions)

        fill_blank_questions = await generate_fill_in_blank(processed_data, fill_blank_limit)
        formatted_questions_with_answers.extend(fill_blank_questions)

    # Remove duplicate questions and limit to the number of requested questions
    unique_questions_with_answers = {qa['question']: qa for qa in formatted_questions_with_answers}
    
    limited_questions = [{"question": q, "choices": a.get('choices', None), "answer": a['answer']} 
                         for q, a in unique_questions_with_answers.items()][:num_questions]
    
    return limited_questions