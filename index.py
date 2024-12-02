import streamlit as st
import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator import Hasher
from managers.session_manager import SessionManager

# *********** Config ***********
st.set_page_config(page_title='III Trend Report Generator', page_icon=":tada:", layout="wide")
if "config" not in st.session_state:
    with open("users.yaml") as file:
        st.session_state.config = yaml.load(file, Loader=SafeLoader)


# *** entry point after login ***
def main():
    st.session_state['logged_in'] = True
    pg = st.navigation(pages = {
        'STEEP +B 趨勢報告': [
            st.Page('page_steep.py', title = 'STEEP +B Report Generator', icon = ':material/add_circle:') 
        ],
        '自選主題趨勢報告': [
            st.Page('page_self_select.py', title = 'SELF SELECT Report Generator', icon = ':material/add_circle:')
        ],
        'ARCHIVE': [
            st.Page('page_archive.py', title = '歷史紀錄查詢（下載典藏檔）', icon = ':material/bookmarks:')
        ]})
        

    pg.run()



    
# *** Authentization ***

authenticator = stauth.Authenticate(
    st.session_state.config['credentials'],
    st.session_state.config['cookie']['name'],
    st.session_state.config['cookie']['key'],
    st.session_state.config['cookie']['expiry_days'],
)
try:
    l, m, r = st.columns((1/4, 1/2, 1/4))
    with m:
        placeholder = st.container()
    with placeholder:
        authenticator.login('main')
except Exception as e:
    st.error(e)

if st.session_state.authentication_status:
    st.session_state.authenticator = authenticator
    main()
    with st.sidebar:
        authenticator.logout()
elif st.session_state.authentication_status is False:
    st.error('使用者名稱/密碼不正確')


