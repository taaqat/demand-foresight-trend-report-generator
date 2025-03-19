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
# * Sidebar Setting
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

    st.header("資策會 Demand Foresight Tools")
    st.page_link('index.py', label = 'STEEP 月報', icon = ':material/add_circle:')

    if st.secrets['permission']['trend_report_generator'] == True:
        st.write("**趨勢報告產生器**")

        st.page_link('pages/page_demo.py', label = 'DEMO Videos', icon = ':material/add_circle:')
        st.page_link('pages/page_steep.py', label = 'STEEP 月報產生器', icon = ':material/add_circle:')
        st.page_link('pages/page_self_select.py', label = '特定主題報告產生器', icon = ':material/add_circle:')
        st.page_link('pages/page_summarizer.py', label = '新聞摘要產生器', icon = ':material/add_circle:')
        st.page_link('pages/page_archive.py', label = 'ARCHIVE', icon = ':material/add_circle:')


    if st.secrets['permission']['theme_based_generator'] == True:
        st.write("**主題式趨勢報告**")

        st.page_link("https://demand-foresight-theme-based-report-generator-7d32y4wrfnhpobtb.streamlit.app/", label = "主題式報告產生器", icon = ':material/link:')


    if st.secrets['permission']['chat_tool'] == True:
        st.write("**跨文件檢索工具**")
        st.page_link("https://livinglab-demand-foresight-dev.streamlit.app/?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJkZW1hbmQtYXBpIiwiYXVkIjoicmVjZWl2ZXIiLCJqdGkiOiJmMmQyMWIxZjRjZDlkNTUxNzQxYzM2NTNiODFkNTdhYyIsImlhdCI6MTc0MjAyMjI2MywibmJmIjoxNzQyMDIyMjYzLCJleHAiOjE4MzY2OTMwNDAsInVzZXJfaWQiOjg5MjAwNjM3MywidHlwZSI6ImFjY2Vzc190b2tlbiIsInB1YmxpY19rZXkiOiItLS0tLUJFR0lOIFBVQkxJQyBLRVktLS0tLVxyXG5NSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXI1bEZoYXNFOWI0NTYwVzBJQS9wXHJcbkkvZzZmaVphRXJuYVhrc04zaDJJaVpRV3M0NE9WQTAyN2Z1SE1rQmxJZkJSUFdvaXM4citEbEI0b0ZyUURMN1Fcclxua1h3K1FCL0tzT3QzYkI1U1BYN0VqZHRqb2RuRHB5T29GT2V5akFITEtadW9uUFFDd1R1eHRVdFFNcitVRDRMNFxyXG5DNlBsSXViWWlxRW5wL3lMV25NZUU1VVliRkdhNDRxazBTL1JIc0o3QjFJbGJiNzA1QWVGblRFbVVTRFc0bzk2XHJcbnM2L3kwaGlIeGZVSVRYVDJFR3VOcFh5a0JFU2ZtcjZ2T2MxU1IwOWxoT2tQejFhM21XQytlaHAzYnFKdzFzdW1cclxuaEFIY0hDWVdhd1RUeU9RajI5NE9ERDFHR2w0M0h3VFNhZTh5V2JldnM3WVZ5a1VZMG0rU2paYkMxTGdrdGczMVxyXG4rUUlEQVFBQlxyXG4tLS0tLUVORCBQVUJMSUMgS0VZLS0tLS1cclxuIiwidXNlcm5hbWUiOiJ0ZXN0R3Vlc3QifQ.u8ZLNiNQjH2T0sGCJbjJTYtEZtxkq0KojHcjqQGtAYY", label = "與文件對話", icon = ':material/link:')
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