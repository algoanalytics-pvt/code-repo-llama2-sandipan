from typing import Any, Dict
from pathlib import Path
import json
import base64
import os
import yaml
from yaml.loader import SafeLoader

import streamlit as st
import toml



#@st.cache(allow_output_mutation=True, ttl=300)
def get_project_root() -> str:
    """Returns project root path.

    Returns
    -------
    str
        Project root path.
    """
    return str(Path(__file__).parent.parent)

def load_auth_config(auth_config: str) -> Dict[Any, Any]:
    """Loads auth configuration file.

    Parameters
    ----------
    auth_config : str
        Filename of auth configuration file.

    Returns
    -------
    dict
        auth configuration file.
    """   
    file_path = Path(get_project_root()) / f"config/{auth_config}"
    with file_path.open() as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def load_config(
    config_streamlit_filename: str) -> Dict[Any, Any]:
    """Loads configuration files.

    Parameters
    ----------
    config_streamlit_filename : str
        Filename of lib configuration file.

    Returns
    -------
    dict
        Lib configuration file.
    """
    config_streamlit = toml.load(Path(get_project_root()) / f"config/{config_streamlit_filename}")
    return dict(config_streamlit)

# get key metrics data
def get_key_metrics_data(news_for):
    file_path_stats_valuation = f"data/stats_valuation_data/{news_for}.json"
    with open(file_path_stats_valuation, "r") as json_file:
        key_metrics_data = json.load(json_file)
    return key_metrics_data



@st.cache_resource 
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)
    
@st.cache_resource    
def load_base64_image(image_path):
    with open(image_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode()
            
    return base64_image


@st.cache_data
def displayPDF(file,width=700,height=750):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width=100% height="{height}" type="application/pdf">'
    #pdf_display = F'<div><iframe src="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width: 100%;></iframe></div>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

@st.cache_data  
def load_sample_qa()->Dict:
    """Define a sample set of questions and answers
    """
    sample_qa = {
    "Give me a list of functions defined in binarysearch.py.": "The functions defined in `binary_search.py` are `linear_search`, `binary_search`, and `binary_search_recursive`. Each of these functions serves the purpose of finding an element within a list, with `binary_search` and `binary_search_recursive` being more efficient for sorted lists.",
    "How does binary search work?": "Binary search works by repeatedly dividing the search interval in half. If the value of the search key is less than the item in the middle of the interval, narrow the interval to the lower half. Otherwise, narrow it to the upper half. Repeatedly check until the value is found or the interval is empty.",
    "What is the time complexity of binary search?": "The time complexity of binary search is O(log n) where n is the number of elements in the array.",
    "Can merge sort be used on any data type?": "Merge sort can be used on any data type that can be compared. This means it can sort arrays of integers, floats, strings, or custom objects, provided there's a clear comparison logic.",
    "What is the difference between binary search and linear search?": "Binary search is more efficient than linear search for sorted lists, with a time complexity of O(log n) compared to O(n) for linear search. However, binary search can only be applied to a sorted list or array.",
    "Explain the merge function in merge_sort_exercise_solution.py.": "The `merge` function in `merge_sort_exercise_solution.py` takes two sorted lists (`left_list` and `right_list`), along with a key based on which the merge should occur, and an optional `descending` flag. It merges these two lists into a single sorted list by repeatedly comparing the smallest (or largest if `descending` is `True`) elements of each list and adding the smaller (or larger) one to the merged list. The process continues until both lists are empty, resulting in a combined sorted list."
}
    return sample_qa

def file_lister(rootdir,pyfiles,cppfiles,javafiles,_gettext):
    for file in os.listdir(rootdir):
        d = os.path.join(rootdir,file)
        if os.path.isdir(d):
            file_lister(d,pyfiles,cppfiles,javafiles,_gettext)
        else:
            if d.endswith(".py"):
                if d.endswith("__init__.py"):
                    pass
                else:
                    pyfiles.append(_gettext(d))
            elif d.endswith(".cpp"):
                cppfiles.append(_gettext(d))
            elif d.endswith(".java"):
                javafiles.append(_gettext(d))
    
    return tuple(pyfiles),tuple(cppfiles),tuple(javafiles)