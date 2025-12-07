from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# Configuration
OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "tinyllama"


def check_spelling_grammar(text, model=MODEL_NAME, ollama_url=OLLAMA_URL):
    """
    Send text to Ollama for spell check and grammar correction.

    Args:
        text (str): The text to check
        model (str): Ollama model to use (default: "tinyllama")
        ollama_url (str): Ollama server URL (default: "http://localhost:11434")

    Returns:
        dict: Dictionary containing corrected text, misspelled words, and suggestions
    """
    if not text or not text.strip():
        return {
            "corrected_text": "",
            "misspelled_words": [],
            "error": "No text provided"
        }

    # Create a simple, direct prompt
    # TinyLlama works better with simple instructions than few-shot examples
    prompt = f"""Correct the spelling in this text: {text}

Only write the corrected version, nothing else:"""

    # Prepare the request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,  
            "top_p": 0.9,
            "top_k": 20,
            "num_predict": 100,  
            "stop": ["\n\n", "Example", "Input:", "Original"] 
        }
    }

    try:
        # Send request to Ollama
        response = requests.post(
            f"{ollama_url}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            corrected_text = result.get("response", "").strip()
            
            # Clean the response aggressively
            # Remove newlines and extra spaces first
            corrected_text = ' '.join(corrected_text.split())
            
            # Strategy 1: Remove common prefixes and labels
            prefixes_to_remove = [
                "Corrected version:", "Corrected text:", "Corrected:", 
                "Corrected spelling:", "Corrected Spelling:",
                "Text:", "Fixed:", "Correction:", "The corrected version is:",
                "Here is the corrected text:", "Here's the correction:",
                "The text should be:", "It should be:", "Answer:",
                "Spelling:", "Fixed spelling:", "Fixed Spelling:"
            ]
            for prefix in prefixes_to_remove:
                # Case-insensitive check
                if corrected_text.lower().startswith(prefix.lower()):
                    corrected_text = corrected_text[len(prefix):].strip()
                    break  # Only remove one prefix
            
            # Strategy 2: Remove quotes
            corrected_text = corrected_text.strip('"').strip("'").strip()
            
            # Strategy 2.5: Fix capitalization if model over-capitalized
            # If original was lowercase/sentence case, but correction is Title Case, fix it
            if corrected_text and len(corrected_text.split()) > 1:
                # Check if it's Title Case (every word capitalized)
                words = corrected_text.split()
                if all(w[0].isupper() for w in words if w):
                    # Check if original was NOT title case
                    orig_words = text.split()
                    if not all(w[0].isupper() for w in orig_words if w):
                        # Convert to sentence case (only first word capitalized)
                        corrected_text = corrected_text[0].upper() + corrected_text[1:].lower()
            
            # Strategy 3: If response contains explanations, extract just the correction
            # Look for sentences that start with explanatory words
            explanation_starters = [
                "I think", "This is", "The error", "Note that", "In this",
                "Here,", "Because", "Since", "As you can see", "The word"
            ]
            for starter in explanation_starters:
                if corrected_text.startswith(starter):
                    # If it starts with explanation, try to find the actual correction
                    # Look for quoted text or text after "is"
                    if '"' in corrected_text:
                        parts = corrected_text.split('"')
                        if len(parts) >= 2:
                            corrected_text = parts[1].strip()
                    break
            
            # Strategy 4: If response is much longer than input, take only first few words
            words_in_input = len(text.split())
            words_in_output = len(corrected_text.split())
            
            if words_in_output > words_in_input * 3:
                # Take only the first N words where N is close to input length
                words = corrected_text.split()
                corrected_text = ' '.join(words[:words_in_input + 2])
            
            # Strategy 5: Check if the output makes sense
            # If it's completely unrelated to input (no common words), use original
            input_words = set(text.lower().split())
            output_words = set(corrected_text.lower().split())
            
            # For single word inputs, be more lenient
            if len(input_words) == 1:
                # For single words, just check if output is also a single word or very short
                if len(output_words) > 3:
                    corrected_text = text
            else:
                # For multi-word inputs, check for some overlap
                common_words = input_words.intersection(output_words)
                if len(common_words) == 0 and len(output_words) > 2:
                    # No common words and output is different - likely hallucination
                    corrected_text = text
            
            # Strategy 6: Final validation
            if len(corrected_text) == 0 or len(corrected_text) > len(text) * 5:
                corrected_text = text
            
            # Find misspelled words by comparing original and corrected text
            misspelled_words = find_misspelled_words(text, corrected_text)
            
            print(f"\n[TERMINAL] Original text: {text}")
            print(f"[TERMINAL] Corrected text: {corrected_text}")
            if misspelled_words:
                print(f"[TERMINAL] Misspelled words found: {misspelled_words}")
            
            return {
                "corrected_text": corrected_text,
                "misspelled_words": misspelled_words,
                "error": None
            }
        else:
            error_msg = f"Error: HTTP {response.status_code} - {response.text}"
            print(f"[TERMINAL] {error_msg}")
            return {
                "corrected_text": "",
                "misspelled_words": [],
                "error": error_msg
            }

    except requests.exceptions.ConnectionError:
        error_msg = "Error: Could not connect to Ollama. Make sure Ollama is running on http://localhost:11434"
        print(f"[TERMINAL] {error_msg}")
        return {
            "corrected_text": "",
            "misspelled_words": [],
            "error": error_msg
        }
    except requests.exceptions.Timeout:
        error_msg = "Error: Request to Ollama timed out. The model may be taking too long to respond."
        print(f"[TERMINAL] {error_msg}")
        return {
            "corrected_text": "",
            "misspelled_words": [],
            "error": error_msg
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"Error: Request failed - {str(e)}"
        print(f"[TERMINAL] {error_msg}")
        return {
            "corrected_text": "",
            "misspelled_words": [],
            "error": error_msg
        }
    except json.JSONDecodeError:
        error_msg = "Error: Invalid JSON response from Ollama"
        print(f"[TERMINAL] {error_msg}")
        return {
            "corrected_text": "",
            "misspelled_words": [],
            "error": error_msg
        }


def find_misspelled_words(original, corrected):
    """
    Compare original and corrected text to find misspelled words.
    Uses fuzzy matching to identify actual spelling corrections.
    """
    import re
    from difflib import SequenceMatcher
    
    # Normalize and split into words
    original_words = re.findall(r'\b\w+\b', original)
    corrected_words = re.findall(r'\b\w+\b', corrected)
    
    misspelled = []
    
    # Use SequenceMatcher to align words
    matcher = SequenceMatcher(None, 
                             [w.lower() for w in original_words], 
                             [w.lower() for w in corrected_words])
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            # Words were changed - these are likely spelling corrections
            for i, j in zip(range(i1, i2), range(j1, j2)):
                orig_word = original_words[i] if i < len(original_words) else None
                corr_word = corrected_words[j] if j < len(corrected_words) else None
                
                if orig_word and corr_word:
                    # Only consider it a spelling error if words are similar but different
                    # (not just capitalization changes)
                    if orig_word.lower() != corr_word.lower():
                        similarity = SequenceMatcher(None, orig_word.lower(), corr_word.lower()).ratio()
                        # If similarity is high (0.5-0.9), it's likely a spelling correction
                        # If too different, might be a word replacement
                        if 0.3 <= similarity < 1.0:
                            misspelled.append({
                                "word": orig_word,
                                "suggestion": corr_word
                            })
    
    return misspelled


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/check', methods=['POST'])
def check_spell():
    """Handle spell checking requests"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({
                "corrected_text": "",
                "misspelled_words": [],
                "error": "No text provided"
            }), 400
        
        result = check_spelling_grammar(text)
        return jsonify(result), 200
        
    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        print(f"[TERMINAL] {error_msg}")
        return jsonify({
            "corrected_text": "",
            "misspelled_words": [],
            "error": error_msg
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Spell Checker Application Starting...")
    print("=" * 60)
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"Model: {MODEL_NAME}")
    print("=" * 60)
    print("Make sure Ollama is running with: ollama serve")
    print("And the model is pulled with: ollama pull tinyllama")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)

