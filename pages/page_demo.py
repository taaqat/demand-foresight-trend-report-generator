import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator import Hasher
import yaml
from yaml.loader import SafeLoader
st.set_page_config(page_title='III Trend Report Generator', page_icon=":tada:", layout="wide")
st.title("DEMO")


# *** SIDE BAR CONFIGURATION
st.sidebar.subheader("趨勢報告產生器")
with st.sidebar:
    st.page_link('pages/page_demo.py', label = 'DEMO Videos', icon = ':material/add_circle:')
    st.page_link('pages/page_steep.py', label = 'STEEP +B', icon = ':material/add_circle:')
    st.page_link('pages/page_self_select.py', label = 'SELF SELECT', icon = ':material/add_circle:')
    st.page_link('pages/page_archive.py', label = 'ARCHIVE', icon = ':material/add_circle:')


st.sidebar.subheader("對話式工具")
st.sidebar.page_link("https://livinglab-demand-foresight-chat.streamlit.app/", label = "RAG chat box", icon = ':material/add_circle:')

st.sidebar.subheader("視覺化界面")





steep, self_select, archive = st.tabs(['STEEP +B', '自選主題', 'ARCHIVE'])

with steep:
    with st.container(border = True):
        st.video("https://www.youtube.com/watch?v=_HAff6tZ9hU")

with self_select:
    with st.container(border = True):
        st.video("https://www.youtube.com/watch?v=VEMfloptbw8")

with archive:
    with st.container(border = True):
        st.video("https://www.youtube.com/watch?v=ibwSk1mbQ1k")