import time
import requests

def call_llm(prompt):
    """
    Call the Ollama LLM model with a prompt.

    Retries up to 3 times if the API request fails.

    Args:
        model (str): The name of the Ollama model to query.
        prompt (str): The prompt to send to the model.

    Returns:
        tuple:
            text_output (str): The raw response from the model.
            attempts (int): Number of attempts made (max 3).
            errors (list[str]): List of error messages encountered.
            time_ns (int): Time taken in total in nanoseconds.
    """
    start = time.perf_counter_ns()
    attempts = 0
    errors = []
    for attempt in range(3):
        attempts = attempt + 1
        try:
            r = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gpt-oss:20b",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=(5, 1800)
            )

            r.raise_for_status() 
            data = r.json()
            break

        except requests.RequestException as e:
            print(f"API error on attempt {attempt+1}/3: {e}")
            errors.append(str(e))

            if attempt < 2:
                print("Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print("API failed after 3 attempts.")
                raise RuntimeError("API failed after retries")

    end = time.perf_counter_ns()
    time_ns = end - start
    text_output = data.get("response", "")
    
    return (text_output, attempts, errors, time_ns)