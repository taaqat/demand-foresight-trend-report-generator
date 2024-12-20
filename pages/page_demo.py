import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator import Hasher
import yaml
from yaml.loader import SafeLoader

st.title("DEMO")


# *** SIDE BAR CONFIGURATION
st.sidebar.header("資策會 Demand Foresight Tools")
with st.sidebar:
    st.page_link('index.py', label = 'Home Page', icon = ':material/add_circle:')

st.sidebar.write("**趨勢報告產生器**")
with st.sidebar:
    st.page_link('pages/page_demo.py', label = 'DEMO Videos', icon = ':material/add_circle:')
    st.page_link('pages/page_steep.py', label = 'STEEP +B 月報', icon = ':material/add_circle:')
    st.page_link('pages/page_self_select.py', label = '自選主題', icon = ':material/add_circle:')
    st.page_link('pages/page_archive.py', label = 'ARCHIVE', icon = ':material/add_circle:')


st.sidebar.write("**對話式工具**")
st.sidebar.page_link("https://livinglab-demand-foresight-chat.streamlit.app/", label = "RAG 與文件對話", icon = ':material/link:')

st.sidebar.write("**視覺化界面**")
# st.sidebar.page_link("[小賴做的視覺化界面]", label = "", icon = ':material/add_circle:')

# *** CSS style setting
st.markdown("""<style>
div[data-baseweb="select"]:hover {
    border-color: #baad8d;
}
div.stButton > button {
    width: 100%;  /* 設置按鈕寬度為頁面寬度的 50% */
    height: 50px;
    margin-left: 0;
    margin-right: auto;
}
div.stButton > button:hover {
    transform: scale(1.02);
    transition: transform 0.05s;
}
div[data-testid="stTextAreaRootElement"]:hover {
    border-color: #baad8d
}
div[data-baseweb="input"]:hover {
    border-color: #baad8d;
}
</style>
""", unsafe_allow_html=True)




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