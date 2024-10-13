from flask import Flask, request, render_template, send_file
from transformers import pipeline
from utils.file_extractor import extract_text_from_file
from utils.nlp_processor import process_text
from utils.question_generator import generate_questions_with_answers
import asyncio
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document
import random

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        quiz_type = request.form.get('quiz_type')
        num_questions = int(request.form.get('num_questions'))  # Get the number of questions
        
        if file and (file.filename.endswith(('.docx', '.pdf', '.txt'))):
            content = extract_text_from_file(file)
            questions = asyncio.run(generate_questions_with_answers(content, quiz_type, num_questions))  # Pass num_questions
            return render_template('quiz_preview.html', questions=questions)

    return render_template('index.html')

@app.route('/download_quiz', methods=['POST'])
def download_quiz():
    questions = request.json.get('quiz_data', [])
    file_format = request.json.get('file_format', 'pdf')
    include_answers = request.json.get('include_answers', True)

    if file_format == 'pdf':
        return generate_pdf(questions, include_answers)
    elif file_format == 'docx':
        return generate_docx(questions, include_answers)

    return "Invalid format", 400

def generate_pdf(questions, include_answers):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setFont("Helvetica", 12)
    
    for index, question_data in enumerate(questions, start=1):
        question = question_data['question']
        choices = question_data.get('choices', [])
        answer = question_data['answer']

        pdf.drawString(50, y, f"Q{index}: {question}")
        y -= 20
        
        for i, choice in enumerate(choices, start=1):
            pdf.drawString(70, y, f"{i}. {choice}")
            y -= 20

        if include_answers:
            pdf.drawString(50, y, f"Answer: {answer}")
            y -= 20

        y -= 20  # Add some space before the next question

        if y <= 50:  # Create a new page if the content reaches the bottom
            pdf.showPage()
            y = height - 50

    pdf.save()
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name="quiz.pdf", mimetype='application/pdf')

def generate_docx(questions, include_answers):
    doc = Document()

    for index, question_data in enumerate(questions, start=1):
        question = question_data['question']
        choices = question_data.get('choices', [])
        answer = question_data['answer']

        doc.add_paragraph(f"Q{index}: {question}")

        for i, choice in enumerate(choices, start=1):
            doc.add_paragraph(f"{i}. {choice}", style='ListNumber')

        if include_answers:
            doc.add_paragraph(f"Answer: {answer}")
        doc.add_paragraph("")  # Add some space

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="quiz.docx", mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

if __name__ == '__main__':
    app.run(debug=True)
