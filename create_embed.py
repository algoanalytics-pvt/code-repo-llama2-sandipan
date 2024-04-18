from langchain_community.embeddings import LlamaCppEmbeddings, HuggingFaceInstructEmbeddings, HuggingFaceBgeEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
import logging
from typing import List, Tuple
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import CSVLoader, PDFMinerLoader, TextLoader, UnstructuredExcelLoader, Docx2txtLoader
import numpy as np
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_community.document_loaders.parsers.txt import TextParser

OPENAI_API_KEY = ""
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize environment variables
# load_dotenv()
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# openai.api_key = OPENAI_API_KEY

# Constants
SOURCE_DIRECTORY = "data"
DOCUMENT_MAP = {
    ".txt": TextLoader,
    ".md": TextLoader,
    ".py": TextLoader,
    ".pdf": PDFMinerLoader,
    ".csv": CSVLoader,
    ".xls": UnstructuredExcelLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".docx": Docx2txtLoader,
    ".doc": Docx2txtLoader,
}

def load_documents_simple(source_dir: str, DOCUMENT_MAP: dict) -> List:
    logging.info(f"Starting to load documents from {source_dir}.")
    documents = []
    
    for root, _, files in os.walk(source_dir):
        for file_name in files:
            file_extension = os.path.splitext(file_name)[1]
            source_file_path = os.path.join(root, file_name)
            
            if file_extension in DOCUMENT_MAP.keys():
                loader_class = DOCUMENT_MAP.get(file_extension)
                
                if loader_class:
                    loader = loader_class(source_file_path)
                    
                    try:
                        document = loader.load()[0]
                        documents.append(document)
                    except Exception as e:
                        logging.error(f"An error occurred while loading {source_file_path}: {e}")
                        
    logging.info("Finished loading documents.")
    return documents

# Utility function to split documents based on their type
def split_documents(documents: List) -> Tuple[List, List]:
    logging.info("Starting to split documents.")
    text_docs, python_docs = [], []
    for doc in documents:
        file_extension = os.path.splitext(doc.metadata["source"])[1]
        if file_extension == ".py":
            python_docs.append(doc)
        else:
            text_docs.append(doc)
    logging.info("Finished splitting documents.")
    return text_docs, python_docs

# documents = load_documents_simple(SOURCE_DIRECTORY, DOCUMENT_MAP)
# text_documents, python_documents = split_documents(documents)

pyloader = GenericLoader.from_filesystem(
    path = "data/algorithms",
    glob="**/[!.]*",
    suffixes=[".py"],
    parser=LanguageParser(language=Language.PYTHON, parser_threshold=0),
)

# txtloader = GenericLoader.from_filesystem(
#     path = "data/algorithms",
#     glob="**/[!.]*",
#     suffixes=[".txt",".md",],
#     parser=TextParser,
# )

# text_documents = txtloader.load()
python_documents = pyloader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON, chunk_size=512, chunk_overlap=50
)

# texts = text_splitter.split_documents(text_documents)
# texts.extend(python_splitter.split_documents(python_documents))

texts = python_splitter.split_documents(python_documents)
print('number of chunks',len(texts))

# # Create embeddings FOR INTRUCTOR LARGE
# embeddings = HuggingFaceInstructEmbeddings(
#     model_name="hkunlp/instructor-large",
#     model_kwargs={"device": "cpu"},
# )

# # CREATE EMBEDDINGS FOR BGE LARGE
# model_name = "BAAI/bge-large-en-v1.5"
# model_kwargs = {'device': 'cpu'}
# encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity
# embeddings = HuggingFaceBgeEmbeddings(
#     model_name=model_name,
#     model_kwargs=model_kwargs,
#     encode_kwargs=encode_kwargs,
# )

# CREATE EMBEDDINGS USING OPENAI TEXT-EMBEDINGS-SMALL
model_name = "text-embedding-3-small"
embeddings = OpenAIEmbeddings(model=model_name)

vectorstore = FAISS.from_documents(documents=texts, embedding=embeddings)
np.save(f"openai_text_embeddings_small.npy", vectorstore,allow_pickle=True)
