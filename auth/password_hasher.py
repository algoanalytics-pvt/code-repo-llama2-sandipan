import streamlit_authenticator as stauth

#create haspassords 
algouser_password = "XXX" # -> 
algodev_password = "XXX" # -> 

hashed_passwords = stauth.Hasher([algouser_password, algodev_password]).generate()
print(hashed_passwords)

 