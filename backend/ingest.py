from dotenv import load_dotenv
import os
load_dotenv()
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# 1.Load the pdf
pdf_files = [
    "Data\\Think_CBT_Workbook_Static.pdf",
    "Data\\wellbeing-team-cbt-workshop-booklet-2016.pdf"
]

docs = []

for pdf in pdf_files:
    loader = PyPDFLoader(pdf)
    docs.extend(loader.load())

print(f"Loaded {len(docs)} pages.")
# 2.Chunks
text_splitter=RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)
split_docs=text_splitter.split_documents(docs)
print("pages:",len(docs))

# 3.Embeddings

from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 4.ChromaDB
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
vectorstore=Chroma.from_documents(
    split_docs,
    embeddings,
    persist_directory=os.path.join(BASE_DIR, "../vector_db"),
    collection_name="cbt_documents"
)

print("Ingestion completed")
