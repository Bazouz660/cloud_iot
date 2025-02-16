from google import genai

client = genai.Client(api_key="AIzaSyDyFSz_BSSZAIqFP_BXRZw02FjU99bX1do")
response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works"
)
print(response.text)