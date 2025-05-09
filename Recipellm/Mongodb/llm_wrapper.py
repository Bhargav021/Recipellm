import google.generativeai as genai

class Custom_GenAI:
    def __init__(self, API_KEY):
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def ask_ai(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text



