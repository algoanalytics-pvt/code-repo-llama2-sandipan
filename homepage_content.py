import streamlit as st
import base64
from utils.design_utils import create_specific_feature
from utils.load import load_base64_image
import streamlit.components.v1 as components

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
    
def homepage_vf(_gettext):


    # Base64 encoding of images
    image1_base64 = image_to_base64("ui_assets/images/programming-concept-illustration_114360-1351.jpg")
    image2_base64 = image_to_base64("ui_assets/images/programmer-1653351_1920.png")
    image3_base64 = image_to_base64("ui_assets/images/online-3410266_1920.jpg")

    title =_gettext('AlgoCode')
    sub = _gettext("Your assistant to help you navigate and understand complex repositories with ease!")
    
    feature1_heading = _gettext('Intelligent Code Explanation')
    feature1_description =_gettext("Say farewell to confusion! Our cutting-edge chatbot effortlessly comprehends any mainstream language, including python, C++, and java. Minimize reading and wasted time as our chatbot takes care of understanding code, and letting you have an interactive explanation.")
    
    feature2_heading = _gettext('Precise and Summarized Responses')
    feature2_description = _gettext("No more lengthy explanations. Our chatbot responds with precision and clarity, distilling complex information into easily understandable summaries. Receive quick and accurate answers, enhancing your experience and confidence in your work.")
    
    
    feature3_heading = _gettext('Contextually Aware')
    feature3_description =_gettext("Our chatbot is smart enough to recognize when questions are out of context or require more information. It engages in interactive conversations, guiding users to provide the necessary details for accurate responses. This ensures that every interaction is productive and meaningful.")
    
    # Define the HTML content with Base64 encoded images

    st.markdown(f"""
        <style>
            body {{
                font-family: 'Poppins', sans-serif;
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                color: #333;
                background-color: #ffffff;
            }}
            .hero-text {{
                text-align: center;
            }}
            .hero-text h1 {{
                font-size: 2rem;
                color: #0a4e8d; /* Adjust color */
                font-weight: bold;
                margin-bottom: 0rem;
                text-shadow: 2px 2px 8px #c2c2c2; /* Subtle text shadow */
            }}
            .hero-text h2 {{
                font-size: 1.2rem;
                color: #333333;2/* Adjust color */
                margin: 0rem 0;
                line-height: 1;
            }}
            .hero-text h3 {{
                font-size: 1rem;
                color: #333333;2/* Adjust color */
                margin: 0rem 0;
                line-height: 1;
            }}
        </style>
        <body>
        <div class="hero-text">
            <h1>{title}</h1>
            <h2>{sub}</h2>
        </div>
        </body>
    """, unsafe_allow_html=True)
    button_name = _gettext('Try Demo')
    st.button(button_name,key ='demo_button', type="primary")
    button_style = """
    <style>
        div.stButton {
        text-align: center;
        }
        div.stButton > button:first-child {
            display: inline-block;
            padding: 10px 20px;
            margin: 10px 0;
            border-radius: 25px;
            background-color: #0a4e8d; /* Green background */
            color: white; /* White text */
            border: none;
            cursor: pointer;
            font-size: 18px;
            transition: background-color 0.3s, box-shadow 0.3s;
        }
        div.stButton > button:first-child:hover {
            background-color: #00008b; /* Darker green on hover */
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        }
    </style>
    """
    
    st.markdown(button_style, unsafe_allow_html=True)
    st.markdown(f"""
        <style>
            .features {{
                text-align: center;
                padding-top: 1.5rem;
                background: white;
            }}
            .features-container {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1rem;
            }}
            .feature-item {{
                background: #eef2f7;
                padding: 1rem;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .feature-item h3 {{
                font-size: 1.7rem;
                color: #2193b0;
                margin: 0rem 0;
            }}
            .feature-item p {{
                font-size: 1rem;
                color: #333;
            }}
            
            .feature-item img {{
                width: 100%;
                object-fit: cover; /* Maintain aspect ratio */
                border-radius: 10px;
                margin-top: 0px;
            }}
        </style>
        <div class="features">
            <div class="features-container">
                <div class="feature-item">
                    <img src="data:image/png;base64,{image1_base64}">
                    <h3>{feature1_heading}</h3>
                    <p>{feature1_description}</p>
                </div>
                <div class="feature-item">
                    <img src="data:image/jpeg;base64,{image2_base64}">
                    <h3>{feature2_heading}</h3>
                    <p>{feature2_description}</p>
                </div>
                <div class="feature-item">
                    <img src="data:image/jpeg;base64,{image3_base64}">
                    <h3>{feature3_heading}</h3>
                    <p>{feature3_description}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
def contact_us(_gettext):
    col1, col2, col3 = st.columns(3)

    #Address
    address_title = _gettext("Address")
    address = _gettext("""Alacrity India Innovation Centre, Ideas to Impacts Building.
                \nPallod Farm Lane 3, \n\n Near Vijay Sales, \n\n Baner Road, Pune - 411045""")
    col1.markdown(f"<h3>{address_title}</h3>", unsafe_allow_html=True)
    col1.info(address)

    # Email
    email_title = _gettext("Email")
    email_id = _gettext("info@algoanalytics.com")
    col2.markdown(f"<h3 style='text-align: left;'>{email_title}</h3>", unsafe_allow_html=True)
    col2.warning(email_id)

    # Load base64 images
    twitter_image = load_base64_image("ui_assets/images/twitter-x-logo-png.png")
    ig_image = load_base64_image("ui_assets/images/instagram-logo-transparent.png")
    linked_in_image = load_base64_image("ui_assets/images/linkedin-logo-transparent.png")
    fb_image = load_base64_image("ui_assets/images/facebook-logo-png.png")

    # Social Media Links with added space
    twitter_tag = f"<img src='data:image/png;base64,{twitter_image}' width='50' style='margin-right: 10px;'>"
    ig_tag = f"<img src='data:image/png;base64,{ig_image}' width='50' style='margin-right: 10px;'>"
    linked_in_tag = f"<img src='data:image/png;base64,{linked_in_image}' width='50' style='margin-right: 10px;'>"
    fb_tag = f"<img src='data:image/png;base64,{fb_image}' width='50' style='margin-right: 10px;'>"

    social_media_links = f"""
    <div style="text-align: left;">
        <a href="https://twitter.com/AlgoanalyticsIn" target="_blank" rel="noopener noreferrer">{twitter_tag}</a>
        <a href="https://www.linkedin.com/company/algoanalytics/" target="_blank" rel="noopener noreferrer">{linked_in_tag}</a>
        <a href="https://www.facebook.com/Algoanalytics-1861931557423786" target="_blank" rel="noopener noreferrer">{fb_tag}</a>
        <a href="https://instagram.com/algoanalyticsin?igshid=OGQ5ZDc2ODk2ZA==" target="_blank" rel="noopener noreferrer">{ig_tag}</a>
    </div>
    """

    # Social Presence
    sm_title = _gettext("Social Presence")
    col3.markdown(f"<h3 style='text-align: left;'>{sm_title}</h3>", unsafe_allow_html=True)
    col3.markdown(social_media_links, unsafe_allow_html=True)
    st.markdown("<br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)


def custom_footer():
    st.markdown("---")
    footer_html = """
    <style>
    body {
         /* Ensure the body is relatively positioned */
        margin-bottom: 0px; /* Adjust this value to match the desired footer height */
    }
    .footer-container {
        position: absolute;
        bottom: 0;
        width: 100%;
        margin-bottom: 10px; /* Adjust this value to move the footer up */
        background-color: #f9f9f9;
        color: #6c757d;
        font-family: 'Arial', sans-serif;
        padding: 20px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        border-bottom: 1px solid #d3d3d3;
    }

    .footer-main-content {
        display: flex;
        align-items: center;
        gap: 10px; /* Maintain a small gap between items */
    }

    .footer-logo {
        font-weight: bold;
        color: #007bff; /* Brand color for the logo */
        font-size: 14px; /* Increase font size for the logo */
    }

    .footer-link {
        color: #007bff;
        text-decoration: none;
        transition: color 0.2s ease-in-out;
    }

    .footer-link:hover {
        text-decoration: underline;
        color: #0056b3; /* A shade darker on hover for contrast */
    }

    .footer-link.active {
        color: #0056b3; /* Highlight color for active link */
    }

    .footer-instruction {
    padding: 5px 10px;
    background: linear-gradient(135deg, #e9ecef, #cfd9e1);
    color: #495057;
    font-size: 12px;
    margin: 0;
    border: 1px solid #cfd9e1;
    border-radius: 5px;
    text-align: center;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    line-height: 1.5;
    font-weight: bold;
    display: inline-block; /* Make it inline-block */
    width: auto; /* Let it adjust to the content width */
}

    /* Responsive adjustments for smaller screens */
    @media (max-width: 576px) {
        .footer-container {
            flex-direction: column; /* Stack elements vertically */
            gap: 1px; /* Space between stacked elements */
        }

        .footer-main-content {
            flex-direction: column;
            align-items: center;
        }

        .footer-instruction {
            order: 1; /* Instruction part comes first */
            width: 100%; /* Full width for visibility */
            margin: 8px 0; /* Increased margin for visual separation */
        }

        .footer-logo, .footer-link {
            font-size: 11px; /* Slightly smaller font size on mobile */
        }
    }
</style>

<div style = "margin-bottom: 0; margin-top:0;"class="footer-container">
    <div class="footer-main-content">
        <div class="footer-logo">AlgoAnalytics</div>
        <a href="https://www.algoanalytics.com/about" target="_blank" class="footer-link">About</a>
        <a href="https://www.algoanalytics.com/services" target="_blank" class="footer-link">Services</a>
        <a href="https://www.algoanalytics.com/contact" target="_blank" class="footer-link active">Contact</a>
    </div>
    <div class="footer-instruction">
        For the best experience, use a desktop browser
    </div>
    <div>
        &copy; 2023 AlgoAnalytics. All rights reserved.
    </div>
</div>
"""

    st.markdown(footer_html, unsafe_allow_html=True)