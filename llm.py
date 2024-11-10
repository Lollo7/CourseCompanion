import os
import PyPDF2
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings  # Updated import for OpenAIEmbeddings
from langchain_community.vectorstores import FAISS  # Updated import for FAISS
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI  # Corrected import for ChatOpenAI from langchain_openai
from langchain.chains import RetrievalQA
from datetime import date
import json
# Read the contents of the output.json file
with open('output.json', 'r') as file:
    data = json.load(file)

with open('today.json', 'r') as file:
    today = json.load(file)

# Access the data from the output.json file
# Example: Print the value of the 'result' key
# print(data['result'])

# Load environment variables from .env file (including the OpenAI API key)
load_dotenv()

# Retrieve the OpenAI API key from environment variables
# openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_key = "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"

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

# Function to extract text from PDF files
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:  # Only append non-empty pages
                text += page_text + "\n"
        return text

# Example: Replace with your actual PDF file paths
downloaded_files = []
for file in os.listdir('personal/course_17700000000698456_files'):
    if file.endswith('.pdf'):
        downloaded_files.append(file)
# print(downloaded_files)
extracted_texts = []

# Extracting texts from the downloaded files and ensuring non-empty content
for file_path in downloaded_files:
    file_path = "personal/course_17700000000698456_files/" + file_path
    # print(f"Extracting text from: {file_path}")
    if file_path.endswith('.pdf'):
        extracted_text = extract_text_from_pdf(file_path)
        if extracted_text.strip():  # Check if extracted text is not empty
            extracted_texts.append(extracted_text)

# Ensure that we have extracted texts before proceeding
if not extracted_texts:
    raise ValueError("No valid text was extracted from the provided PDF files.")

# Create documents from extracted texts
documents = [Document(page_content=text) for text in extracted_texts]

# Split documents into smaller chunks for better embedding and retrieval performance
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
split_docs = text_splitter.split_documents(documents)

# Ensure there are split documents before proceeding with embeddings
if not split_docs:
    raise ValueError("No documents were split for embedding.")

# Create embeddings for each document chunk using OpenAI's embedding model (API key is loaded from environment)
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# Generate vector store using FAISS with document embeddings
vectorstore = FAISS.from_documents(split_docs, embeddings)

# Set up the retriever to search for relevant documents based on similarity
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# Define the prompt template for the LLM to generate responses based on retrieved context
prompt_template = """
You are an assistant helping with course scheduling. Use the following course material to answer the question:

Context:
{context}

Question:
{question}

Answer:
"""

prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# Initialize LangChain's ChatOpenAI LLM (e.g., GPT-4o-mini or GPT-3.5-turbo) using the API key from environment variables
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=openai_api_key)

# Create a RAG chain that combines retrieval and generation steps using LangChain's RetrievalQA chain.
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True  # Optionally return source documents for further insights.
)

# Example query to demonstrate functionality of the RAG system using 'invoke' instead of '__call__'.
def run_example_query(query):
    """Run an example query through the RAG chain and handle multiple output keys."""
    response = rag_chain.invoke({"query": query})  # Use 'invoke' instead of '__call__'
    
    # Accessing both result and source_documents from the response dictionary
    generated_response = response["result"]
    source_docs = response["source_documents"]
    
    print("Generated Response:", generated_response)
    
    # print("\nSource Documents:")
    # for doc in source_docs:
    #     print(doc.page_content[:500])  # Print first 500 characters of each source doc.

sample_output = '''
event = {
      'summary': 'Google I/O 2015',
      'description': 'A chance to hear more about Google\'s developer products.',
      'start': {
        'dateTime': '2015-05-28T09:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
      },
      'end': {
        'dateTime': '2015-05-28T17:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
      },
    }
    '''

# print(data)


# Main execution block: Run an example query when this script is executed directly.
if __name__ == '__main__':
    run_example_query(
        f"Given these assignments, {data}, my current events {today},"
        f"and the current day being {date.today()}, I want help planning"
        f"out my assignmets around what I already have scheduled. Can you create"
        f"a scheule based on assignment points and difficulty and output your response"
        f"in the following format {sample_output}. I expect only a list of json objects and"
        f"no other information. I only want the most important assignments that are due the earliest."
        f"Please only include a schedule for today {date.today()}."
    )