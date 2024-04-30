from langchain_community.embeddings import LlamaCppEmbeddings, HuggingFaceInstructEmbeddings, HuggingFaceBgeEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter,RecursiveJsonSplitter
import logging
from typing import List, Tuple
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import CSVLoader, PDFMinerLoader, TextLoader, UnstructuredExcelLoader, Docx2txtLoader
import numpy as np
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_community.document_loaders.parsers.txt import TextParser
from langchain_community.document_loaders import JSONLoader
import glob

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


# documents = load_documents_simple(SOURCE_DIRECTORY, DOCUMENT_MAP)
# text_documents, python_documents = split_documents(documents)

pyloader = GenericLoader.from_filesystem(
    path = "data",
    glob="**/[!.]*",
    suffixes=[".py"],
    parser=LanguageParser(language=Language.PYTHON, parser_threshold=0),
)

# jsonloader = JSONLoader(
#     file_path= glob.glob("data/**/*.json", recursive=True),
#     jq_schema='.'
# )

txtloader = GenericLoader.from_filesystem(
    path = "data",
    glob="**/[!.]*",
    suffixes=[".txt", ".md",".sh"],
    parser=TextParser(),
)


python_documents = pyloader.load()
# json_documents = jsonloader.load()
text_documents = txtloader.load()


text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
python_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON, chunk_size=1024, chunk_overlap=100)
# json_splitter = RecursiveJsonSplitter(max_chunk_size=300)


texts = python_splitter.split_documents(python_documents)
# texts.extend(json_splitter.split_json(json_documents))
texts.extend(text_splitter.split_documents(text_documents))
print('number of chunks',len(texts))
# print(texts)
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
vectorstore.save_local("")

