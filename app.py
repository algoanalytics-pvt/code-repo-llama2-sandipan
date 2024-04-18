import base64
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_option_menu import option_menu
from homepage_content import homepage_vf,contact_us,custom_footer
from dashboard import demo_dashboard
from model.chatbot_agent import setup_bot_agent

if "lang" not in st.session_state:
    
    st.session_state.lang = "en"
    
# TRANSLATE
#=============================================================================================================
import gettext
_gettext = gettext.gettext


try:
  localizator = gettext.translation('base', localedir='locales', languages=[st.session_state.lang])
  localizator.install()
  _gettext = localizator.gettext 
except Exception as e:
  print('inside exception')
  print(e)
#=============================================================================================================

# Page Configuraion
st.set_page_config(page_title="ChatBot Github Repo",
                   page_icon="ui_assets/images/algo-logo.png",
                   layout="wide",
                   )

with open('css/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ----------Website Header section------------------------
with st.container():

    brand_logo, demo_button_section,view_all_button,language_option,  = st.columns((2,1.8,0.5,0.4)) 

    #=============================================================================================================
    # ----------------language section  
    with language_option:
        # # this is center the drop down widget
        # st.markdown(
        #     """
        #     <style>
                
        #         div[data-testid="column"]:nth-of-type(3)
        #         {
        #             text-align: end;
        #             align-items: center;
        #             background-color": #E1EDFA
        #         } 
        #     </style>
        #     """,unsafe_allow_html=True
        #     )
        
        # col1, col2 = st.columns((0.1,1))

        # with col2:
        #     option = st.selectbox(label = "Language Selector", options = ("en","ja"), label_visibility = "collapsed", key = "lang")
        pass
        
     #=============================================================================================================   



    # Add Algoanalytics logo
    with brand_logo:
       
        
        #brand_logo_image_path = "ui_assets/images/algo_logo.jpg"
        brand_logo_image_path = "ui_assets/images/algo-logo.png"
        
        with open(brand_logo_image_path, "rb") as img_file:
            brand_image = base64.b64encode(img_file.read()).decode()
        

        app_name1 = _gettext("AlgoCode Programming Chat Assistant")
        st.markdown(f'''
        <div class='brand_logo_namestyle'>
            <img src="data:image/png;base64,{brand_image}" width="70">
            <div style="flex: 1; text-align: start; padding-left:5vw;">
            <h4 class='app-name'>{app_name1}</h4>
            </div>
            
        </div>''', unsafe_allow_html=True)


    with demo_button_section:   
        st.markdown(
        """
        <style>
            
            div[data-testid="column"]:nth-of-type(2)
            {
                text-align: start;
                align-items: center;
                background-color": #E1EDFA
            } 
        </style>
        """,unsafe_allow_html=True
        )

        if 'option_menu' not in st.session_state:
            st.session_state.option_menu="Overview"
            
        if st.session_state.get('demo_button', False):
            st.session_state['manual_select'] = 1
            manual_select = st.session_state['manual_select']
        else:
            manual_select = None
            
        selected_tab =  option_menu(None, [_gettext("Overview"), _gettext("Demo"),_gettext('Contact us')],
            icons=['house-fill', 'arrow-up-circle-fill','telephone-fill'],
            key='option_menu',
            menu_icon="cast", default_index=0, orientation="horizontal",manual_select=manual_select,
            
            styles={
                        "container": {"padding": "0.01", "background-color": "#E1EDFA00"},#E1EDFA99
                        "nav-link": {
                            "font-size": "15px",
                            "color":"grey",
                            "text-align": "center",
                            "margin": "0px",
                            "--hover-color": "#E1EDFA",
                            "--background-color" :"grey"
        
                        },
                        "nav-link-selected": {"background-color": "#789BE600","color":"#789BE6"},
                        
                    },
            
            )
#------Home page ------------------------------ 

    st.markdown(
        """
        <style>
        .horizontal-line {
            height: 1px;
            width: calc(100% + 3rem); /* Adjusted width to account for the left and right padding in your main layout */
            margin-left: -1.5rem; /* Adjusted negative margin to counteract the left padding in your main layout */
            background-color: #D3D3D3;
            box-shadow: 0px 1px 2px 0px rgba(0,0,0,0.2);
            margin-top: 0;
            padding: 0;
            border: none;
        }
        </style>
        <hr class="horizontal-line">
        """,
        unsafe_allow_html=True
    )


def on_click_js(url="https://apps.onestop.ai/llm-dashboard/"):
    link_open =f"""
        <script>
            var win = window.open('{url}', '_blank');
            win.focus();
        </script>
    """
    st.markdown(link_open,unsafe_allow_html=True)

with view_all_button:
    pass
    # st.markdown(
    # """
    # <style>
    #     div[data-testid="column"]:nth-of-type(1)
    #     {
    #         align-items: center
    #     } 

    #     div[data-testid="column"]:nth-of-type(2)
    #     {
            
    #         text-align: start;
    #     } 
    #     div[data-testid="column"]:nth-of-type(3)
    #     {
    #         text-align: center;
            
    #     } 
    # </style>
    # """,unsafe_allow_html=True
    # )

    
    # def create_link(url, label, hover_color="#00008b"):  # You can change the hover color here
    #     # HTML and CSS to style the link as a button, including hover effect
    #     button_html = f"""
    #     <style>
    #     .custom-button {{
    #         color: white; 
    #         background-color: #799BE6; 
    #         border: none; 
    #         border-radius: 4px; 
    #         padding: 5px 10px; 
    #         text-align: center; 
    #         text-decoration: none; 
    #         display: inline-block; 
    #         font-size: 16px; 
    #         margin: 4px 2px; 
    #         cursor: pointer;
    #         transition: background-color 0.3s;  /* Smooth transition for background color change */
    #     }}
    #     .custom-button:hover {{
    #         background-color: {hover_color};  /* Change hover background color */
    #     }}
    #     </style>
    #     <a href="{url}" target="_blank">
    #     <button class="custom-button">{label}</button></a>
    #     """

    #     st.markdown(button_html, unsafe_allow_html=True)

    # # Usage
    # button_name = _gettext("LLM Dashboard")
    # create_link("https://apps.onestop.ai/llm-dashboard/", button_name)

if st.session_state.option_menu in ["Overview","概要"]: #==_gettext("Home")
    
    homepage_vf(_gettext)
    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
    custom_footer()
    
    # for cachhing 
    chat_bot_agent = setup_bot_agent()
    
#---------Dashboard-----------------------------
elif st.session_state.option_menu in ["Demo","デモ"]:

    demo_dashboard(_gettext)    
    
elif st.session_state.option_menu in ["Contact us","お問い合わせ"]:

    contact_us(_gettext)

hide_streamlit_style = """
            <style>
            
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)         