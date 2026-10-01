# AI Career Guide and Resume Analyzer

A Flask-based AI career guidance and resume analysis prototype built around the project requirements described in the specification.

## Features

- Career guide with skill-gap analysis and 30-day learning plan
- Resume upload and ATS-style review
- Interview practice generation and answer scoring
- Dashboard and connected workflow across all modules
- Gemini-ready architecture with graceful fallbacks when AI is unavailable

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your Gemini API key in `.env`.
4. Run the app:
   ```bash
   python app.py
   ```
5. Open `http://localhost:5000` in the browser.

## Notes

- The `.env` file is not meant to be committed.
- Resume parsing supports PDF and DOCX files.
- AI responses are structured and handled gracefully when the API key is missing or the service fails.
