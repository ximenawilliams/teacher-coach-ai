Agrega esta sección en tu `README.md` debajo de **Technology Stack** o **How It Works**:

````markdown
## Local Gemma Integration with Ollama

Teacher Coach AI supports local AI inference using Ollama and Gemma models.

The application can run educational recommendations locally without depending entirely on cloud infrastructure, making it suitable for low-resource schools and environments with limited connectivity.

### Ollama Integration

The Streamlit application connects to Gemma through Ollama using Python.

Example integration:

```python
import ollama

response = ollama.chat(
    model="gemma3:1b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

recommendation = response["message"]["content"]
```

### Workflow

1. Teacher uploads student performance data
2. The system detects learning gaps
3. Teacher Coach AI builds an educational prompt
4. Ollama sends the prompt to Gemma
5. Gemma generates reinforcement recommendations for the teacher

### Benefits

- Local AI execution
- Offline-first approach
- Low infrastructure requirements
- Privacy-friendly educational analysis
- Designed for affordable computers and tablets

### Requirements

- Ollama
- Gemma model installed locally
- Python
- Streamlit

Example:

```bash
ollama pull gemma3:1b
streamlit run app.py
```
````
