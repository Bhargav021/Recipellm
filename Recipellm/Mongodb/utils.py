import re
import json

def clean_query(response_text):
    if "```" in response_text:
        response_text = response_text.split("```")[1]
    return response_text.strip()

def extract_json_block(text):
    match = re.search(r'(\{[\s\S]*?\})', text)
    return match.group(1) if match else text

def format_mongo_results(results):
    if not results:
        return "<b>No information found in database.</b>"

    lines = []
    for doc in results:
        lines.append("<li>" + ", ".join(f"<b>{k}:</b> {v}" for k, v in doc.items() if k != "_id") + "</li>")
    return "<b>Query Results:</b><br><ul>" + "\n".join(lines) + "</ul><br>"
