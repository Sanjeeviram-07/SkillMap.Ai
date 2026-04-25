import requests
from typing import Optional

def call_ollama(prompt: str, model: str = "llama3", base_url: str = "http://localhost:11434") -> str:
    """
    Calls the Ollama API to generate a response for a given prompt.
    
    Args:
        prompt (str): The input prompt for the model.
        model (str): The model name to use (default: llama3).
        base_url (str): The base URL of the Ollama API (default: http://localhost:11434).
        
    Returns:
        str: The generated text response from the model.
        
    Raises:
        requests.exceptions.RequestException: If the API call fails.
        KeyError: If the response format is unexpected.
    """
    url = f"{base_url}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False  # Disable streaming for a simple return
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        return data.get("response", "")
        
    except requests.exceptions.RequestException as e:
        # Re-raise with a descriptive message or handle as needed
        raise requests.exceptions.RequestException(f"Ollama API request failed: {e}")

if __name__ == "__main__":
    # Test the function
    try:
        print("Testing Ollama API call...")
        output = call_ollama("Briefly explain what an LLM is.")
        print("\nResponse:")
        print(output)
    except Exception as e:
        print(f"\nError: {e}")
