from google import genai

class Custom_GenAI:
    def __init__(self, api_key, model="gemini-2.0-flash"):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)

    def ask_ai(self, prompt, temperature=0.3):
        try:
            chat = self.model.start_chat()
            response = chat.send_message(prompt, generation_config={"temperature": temperature})
            return response.text.strip()
        except Exception as e:
            return f"❌ LLM error: {e}"
