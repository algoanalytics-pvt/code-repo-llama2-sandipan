import streamlit as st
from PIL import Image
import json
from streamlit_lottie import st_lottie



def create_featurecard(text,background_color='#FFFFF',font_size='20px'):
    st.markdown(
            f"""
            <div style='background-color: {background_color}; 
            padding: 20px; 
            border-radius: 
            0px; 
            width: 100%;
            height: 300px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            '>
            
            <span style='color: black;
            text-align: center;font-size: {font_size};
            color: #635F5F;
            '>{text}</span>
            </div>
            """,
            unsafe_allow_html=True
            )
    
   
def create_specific_feature(text_heading, description,image_path, heading_font_size='30px',description_font_size ='18px',image_present=True,image_right_side=True,lottie_image=True):
    
        
        with st.container():
            #first_section, second_section = st.columns((2,1))
            
            if image_right_side==True:
                #content_section = first_section
                #image_section=second_section 
                content_section, image_section = st.columns((2,1))
                             
            else:
                #content_section = second_section
                #image_section=first_section
                image_section, content_section = st.columns((1,2))
                
                
                
                
            
            with content_section:
                background_color = 'white'
                
                
                #text = 'Stay Informed with Curated Daily News'
                #description = 'Stay updated with the latest developments in the stock market effortlessly. Our app curates news related to the stocks you care about on a daily basis. We understand that staying informed is crucial for making well-informed investment decisions.'
                st.markdown(
                f"""
                <div style='background-color: {background_color}; 
                padding: 20px; 
                border-radius: 
                0px; 
                width: 100%;
                height: 300px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: start;
                '>
                
                <span style='color: black;
                text-align: start;font-size: {heading_font_size};
                color: #799BE6;/*#635F5F*/
                '>{text_heading}</span>
                <br>
                <br>
                <span style='color: black;
                text-align: start;font-size:{description_font_size};
                color: #635F5F;
                '>{description}</span>
                
                </div>
                
                
                """,
                unsafe_allow_html=True
                )
                
            with image_section:
                if image_present:
                    if lottie_image:
                        lottie_img = load_lottiefile(image_path)
                        st_lottie(lottie_img,height=300,speed=0.5)
                    else:
                        news_image = Image.open(image_path)
                        st.image(news_image)

@st.cache_resource 
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)