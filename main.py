# File: main.py

from fastapi import FastAPI, HTTPException  # Original line
from pydantic import BaseModel
import requests
import json
import os
from pydantic import BaseModel
from typing import List, Dict, Any
from fpdf import FPDF
from fastapi.responses import FileResponse
import io
from dotenv import load_dotenv
load_dotenv()

from fastapi.middleware.cors import CORSMiddleware

from biz_roadmap_generation.gemini_roadmap import gemini_roadmap

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from fastapi import FastAPI, HTTPException, Response
import requests

# *** Modified Import Statement ***
from duckduckgo_search import DDGS  # Updated import for compatibility

def text_to_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    flowables = []

    for line in text.split('\n'):
        para = Paragraph(line, styles['Normal'])
        flowables.append(para)

    doc.build(flowables)
    buffer.seek(0)
    return buffer.getvalue()


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# OPENROUTER_API_KEY="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"

class IdeaModel(BaseModel):
    name: str
    mission: str
    goals: List[str]
    targetMarket: Dict[str, Any]
    primaryProduct: str
    sdgs: List[str]

class ChatRequest(BaseModel):
    # name: str
    idea: IdeaModel

# class ChatRequest(BaseModel):
#     message: str

# *** New Additions Start Here ***

# Added: Function to integrate DuckDuckGo search and format citations
def integrate_duckduckgo(query: str, max_results: int = 3) -> str:
    """Fetches DuckDuckGo search results and formats them as citations."""
    try:
        results = ddg_search(query, max_results=max_results)
        if not results:
            return "\n\nCitations: No relevant citations found."
        citations = "\n".join([f"[{i+1}] {res['title']}: {res['link']}" for i, res in enumerate(results)])
        return f"\n\nCitations:\n{citations}"
    except Exception as e:
        return f"\n\nCitations: DuckDuckGo search error: {str(e)}"

# *** New Additions End Here ***


@app.post("/investors")
async def getInvestors(request: ChatRequest):
    try:
        request_json = request.json()
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            },
           json={
                "model": "meta-llama/llama-3.2-3b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant, expert in starting non profits. Provide concise and accurate responses."
                    },
                    {
                        "role": "user",
                        # "content": "Considering this particular idea, Please provide steps on how I can connect with investors and list the investors I can potentially connect with, steps to take, and things to keep in mind during this."
                        "content": "The JSON file I provided contains the content of my non-profit idea. Use this to identify potential investors for my non-profit. Create a list of what categories of entities would be interested in investing in non-profits with a mission like mine. Examples of entity categories can be corporations, celebrities, or charities. Create a list of names for each category of entities. Each list should include at least 2 names. Your output should be in markdown format"
                    },
                    {
                        "role": "user",
                        "content": request_json
                    }
                ]
            }
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            main_content = response.json()["choices"][0]["message"]["content"]
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from OpenRouter API")

        # *** New Additions Start Here ***
        # Added: Append DuckDuckGo citations
        query = f"Investors for {request.idea.mission}"
        citations = integrate_duckduckgo(query)
        return main_content + citations
        # *** New Additions End Here ***

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenRouter API: {str(e)}")


@app.post("/grantInfo")
async def getGrantInfo(request: ChatRequest):
    try:
        request_json = request.json()
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            },
           json={
                "model": "meta-llama/llama-3.2-3b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant, expert in starting non profits. Provide concise and accurate responses."
                    },
                    {
                        "role": "user",
                        # "content": "Considering this particular idea, Please provide steps on how I can connect with investors and list the investors I can potentially connect with, steps to take, and things to keep in mind during this."
                        "content": "The JSON file I provided contains the content of my non-profit idea. Use this to identify potential grants I can apply to, for my non-profit. Create a list of entities that would be interested in providing grants to non-profits with a mission like mine. Your output should be in markdown format"
                    },
                    {
                        "role": "user",
                        "content": request_json
                    }
                ]
            }
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            main_content = response.json()["choices"][0]["message"]["content"]
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from OpenRouter API")

        # *** New Additions Start Here ***
        # Added: Append DuckDuckGo citations
        query = f"Grants for {request.idea.mission}"
        citations = integrate_duckduckgo(query)
        return main_content + citations
        # *** New Additions End Here ***

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenRouter API: {str(e)}")


@app.post("/getGrantProposal")
async def getGrantProposal(request: ChatRequest):
    try:
        # request_json = request.json()
        idea_description = request.json()
        
        prompt = f"""Write a persuasive grant proposal for a non-profit organization based on this {idea_description}. Include:

1. A captivating executive summary that highlights the problem, your solution, and potential impact
2. A clear problem statement with supporting data and real-world examples
3. Your organization's unique approach and proposed solution
4. Specific, measurable goals and objectives
5. A detailed implementation plan with timeline and milestones
6. Expected outcomes and how you'll measure success
7. A realistic budget breakdown
8. Your team's qualifications and relevant experience
9. Sustainability plan for long-term impact
10. Compelling conclusion that reinforces the urgency and importance of your project

Use a conversational yet professional tone, incorporate storytelling elements, and emphasize the human impact of your work. Provide concrete examples and data to support your claims. Tailor the proposal to align with the goals and values of potential funders."""
    
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            },
            json={
                "model": "meta-llama/llama-3.2-3b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant, expert in writing grant proposals for non-profits. Provide compelling, concise and accurate responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            propContent = response.json()["choices"][0]["message"]["content"]

            # *** New Additions Start Here ***
            # Added: Append DuckDuckGo citations
            query = f"Grant proposal examples for {request.idea.mission}"
            citations = integrate_duckduckgo(query)
            combined_content = propContent + citations
            # *** New Additions End Here ***

            pdf_bytes = text_to_pdf(combined_content)
            # Return the PDF as a downloadable file
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=grant_proposal.pdf"}
            )
            # return FileResponse(
            #     pdf_buffer,
            #     media_type="application/pdf",
            #     headers={"Content-Disposition": "attachment; filename=grant_proposal.pdf"}
            # )


        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from OpenRouter API")
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenRouter API: {str(e)}")


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
@app.post("/business_plan_roadmap")
async def getPlanning(request: ChatRequest):
    # *** New Additions Start Here ***
    # Added: Try-except block and append DuckDuckGo citations
    try:
        response_content = gemini_roadmap()

        # Append DuckDuckGo citations
        query = f"Business plan roadmap for {request.idea.mission}"
        citations = integrate_duckduckgo(query)
        combined_response = response_content + citations

        return combined_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roadmap generation error: {str(e)}")
    # *** New Additions End Here ***


# *** New Additions Start Here ***

# Added: Function to perform DuckDuckGo search
def ddg_search(query: str, max_results: int = 3) -> list:
    """Performs DuckDuckGo search and returns results"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return results
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
        return []

# *** New Additions End Here ***
