from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
import os

embeddings=HuggingFaceEmbeddings(
     model_name="sentence-transformers/all-MiniLM-L6-v2"
)

Base_DIR=os.path.dirname(os.path.abspath(__file__))
   
vectorstore =Chroma(
    persist_directory=os.path.join(Base_DIR, "../vector_db"),
    embedding_function=embeddings,
    collection_name="cbt_documents"
)

retriever=vectorstore.as_retriever(search_kwargs={"k":3})
def retrieve_context(query):
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant context found"

    context = "\n\n".join([
        doc.page_content.replace("\n", " ").strip()
        for doc in docs
    ])

    return context
    
def retriever_node(state):
    query = state["query"]

    docs = retriever.invoke(query)
    print("Debug docs:", docs)

    if not docs:
        return {"context": "No relevant context found."}

    context = "\n\n".join([
         doc.page_content.replace("\n", " ").strip()
         for doc in docs
    ])

    return {
        "context": context
    }

print("DB COUNT:", vectorstore._collection.count())
if __name__ == "__main__":
    while True:
        q = input("You: ")
        result = retriever_node({"query": q})
        print("Context:\n", result["context"])