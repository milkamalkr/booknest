#ort google.generativeai as genai
from google import genai
# Paste your API key here
# genai.configure(api_key="AIzaSyB9wgZzpxY_4Imak8rwWLasi1o7By541mU")

# # Choose a model (free tier supported model)
# model = genai.GenerativeModel("gemini-1.5-flash")

# response = model.generate_content("Explain AI in simple words")

# print(response.text)



def main():
    # 1. Initialize the client by passing the API key directly
    # Replace "your-api-key-here" with your actual Gemini API key
    client = genai.Client(api_key="AIzaSyB9wgZzpxY_4Imak8rwWLasi1o7By541mU")

    try:
        # 2. Call the generate_content method
        # Parameters: model name, and the prompt (contents)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Explain quantum computing in two simple sentences."
        )
        
        # 3. Print the text response
        print("Gemini Response:\n" + response.text)
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")

if __name__ == "__main__":
    main()