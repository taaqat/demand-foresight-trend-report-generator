import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator import Hasher
import requests
import yaml
from managers.data_manager import DataManager
from managers.session_manager import SessionManager
from yaml.loader import SafeLoader

# * page layout
if "page_config_set" not in st.session_state:
    st.set_page_config(page_title='Demand Foresight Tools', page_icon=":material/home:", layout="wide")
    st.session_state["page_config_set"] = True

st.title("DEMO")


# ****************************************** SIDE BAR CONFIGURATION ******************************************
# * III Icon 和開發團隊
with st.sidebar:
        icon_box, text_box = st.columns((0.2, 0.8))
        with icon_box:
            st.markdown(f'''
                            <img class="image" src="data:image/jpeg;base64,{DataManager.image_to_b64(f"./pics/iii_icon.png")}" alt="III Icon" style="width:500px;">
                        ''', unsafe_allow_html = True)
        with text_box:
            st.markdown("""
            <style>
                .powered-by {text-align:right;
                            font-size: 14px;
                            color: grey;}
            </style>
            <p class = powered-by> Powered by 資策會數轉院 <br/>跨域實證服務中心 創新孵化組</p>""", unsafe_allow_html = True)

st.sidebar.header("資策會 Demand Foresight Tools")
with st.sidebar:
    st.page_link('index.py', label = 'STEEP +B Gallery', icon = ':material/add_circle:')

if st.secrets['permission']['trend_report_generator'] == True:
    st.sidebar.write("**趨勢報告產生器**")
    with st.sidebar:
        st.page_link('pages/page_demo.py', label = 'DEMO Videos', icon = ':material/add_circle:')
        st.page_link('pages/page_steep.py', label = 'STEEP +B 月報', icon = ':material/add_circle:')
        st.page_link('pages/page_self_select.py', label = '自選主題', icon = ':material/add_circle:')
        st.page_link('pages/page_archive.py', label = 'ARCHIVE', icon = ':material/add_circle:')

if st.secrets['permission']['theme_based_generator'] == True:
    st.sidebar.write("**主題式趨勢報告**")
    with st.sidebar:
        st.sidebar.page_link("https://demand-foresight-theme-based-report-generator-7d32y4wrfnhpobtb.streamlit.app/", label = "主題式報告產生器", icon = ':material/link:')


if st.secrets['permission']['chat_tool'] == True:
    st.sidebar.write("**跨文件檢索工具**")
    with st.sidebar:
        st.sidebar.page_link("https://demand-foresight-citation-energy.streamlit.app/", label = "與文件對話", icon = ':material/link:')

# if st.secrets['permission']['visualization'] == True:
    #      st.sidebar.write("**視覺化界面**")
    #     st.sidebar.page_link("[小賴做的視覺化界面]", label = "", icon = ':material/add_circle:')

with st.sidebar:
    SessionManager.fetch_IP()

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
# ***********************************************************************************************




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