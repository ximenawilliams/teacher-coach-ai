import ollama

def test_gemma():
    response = ollama.chat(
        model="gemma4",
        messages=[
            {
                "role": "user",
                "content": "Explain in one sentence how AI can help teachers."
            }
        ]
    )

    print("Gemma response:")
    print(response["message"]["content"])

test_gemma()
