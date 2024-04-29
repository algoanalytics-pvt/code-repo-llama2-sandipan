# Import section
import numpy as np
import streamlit as st
from langchain_community.chat_models import ChatAnyscale
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler 
from utils.prompt_template_utils import get_prompt_template
import logging
import os
from langchain_openai import OpenAIEmbeddings
from .load_models import (
    load_quantized_model_gguf_ggml,
    load_quantized_model_qptq,
    load_full_model,
    MAX_NEW_TOKENS
)
from transformers import GenerationConfig, pipeline


# Initialize logging
logging.basicConfig(level=logging.INFO)


# Constants
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
ANYSCALE_API_KEY = ""
os.environ["ANYSCALE_API_BASE"] = "https://api.endpoints.anyscale.com/v1"
os.environ["ANYSCALE_API_KEY"] = ANYSCALE_API_KEY 

# Utility function to load documents without multi-threading
logging.info("Initialized constants and environment variables.")
# @st.cache_resource
def load_model(device_type, model_id, model_basename=None, LOGGING=logging):
    """
    Select a model for text generation using the HuggingFace library.
    If you are running this for the first time, it will download a model for you.
    subsequent runs will use the model from the disk.

    Args:
        device_type (str): Type of device to use, e.g., "cuda" for GPU or "cpu" for CPU.
        model_id (str): Identifier of the model to load from HuggingFace's model hub.
        model_basename (str, optional): Basename of the model if using quantized models.
            Defaults to None.

    Returns:
        HuggingFacePipeline: A pipeline object for text generation using the loaded model.

    Raises:
        ValueError: If an unsupported model or device type is provided.
    """
    logging.info(f"Loading Model: {model_id}, on: {device_type}")
    logging.info("This action can take a few minutes!")

    if model_basename is not None:
        if ".gguf" in model_basename.lower():
            return load_quantized_model_gguf_ggml(model_id, model_basename, device_type, LOGGING)
        elif ".ggml" in model_basename.lower():
            model, tokenizer = load_quantized_model_gguf_ggml(model_id, model_basename, device_type, LOGGING)
        else:
            model, tokenizer = load_quantized_model_qptq(model_id, model_basename, device_type, LOGGING)
    else:
        model, tokenizer = load_full_model(model_id, model_basename, device_type, LOGGING)

    # Load configuration from the model to avoid warnings
    generation_config = GenerationConfig.from_pretrained(model_id)
    print(generation_config)
    # see here for details:
    # https://huggingface.co/docs/transformers/
    # main_classes/text_generation#transformers.GenerationConfig.from_pretrained.returns

    # Create a pipeline for text generation
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=MAX_NEW_TOKENS,
        temperature=0.001,
        # top_p=0.95,
        repetition_penalty=1.15,
        generation_config=generation_config,
    )

    local_llm = HuggingFacePipeline(pipeline=pipe)
    logging.info("Local LLM Loaded")

    return local_llm


# Main setup function
@st.cache_resource
def setup_bot_agent():

    vectorstore = FAISS.load_local("C:/Users/ragha/Documents/GitHub/code-repo-llama2-sandipan", OpenAIEmbeddings(model="text-embedding-3-small"), allow_dangerous_deserialization=True)

    template = """You are a software engineer answering to a senior software engineer, you will use the provided knowledge to answer questions about the code. Think step by step and respond appropriately If you can not answer a question based on 
    the provided context, inform the user. Do not use any other prior information for answering. Give concise but fully explained answers in a bulleted format. Do not narrate the conversation.
    """

    ANYSCALE_MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
    # ANYSCALE_MODEL_NAME = "codellama/CodeLlama-70b-Instruct-hf"
    LLM = ChatAnyscale(model_name = ANYSCALE_MODEL_NAME)
   
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k":3})
    
    prompt, memory = get_prompt_template(system_prompt=template, promptTemplate_type="llama", history=False)

    qa = RetrievalQA.from_chain_type(
        llm=LLM,
        chain_type="stuff",  # try other chains types as well. refine, map_reduce, map_rerank
        retriever=retriever,
        return_source_documents=True, # verbose=True,
        chain_type_kwargs={"prompt": prompt, "memory": memory},
    )

    return qa

if __name__ == "__main__":
    chat_bot_agent = setup_bot_agent()
    file = open("../sample_questions.txt", "r")
    questions = file.readlines
    # print(questions)
    # for i in file.read
    # chat_bot_agent.run("Explain the partition() function")
