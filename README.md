# TalentScout AI Assistant

An intelligent chatbot designed to assist in the initial screening of candidates for TalentScout, a fictional recruitment agency specializing in technology placements. The chatbot uses Google's Gemma 2B model primarily through Ollama with GPU acceleration support, and falls back to Hugging Face for robustness.

## Features

- Interactive chat interface for candidate screening
- Enhanced UI with intuitive manual input form and resume upload options
- Automated collection of candidate information
- Robust PDF parsing using PyMuPDF and pdfplumber
- Dynamic technical question generation based on candidate tech stack
- Intelligent fallback mechanism between Ollama (primary) and Hugging Face (secondary) for model inference
- Context-aware conversation handling
- Secure handling of candidate data
- GPU acceleration support for faster inference

## Prerequisites

- Python 3.8 or higher
- Ollama installed locally
- NVIDIA GPU with CUDA support (optional, for GPU acceleration)

## Setup

1.  Create a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Set up environment variables:
    *   Create a `.env` file in the root directory of the project.
    *   Add your Hugging Face API token to this file:
        ```
        HUGGINGFACEHUB_API_TOKEN=hf_YOUR_ACTUAL_TOKEN_HERE
        ```
        (Replace `hf_YOUR_ACTUAL_TOKEN_HERE` with your actual token from Hugging Face.)
    *   (Optional) To specify a custom cache directory for Hugging Face models, add this to your `.env` file:
        ```
        HUGGINGFACE_HUB_CACHE=/path/to/your/desired/cache/directory
        ```
        (Replace `/path/to/your/desired/cache/directory` with your preferred path.)

4.  Set up Ollama:
    *   Install Ollama from [ollama.ai](https://ollama.ai)
    *   Pull the Gemma model (if not already pulled):
        ```bash
        ollama pull gemma:2b
        ```

5.  (Optional) GPU Setup:
    *   Ensure you have NVIDIA drivers installed
    *   Install CUDA toolkit if not already installed
    *   The application will automatically detect and use GPU if available for both Ollama and Hugging Face.

6.  Run the application:
    ```bash
    streamlit run app.py
    ```

## Usage

1.  Open your web browser and navigate to the URL shown in the terminal (typically `http://localhost:8501`)
2.  On the welcome screen, choose your preferred method to start the screening process:
    *   **Manual Input**: Fill in your candidate details using a dedicated form.
    *   **Upload Resume**: Upload your resume (PDF or DOCX) for automatic information extraction.
3.  Review and confirm extracted/entered information. If any details are missing after resume upload, you will be prompted to fill them in manually.
4.  The chatbot will then initiate the conversation and ask technical questions based on the provided tech stack.
5.  Interact with the chatbot as needed.

## Performance Optimization

The application automatically optimizes for your hardware:
- Uses GPU acceleration when available for both Ollama and Hugging Face models.
- Falls back to CPU if GPU is not available or encounters issues.
- Configurable batch size and context window (managed internally by Ollama/Hugging Face pipelines).
- Adjustable number of threads for CPU processing (managed by Ollama/Hugging Face pipelines).

## Data Privacy

This application handles candidate data with privacy in mind:
- All data is processed locally
- Candidate information and conversation analysis are saved to a `candidates/` directory for review.
- No permanent storage of sensitive information on external servers (unless Hugging Face API is used, in which case data is processed temporarily).
- Compliance with data privacy standards (local processing).

## Note

This is a demonstration project. In a production environment, additional security measures, robust error logging, and more comprehensive data management would be implemented. 