Project Name - QuizGenie

Project Description - The web-based project written in Python using Flask framework allows users to upload Word or pdf files as input and generates quizzes of MCQs and short questions based on the uploaded file.

Project Set Up

1.	mkdir flask_quiz_generator 
2.	cd flask_quiz_generator
3.	python3 -m venv venv
4.	source venv/bin/activate  # On Windows use: venv\Scripts\activate
5.	pip install Flask python-docx PyPDF2 spacy transformers
6.	python -m spacy download en_core_web_sm  # Download spaCy's English model
7.	pip install torch
8.	pip install sentencepiece
9.	mkdir app
10.	cd app
11.	git clone https://github.com/Htet-Myat-Hmue/quiz-generator.git

