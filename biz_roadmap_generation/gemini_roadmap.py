# File: bizbot/gemini_roadmap.py

import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
import json

# *** Modified Import Statement ***
from duckduckgo_search import DDGS  # Updated import for compatibility

def gemini_roadmap():
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    # system_instruction example from https://ai.google.dev/gemini-api/docs/system-instructions?lang=python
    # system_instruction = "You are a cat. Your name is Neko."
    # user_prompt = "Good morning! How are you?"

    system_instruction = "You are a consultant for non-profits. You receive details on the type of non-profit your client wants to create. You have 20 years of experience advising for clients across the globe, and specialize in creating business plans and actionable roadmaps for aspirational non-profit founders. You consider your clients' country of operation when providing advice. When you provide advice, you include website links to resources for your clients to follow. Double check these links work."

    # meowsicals - eritrean cat music
    user_prompt = "Please advise on how to create my non-profit, Meowsicals. Our goal is to bring the joy of music to stray cats in Eritrea. Our goal is for 15 percent of our stray cat population to be serenaded at least once a week"

    # open and read the JSON file
    # with open('sample_input.json', 'r') as file:
    #         data = json.load(file)

    # print("Data: ")
    # print(data)


    model=genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        # system_instruction="You are a cat. Your name is Neko."
        system_instruction = system_instruction
    )

    # response = model.generate_content("Good morning! How are you?")
    response = model.generate_content(user_prompt)
    
    # *** New Additions Start Here ***
    # Removed duplicate integrate_duckduckgo function

    # Define the query based on the non-profit's mission
    query = "Bring the joy of music to stray cats in Eritrea"

    # Get DuckDuckGo citations using updated function
    try:
        ddg_search = DDGS()
        results = ddg_search.text(query, max_results=3)  # Use .text() method
        if not results:
            citations_text = "\n\nCitations: No relevant citations found."
        else:
            citations_text = "\n\nCitations:\n" + "\n".join([f"[{i+1}] {res['title']}: {res['link']}" for i, res in enumerate(results)])
    except Exception as e:
        citations_text = f"\n\nCitations: Unable to fetch citations - {str(e)}"

    # Append citations to the response text
    combined_response = response.text + citations_text

    print(combined_response)
    return combined_response  # Ensure that the function returns the combined response
    # *** New Additions End Here ***
