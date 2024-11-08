import os
from flask import Flask # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def home():
    return 'Welcome to Page Analyzer!'

if __name__ == '__main__':
    app.run(debug=True)
