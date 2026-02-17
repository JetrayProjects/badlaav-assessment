# Simple AI Agent

This project implements a Multimodal AI Agent capable of processing text, images, audio, and PDFs. It features a web search tool and a Streamlit-based web interface.

## Features
*   **Multimodal Input:**
    *   **Text:** Chat naturally.
    *   **Images:** Upload PNG/JPG for analysis (e.g., "What's in this image?").
    *   **Audio:** Upload MP3/WAV/M4A. The agent **transcribes** it automatically and responds to the content.
    *   **PDF:** Upload documents for summary or analysis.
*   **Web Search:** The agent can use Google Search to find real-time information.
*   **Conversation Memory:** Maintains context across multiple turns.
*   **Streamlit UI:** A clean, browser-based interface for easy interaction.

## Prerequisites

1.  **OpenAI API Key**
    Create a `.env` file in the project root:
    ```bash
    touch .env
    ```
    Add your key to the file:
    ```
    OPENAI_API_KEY=sk-proj-...
    ```

2.  **Virtual Environment**
    Create a virtual environment to isolate dependencies:
    ```bash
    python3 -m venv venv
    ```

3.  **Activate Environment**
    ```bash
    source venv/bin/activate
    ```

4.  **Install Dependencies**
    Install all required packages from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## Running the App

We have replaced the command-line interface with a **Streamlit Web UI** for a better experience.

Run the following command:
```bash
python -m streamlit run ui.py
```

This will open your browser to `http://localhost:8501` (or similar).

## How to Use
1.  **Chat:** Type your message in the input box at the bottom.
2.  **Attach Files:** Click the **"➕ Attach files"** button above the chat input to upload:
    *   **Images** (`.png`, `.jpg`)
    *   **Audio** (`.mp3`, `.wav`, `.m4a`)
    *   **PDFs** (`.pdf`)
3.  **Send:** Click the "Send" button (or press Enter in the chat box).

(Note: Sample files are given in the folder 'sample_files')

## Project Structure
*   `ui.py`: The main Streamlit application.
*   `api/agent.py`: Defines the Agent, Model (`gpt-4o`), and Tools (`search_web`).
*   `cli.py`: (Legacy) Command-line interface.
