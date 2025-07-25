from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from job_parser import get_job_list
from langchain_core.documents import Document
from resume_parser import get_resume
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
hf_token = os.getenv("HF_TOKEN")


# Load the model


model_name = "sentence-transformers/all-mpnet-base-v2"

def load_docs(resume,df):
    print("--------loading docs-------")
    job_list=get_job_list(df)
    documents = []

    for job in job_list:
        print(f"---Processing job for {job}")
        # You can customize this: serialize full dict or format selected fields
        text = "\n".join(f"{k}: {v}" for k, v in job.items())
        
        doc = Document(page_content=text, metadata=job)  # you can keep job dict in metadata too
        documents.append(doc)


    embedding_model = HuggingFaceEmbeddings(model_name=model_name)
    vector_store = FAISS.from_documents(documents,embedding_model)

    # vector_store = FAISS.from_documents(sentence_embedding, data)
    retriever = vector_store.as_retriever(    search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.4, "k": 4})

    resume_content=get_resume(resume)
    res=retriever.invoke(resume_content)
    df = pd.DataFrame([doc.metadata for doc in res])
    print("---Completed AI Job matching---")
    return df


