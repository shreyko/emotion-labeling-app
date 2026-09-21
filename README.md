# Emotion Labeling Task Web Interface

This repository contains the code for an academic data labeling task focused on emotion detection. The interface is built entirely in Python using Streamlit, and it securely records participant annotations to a cloud database.

## Live Demo

If you would like to see the application in action and participate in the labeling task, please head over to the live web interface here: **(https://emotion-labeling-app-j8dlzfebhsgoorvyph2qv2.streamlit.app/)**

## Architecture and Backend

*   **Frontend**: Built using Streamlit, providing a lightweight, interactive web interface generated purely from Python code.
*   **Backend / Database**: The application uses Google Sheets as a serverless database. It communicates with the Google Sheets API via the `gspread` library to read existing users, verify duplicate submissions, and append new annotation data in real time.
*   **State Management**: Streamlit's `st.session_state` is utilized to handle routing between the authentication, labeling, and completion pages without losing the participant's assigned dataset.

## Security Notice

For security purposes, the authentication credentials required to connect to the backend database are deliberately excluded from this repository. Specifically, the `.streamlit/secrets.toml` file and the Google Cloud Service Account JSON keys have been omitted to prevent unauthorized write access to the database. The live deployment holds these keys securely in the Streamlit Cloud environment.

## Project Structure

*   **app.py**: The main application code handling user logic, random tweet assignment, and database transactions.
*   **data/**: Contains the sample dataset of 50 tweets sampled from the Hugging Face Emotion dataset.
*   **scripts/**: Contains helper scripts used during development to fetch and format the raw dataset.
*   **requirements.txt**: The list of Python dependencies required to run the project locally.


