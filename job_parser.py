
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from huggingface_hub import login
from langchain_core.tools import tool
from dotenv import load_dotenv
from datetime import date
import pandas as pd
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
You are an intelligent Job Posting parser.

Extract all the relevant information from the following job opening post. Present the output in structured JSON format with the following fields:

title

company

location

Employment Type (e.g., Full-time, Part-time, Contract) (if mentioned)

Remote/Hybrid/Onsite (if mentioned)

experience (e.g., 3+ years, entry-level, etc.)

Key Responsibilities (as bullet points)

skills (as bullet points)

Education Requirements (if mentioned)

Salary Range (if mentioned)

Application Deadline (if mentioned)

posted_date (if mentioned)

job_link (if mentioned)

Here's the job post text:
##input_job##

Important Rule: Do not return think part in the output or prefix, sufix or explaination, only return the above stated information in JSON format and nothing else.
"""
def get_job_list(df):
    l=[]
    for i in range(len(df)):
        prompt_with_data=prompt.replace('##input_job##',str(df.iloc[i]))
        res=model.invoke(prompt_with_data)
        res.content.replace('\n','')
        res_final=res.content.split("```json")
        res_final=res_final[1].split("```")
        doc_json=json.loads(res_final[0])
        l.append(doc_json)
    return l






# Extract all text from the PDF


