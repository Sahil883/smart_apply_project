from pdfminer.high_level import extract_text
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from huggingface_hub import login
from langchain_core.tools import tool
from dotenv import load_dotenv
from datetime import date
import json
import os
load_dotenv()
hf_token = os.getenv("HF_TOKEN")


today = date.today()


llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
    task="text-generation"
    
)


model = ChatHuggingFace(llm=llm)

prompt="""
You are an intelligent resume parser.

Given the following string containing the content of a resume, extract and return a Python dictionary with the following fields:

"Name": The full name of the candidate.

"Years of experience": Total years of professional experience (as an integer or float) based on todays date that is ##date##.

"Skills": A list of relevant technical or professional skills.

"Experience": A brief summary or bullet points of prior job roles and responsibilities.

"Current company and position": The name of the company where the person is currently working (if mentioned) and the persons position in the company.

"Certifications": A list of any professional certifications (if available, else return an empty list).

Use only the information found in the input text. If any field is missing or not clearly mentioned, return None or an empty list accordingly.

Input Resume:
##input_resume##
"""
def get_resume(pdf):
    print('------Parsing resume---------')
    text = extract_text(pdf,codec='utf-8')
    prompt_with_data=prompt.replace('##input_resume##',text)
    prompt_with_data=prompt_with_data.replace('##date##',str(today))

    res=model.invoke(prompt_with_data)
    res_final=res.content.split("```python")
    res_final=res_final[1].split("```")
    print('------Parsing resume completed---------')
    return res_final






# Extract all text from the PDF


