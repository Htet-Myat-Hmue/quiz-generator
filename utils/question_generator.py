import re
import random
import asyncio
import spacy
from transformers import pipeline, T5Tokenizer, T5ForConditionalGeneration
from utils.nlp_processor import process_text

# Initialize summarization and question-generation models
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
tokenizer = T5Tokenizer.from_pretrained("t5-base")
model = T5ForConditionalGeneration.from_pretrained("t5-base")

# Load the spaCy model once globally
nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    """Preprocess text to normalize titles and flatten bullet points."""
    text = re.sub(r'(\b[A-Za-z0-9 ]+):\s*\n', r'\1: ', text)
    text = re.sub(r'[\n\r]\s*[-•]\s+', ' ', text) 
    return text

def is_valid_answer(word):
    """Check if the word is not a stop word and is not numeric."""
    return not nlp.vocab[word.lower()].is_stop and not word.isdigit()

async def generate_mcqs(question_answering_pipeline, processed_data, text, num_questions):
    """Generate multiple-choice questions asynchronously using BERT with dynamic templates."""
    formatted_questions_with_answers = []
    unique_mc_questions = set()

    while len(unique_mc_questions) < num_questions:  
        if processed_data['tokens']:
            token = random.choice(processed_data['tokens'])
            # Use more dynamic and relevant question prompts
            question_variants = [
                f"What is the significance of '{token}' in the context of the provided text?",
                f"Which statement best describes '{token}'?",
                f"How does '{token}' relate to the main topic discussed?",
                f"Why is '{token}' important in this context?"
            ]

            question = random.choice(question_variants)  # Choose a random question variant
            if question not in unique_mc_questions:  # Ensure unique questions
                unique_mc_questions.add(question)

                # Get the correct answer based on the context
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
    formatted_questions_with_answers = []
    sentences = processed_data['sentences']

    while len(formatted_questions_with_answers) < num_questions:
        for sentence in sentences:
            if len(formatted_questions_with_answers) >= num_questions:
                break

            statement = sentence.strip()
            if statement and len(statement.split()) > 5:
                tf_question = f"{statement}"
                answer = "True" if random.choice([True, False]) else "False"
                
                formatted_questions_with_answers.append({
                    "question": tf_question,
                    "answer": answer
                })

    return formatted_questions_with_answers[:num_questions]

async def generate_fill_in_blank(processed_data, num_questions):
    formatted_questions_with_answers = []
    sentences = processed_data['sentences']

    while len(formatted_questions_with_answers) < num_questions:
        for sentence in sentences:
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

    return formatted_questions_with_answers[:num_questions]

async def generate_questions_with_answers(text, quiz_type="mixed", num_questions=3):
    text = preprocess_text(text)
    processed_data = process_text(text)

    # Initialize the question answering pipeline here
    question_answering_pipeline = pipeline("question-answering")

    formatted_questions_with_answers = []

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
        mcq_limit = num_questions // 3
        tf_limit = num_questions // 3
        fill_blank_limit = num_questions - mcq_limit - tf_limit

        mcq_questions = await generate_mcqs(question_answering_pipeline, processed_data, text, mcq_limit)  # Ensure num_questions is passed
        tf_questions = await generate_true_false(processed_data, tf_limit)
        fill_blank_questions = await generate_fill_in_blank(processed_data, fill_blank_limit)

        formatted_questions_with_answers.extend(mcq_questions)
        formatted_questions_with_answers.extend(tf_questions)
        formatted_questions_with_answers.extend(fill_blank_questions)

    unique_questions_with_answers = {qa['question']: qa for qa in formatted_questions_with_answers}
    limited_questions = [{"question": q, "choices": a.get('choices', None), "answer": a['answer']} 
                         for q, a in unique_questions_with_answers.items()][:num_questions]
    
    return limited_questions

