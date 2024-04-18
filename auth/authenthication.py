import streamlit_authenticator as stauth
import pickle

from utils.load import load_auth_config

def setup_authenticator():
    
    config = load_auth_config('auth_config.yaml')
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )
    
    return authenticator
    
    