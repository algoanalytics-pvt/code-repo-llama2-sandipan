import streamlit as st 
import time
import logging
from utils.load import file_lister, load_sample_qa
from auth.authenthication import setup_authenticator
from model.chatbot_agent import setup_bot_agent
from utils.load import load_config
import random as r
from transformers import TextStreamer
import os

logging.basicConfig(level=logging.INFO)
SOURCE_DIRECTORY = "data"
# streamer = TextStreamer()

def display_streaming_summary(assistant_response: str):
    summary_style ="""
    background-color: #E5E8E8;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
    display: block;
    text_align: left;
    font-size: 18px; 
    color: black;
    justify-content: flex-start;
"""
    message_placeholder = st.empty()
    full_response = ""
    for chunk in assistant_response:
        full_response += chunk
        if chunk == " ":
            time.sleep(r.uniform(0.02,0.12))
        # elif chunk == "\n":
        else:
            time.sleep(0.001)  # Sleep to simulate typing
        # Add a blinking cursor to simulate typing
        message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
    
    # After the loop, display the full message without the cursor
    message_placeholder.markdown(
        f'<div style="{summary_style}">{full_response}</div>',
        unsafe_allow_html=True
    )

def demo_dashboard(_gettext):
                            
    global ui
    logging.info("Entered demo_dashboard function.")  

    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []
    
    # AVATARS
    config_data = load_config("config.toml")
    user_emoji = config_data["emojis"]["user_emoji"]
    chatbot_emoji = config_data["emojis"]["chatbot_emoji"]

    # CSS styles for user and chatbot messages
    user_message_style = config_data["chatbot_style"]["user_message_style"]
    chatbot_message_style = config_data["chatbot_style"]["chatbot_message_style"]
    
    # Load sample questions and their answers
    sample_qa = load_sample_qa()

    with st.container():

        chat_tab,login_tab = st.tabs([_gettext("Chatbot"), _gettext("Login")])

        with login_tab:
            _,login_collumn,_ = st.columns((0.3,0.4,0.3))
            with login_collumn:
                st.info('Login')
                login_detail=st.empty()
                login_detail.caption(_gettext("For login details contact info@algoanalytics.com"))
                            
                #----------Authenticaiton------------------------------
                authenticator = setup_authenticator() 
                name, authentication_status, username = authenticator.login('Login', 'main')
                
                if authentication_status:    
                    authenticator.logout('Logout', 'main')
                    st.success(f'Login Successful! Welcome, *{name}*!')
                    login_detail.empty()

                # check authentication   
                if authentication_status==False:
                    st.error('Username/password is incorrect')
                    
                if authentication_status == None:
                    st.warning('Please login for chat functionality')
        
        # authentication_status = True
        with chat_tab:
        
            content_column,chat_column =  st.columns((1,1))
            
            #--------content column------------------------- 
            with content_column:
                
                st.info(_gettext('Code Viewer'))
                
                pyfiles,cppfiles,javafiles = [],[],[]
                
                file_lister(SOURCE_DIRECTORY,pyfiles,cppfiles,javafiles,_gettext)
                
                # language = st.selectbox(_gettext("Choose Language"),(_gettext("Python"), _gettext("C++"), _gettext("Java")))

                # if language == "Python":
                #     if len(pyfiles) > 0:
                #         file1 = st.selectbox(_gettext("Choose a python file to display"), pyfiles)
                #         filepy = open(file1, "r")
                #         st.code(filepy.read(), language= "python", line_numbers=True,)
                #     else:
                #         st.write(_gettext("No Python files to display."))
                # if language == "C++":
                #     if len(cppfiles) > 0:
                #         file1 = st.selectbox(_gettext("Choose a C++ file to display"),cppfiles)
                #         filecpp = open(file1, "r")
                #         st.code(filecpp.read(), language= "cpp", line_numbers=True,)
                #     else:
                #         st.write(_gettext("No C++ files to display."))
                # if language == "Java":
                #     if len(javafiles) > 0:
                #         file1 = st.selectbox(_gettext("Choose a Java file to display"),javafiles)
                #         filejv = open(file1, "r")
                #         st.code(filejv.read(), language= "java", line_numbers=True,)
                #     else:
                #         st.write(_gettext("No Java files to display."))       
                    
                file1 = st.selectbox(_gettext("Choose a python file to display"), pyfiles)
                filepy = open(file1, "r")
                st.write(f"Current File: {os.path.splitext(os.path.basename(file1))[0]+os.path.splitext(os.path.basename(file1))[1]}:")
                st.code(filepy.read(), language= "python", line_numbers=True,)
                
                #--------Chatbot column-------------------------
                with chat_column:
                    if authentication_status is True:
                        st.info(_gettext('Welcome to Our LLM Powered Chatbot!'))
                        st.write("")
                        st.write("")
                        with st.expander(_gettext("Instructions"),expanded=False):
                            
                            # help instructions displayed
                            # help_instructions =_gettext("""<h11>Here are some helpful instructions on how to use the app!</h11>
                            #                 <ol>
                            #                     <li>The Repository provided has been sorted by languages.</li>
                            #                     <li>You can use the dropdowns in the Code Viewer to choose a language and a file to displayed.</li>
                            #                     <li>To chat with the agent please head to the Chatbox.</li>
                            #                     <li>Please <u>provide the full names of the files or functions</u> in a query for the best responses.</li>
                            #                 </ol>
                            #             """)
                            help_instructions =_gettext("""<h11>Here are some helpful instructions on how to use the app!</h11>
                                            <ol>
                                                <li>There has been a sample repository provided. Users will be able to provide their own repository soon.</li>
                                                <li>You can ask questions related to the sample repository.</li>
                                                <li>You can use the dropdown in the Code Viewer to choose a file to displayed.</li>
                                                <li>To chat with the agent please head to the Chatbox.</li>
                                                <li>Please <u>provide the full names of the files and functions</u> in a query for the best responses.</li>
                                            </ol>
                                        """)
                                
                            box_colour = "Aliceblue"
                            st.markdown(f"""<div style='background-color: {box_colour}; padding: 10px; border-radius: 5px; width: 100%;text-align: left;'>
                                                <span style='color: black;'>{help_instructions}</span>
                                            </div>
                                            
                                            
                                        """, unsafe_allow_html=True )
                            
                            st.write("")
                        
                        # setup chatbot agent 
                        chat_bot_agent = setup_bot_agent()

                        def update():
                                st.session_state.text = st.session_state.text_value        

                        with st.form(key='my_form', clear_on_submit=True):
                            input_text = st.text_input(_gettext('Chat with our LLM-Powered code Assistant'), value="", key='text_value')
                            submit = st.form_submit_button(label=_gettext('Answer'), on_click=update)
                        # global ui
                        ui=st.empty()    
                        if submit:
                            prompt = input_text
                            assistant_response = None
                            if prompt:
                                
                                ui.markdown(
                                        f'<div style="{user_message_style}">{user_emoji} {prompt}</div>',
                                        unsafe_allow_html=True
                                    )
                                
                                with st.spinner(_gettext('Generating your answer ✨')):
                                    print(_gettext('Generating Answer'))
                                    assistant_response = chat_bot_agent({"query":prompt})["result"]
                                
                                    
                                # store the output 
                                st.session_state.past.append(prompt)
                                st.session_state.generated.append(assistant_response)
                            
                        if st.session_state['generated']:
                            for i in range(len(st.session_state['generated']) - 1, -1, -1):
                                if st.session_state['past'][i] is not None and st.session_state['generated'][i] is not None:
                                    if i == len(st.session_state['generated']) - 1:
                                        ui.markdown(
                                            f'<div style="{user_message_style}">{user_emoji} {st.session_state["past"][i]}</div>',
                                            unsafe_allow_html=True
                                        )

                                        st.markdown(
                                            f'<div style="{chatbot_message_style}">{chatbot_emoji} {st.session_state["generated"][i]}</div>',
                                            unsafe_allow_html=True
                                        )
                                    else:
                                        st.markdown(
                                            f'<div style="{user_message_style}">{user_emoji} {st.session_state["past"][i]}</div>',
                                            unsafe_allow_html=True
                                        )

                                        st.markdown(
                                            f'<div style="{chatbot_message_style}">{chatbot_emoji} {st.session_state["generated"][i]}</div>',
                                            unsafe_allow_html=True
                                        )
                                        

                    elif authentication_status is None:
                        st.info(_gettext('Welcome to Our LLM Powered Chatbot!'))
                        st.write("")
                        st.write("")
                        with st.expander(_gettext("Instructions"),expanded=True):
                            
                            # help instructions displayed
                            help_instructions ="""<h11>Here are some instructions on how to use the app!</h11>
                                                    <ol>
                                                        <li>The repository provided has been sorted by languages.</li>
                                                        <li>Please Note: The sample questions are part of a Demo verison of the app with pre-computed responses.</li>
                                                    </ol>
                                                """
                            
                            box_colour = "Aliceblue"
                            st.markdown(f"""<div style='background-color: {box_colour}; padding: 10px; border-radius: 5px; width: 100%;'>
                                                <span style='color: black;'>{_gettext(help_instructions)}</span>
                                            </div>
                                            
                                            
                                        """, unsafe_allow_html=True )
                            
                            st.write("")
                        # Display sample questions for the user to choose from
                        selected_question = st.selectbox(_gettext("Select a sample question"), list(sample_qa.keys()), key='sample_question')
                        # When the user clicks the button, the hardcoded answer is displayed
                        if st.button(label=_gettext('Show answer'), key='show_answer'):
                            # Display the hardcoded answer
                            display_streaming_summary(sample_qa[selected_question]) 