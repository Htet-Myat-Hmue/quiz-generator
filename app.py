from flask import Flask, request, render_template
from utils.file_extractor import extract_text_from_file
from utils.question_generator import generate_questions

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and (file.filename.endswith('.docx') or file.filename.endswith('.pdf')):
            content = extract_text_from_file(file)
            questions = generate_questions(content)
            return render_template('quiz_preview.html', questions=questions)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
