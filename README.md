# 🔤 AI-Powered Spell Checker

A web-based spell checker application that uses **TinyLlama** (via Ollama) to detect and correct spelling errors in real-time. This project demonstrates the integration of a local LLM with a Flask web application to provide intelligent spell-checking capabilities.

## ✨ Features

- **Real-time Spell Checking**: Instantly checks and corrects spelling errors as you type
- **AI-Powered Corrections**: Uses TinyLlama LLM for intelligent spell correction
- **Misspelled Word Detection**: Highlights misspelled words with suggested corrections
- **Clean Web Interface**: Simple and intuitive user interface
- **Local Processing**: All processing happens locally using Ollama - no data sent to external servers
- **Terminal Logging**: Displays original text, corrected text, and misspelled words in the terminal

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML, CSS, JavaScript
- **AI Model**: TinyLlama (via Ollama)
- **HTTP Client**: Requests library

## 📋 Prerequisites

Before running this application, ensure you have the following installed:

1. **Python 3.7+**
2. **Ollama** - [Download and install Ollama](https://ollama.ai/)
3. **TinyLlama model** - Pull the model using Ollama

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Spell-Checker
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install and Setup Ollama

#### Install Ollama
- Visit [ollama.ai](https://ollama.ai/) and download the installer for your OS
- Follow the installation instructions

#### Start Ollama Server
```bash
ollama serve
```

#### Pull TinyLlama Model
```bash
ollama pull tinyllama
```

## 🎯 Usage

### 1. Start the Flask Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 2. Access the Web Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

### 3. Check Spelling

1. Enter or paste text into the input field
2. Click the "Check Spelling" button
3. View the corrected text and any misspelled words with suggestions

### 4. Monitor Terminal Output

The terminal will display:
- Original text
- Corrected text
- List of misspelled words with suggestions

Example terminal output:
```
[TERMINAL] Original text: Ths is a tst sentance
[TERMINAL] Corrected text: This is a test sentence
[TERMINAL] Misspelled words found: [{'word': 'Ths', 'suggestion': 'This'}, {'word': 'tst', 'suggestion': 'test'}, {'word': 'sentance', 'suggestion': 'sentence'}]
```

## 📁 Project Structure

```
Spell-Checker/
├── app.py                 # Flask application and spell-checking logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── static/               # Static files (CSS, JS, images)
└── README.md            # This file
```

## 🔧 Configuration

The application can be configured by modifying the following variables in `app.py`:

```python
OLLAMA_URL = "http://localhost:11434"  # Ollama server URL
MODEL_NAME = "tinyllama"                # LLM model to use
```

### Model Options

You can experiment with different Ollama models by changing `MODEL_NAME`:
- `tinyllama` (default) - Fast and lightweight
- `llama2` - More accurate but slower
- `mistral` - Good balance of speed and accuracy

To use a different model, first pull it:
```bash
ollama pull <model-name>
```

## 🧪 How It Works

1. **User Input**: User enters text in the web interface
2. **API Request**: Frontend sends text to Flask backend via POST request
3. **LLM Processing**: Backend sends text to Ollama with a spell-checking prompt
4. **Response Cleaning**: Multiple strategies clean and validate the LLM response
5. **Word Comparison**: Algorithm compares original and corrected text to identify misspelled words
6. **Result Display**: Corrected text and suggestions are displayed to the user

### Spell Checking Algorithm

The application uses a sophisticated multi-strategy approach:

1. **Prompt Engineering**: Simple, direct prompts for better LLM performance
2. **Response Cleaning**: Removes prefixes, quotes, and explanatory text
3. **Validation**: Ensures output is reasonable and related to input
4. **Fuzzy Matching**: Uses `SequenceMatcher` to identify spelling corrections
5. **Similarity Scoring**: Filters corrections based on word similarity (0.3-1.0 ratio)

## 🐛 Troubleshooting

### Ollama Connection Error
**Error**: `Could not connect to Ollama`

**Solution**: 
- Ensure Ollama is running: `ollama serve`
- Check if Ollama is accessible at `http://localhost:11434`

### Model Not Found
**Error**: `Model not found`

**Solution**:
- Pull the model: `ollama pull tinyllama`
- Verify model is available: `ollama list`

### Slow Response Times
**Solution**:
- Use a smaller model like `tinyllama`
- Reduce `num_predict` in the model options (in `app.py`)
- Ensure your system has adequate resources

### Port Already in Use
**Error**: `Address already in use`

**Solution**:
- Change the port in `app.py`: `app.run(port=5001)`
- Or kill the process using port 5000

## 🤝 Contributing

Contributions are welcome! Here are some ways you can contribute:

- Report bugs and issues
- Suggest new features
- Improve documentation
- Submit pull requests

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Ollama** - For providing an easy way to run LLMs locally
- **TinyLlama** - For the lightweight and efficient language model
- **Flask** - For the simple and powerful web framework

## 📧 Contact

For questions or feedback, please open an issue on the repository.

---

**Note**: This application processes all data locally using Ollama. No text is sent to external servers, ensuring privacy and data security.
