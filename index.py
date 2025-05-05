import streamlit as st
import yaml
import streamlit as st
import re
import requests
import time
import random
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator import Hasher
from managers.session_manager import SessionManager
from managers.data_manager import DataManager
from managers.llm_manager import LlmManager
from managers.constants import *


# *********** Config ***********
# * page layout
if "page_config_set" not in st.session_state:
    st.set_page_config(page_title='Demand Foresight Tools', page_icon=":material/home:", layout="wide")
    st.session_state["page_config_set"] = True

# * user authentication data
if "config" not in st.session_state:
    with open("users.yaml") as file:
        st.session_state.config = yaml.load(file, Loader=SafeLoader)

# * model
if "model_type" not in st.session_state:
    st.session_state['model_type'] = ""

# * configure the start-date, end-date, and theme picture path for year month in 2024
#  {'2024 MONTH': [START_DATE, END_DATE, PIC_PATH]}
st.session_state["ym_mapping"] = ym_mapping


# ***************************************************
# *** Sidebar Configuration
# ---------------------------------------------------
# *** button style setting
st.markdown("""<style>
div.stButton > button {
    width: 100%;  
    height: 50px;
    margin-left: 0;
    margin-right: auto;
}
div.stButton > button:hover {
    transform: scale(1.02);
    transition: transform 0.05s;
}
div.stDownloadButton > button {
    width: 100%;  
    margin-left: 0;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# *** navigation bar by st.page_link()
st.session_state['logged_in'] = True

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
    st.page_link('index.py', label = 'STEEP 月報', icon = ':material/add_circle:')

if st.secrets['permission']['trend_report_generator'] == True:
    st.sidebar.write("**趨勢報告產生器**")
    with st.sidebar:
        st.page_link('pages/page_demo.py', label = 'DEMO Videos', icon = ':material/add_circle:')
        st.page_link('pages/page_steep.py', label = 'STEEP 月報產生器', icon = ':material/add_circle:')
        st.page_link('pages/page_self_select.py', label = '特定主題報告產生器', icon = ':material/add_circle:')
        st.page_link('pages/page_summarizer.py', label = '新聞摘要產生器', icon = ':material/add_circle:')
        st.page_link('pages/page_archive.py', label = 'ARCHIVE', icon = ':material/add_circle:')

if st.secrets['permission']['theme_based_generator'] == True:
    st.sidebar.write("**主題式趨勢報告**")
    with st.sidebar:
        st.sidebar.page_link("https://demand-foresight-theme-based-report-generator-7d32y4wrfnhpobtb.streamlit.app/", label = "主題式報告產生器", icon = ':material/link:')


if st.secrets['permission']['chat_tool'] == True:
    st.sidebar.write("**跨文件檢索工具**")
    with st.sidebar:
        st.sidebar.page_link("https://livinglab-demand-foresight-dev.streamlit.app/?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJkZW1hbmQtYXBpIiwiYXVkIjoicmVjZWl2ZXIiLCJqdGkiOiJmMmQyMWIxZjRjZDlkNTUxNzQxYzM2NTNiODFkNTdhYyIsImlhdCI6MTc0MjAyMjI2MywibmJmIjoxNzQyMDIyMjYzLCJleHAiOjE4MzY2OTMwNDAsInVzZXJfaWQiOjg5MjAwNjM3MywidHlwZSI6ImFjY2Vzc190b2tlbiIsInB1YmxpY19rZXkiOiItLS0tLUJFR0lOIFBVQkxJQyBLRVktLS0tLVxyXG5NSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXI1bEZoYXNFOWI0NTYwVzBJQS9wXHJcbkkvZzZmaVphRXJuYVhrc04zaDJJaVpRV3M0NE9WQTAyN2Z1SE1rQmxJZkJSUFdvaXM4citEbEI0b0ZyUURMN1Fcclxua1h3K1FCL0tzT3QzYkI1U1BYN0VqZHRqb2RuRHB5T29GT2V5akFITEtadW9uUFFDd1R1eHRVdFFNcitVRDRMNFxyXG5DNlBsSXViWWlxRW5wL3lMV25NZUU1VVliRkdhNDRxazBTL1JIc0o3QjFJbGJiNzA1QWVGblRFbVVTRFc0bzk2XHJcbnM2L3kwaGlIeGZVSVRYVDJFR3VOcFh5a0JFU2ZtcjZ2T2MxU1IwOWxoT2tQejFhM21XQytlaHAzYnFKdzFzdW1cclxuaEFIY0hDWVdhd1RUeU9RajI5NE9ERDFHR2w0M0h3VFNhZTh5V2JldnM3WVZ5a1VZMG0rU2paYkMxTGdrdGczMVxyXG4rUUlEQVFBQlxyXG4tLS0tLUVORCBQVUJMSUMgS0VZLS0tLS1cclxuIiwidXNlcm5hbWUiOiJ0ZXN0R3Vlc3QifQ.u8ZLNiNQjH2T0sGCJbjJTYtEZtxkq0KojHcjqQGtAYY", label = "與文件對話", icon = ':material/link:')

# if st.secrets['permission']['visualization'] == True:
#      st.sidebar.write("**視覺化界面**")
#     st.sidebar.page_link("[小賴做的視覺化界面]", label = "", icon = ':material/add_circle:')

with st.sidebar:
    SessionManager.fetch_IP()


# **************************************************************************
# *** function that would be called after login (entry point of the app) ***
def main():

    st.title("STEEP +B 月報")
    st.caption(":gray[2024 年的 STEEP 月報僅提供 pptx 版本的載點。2025 年起的 STEEP 月報，以網頁式簡報呈現，同時也提供 pptx 版本簡報的載點。]")
    
    
    
    # ----------------------------------------------------------------------------
    # *** STEEP Report 
    # * Function for loading STEEP +B monthly report in 2024 *
    @st.cache_data                          # * cache the data to reduce data transmission burden
    def load_steep_2024(month, pic_id):
        """
        # * month = month: the year-month requested by users
        # * pic_id = st.session_state['ym_mapping']['2024'][month][2]: 為了要讓每個月的照片不同，動態讀取 session_state 中的 pic path（本來用 randint 但這方法會讓 st.cache_data 失效）
        """

        # * define six blocks (STEEP +B respectively)
        cols = [col for group in (st.columns(3), st.columns(3))for col in group]

        # * for each topic, get the powerpoint from III database, and the theme picture in /pic folder, then render it like a gallery
        for col, topic in zip(cols, ["social", "technological", "economic", "environmental", "political", "business_and_investment"]):
            with col:
                try:
                    # * fetch pptx based on start_date, end_date for corresponding month
                    link_html_obj = DataManager.get_output_download_link(st.session_state["ym_mapping"]['2024'][month][0],
                                                                        st.session_state["ym_mapping"]['2024'][month][1], 
                                                                        topic, 
                                                                        'pptx', 
                                                                        'steep')
                    
                    # * extract pptx base64 string
                    pptx_base64 = re.search('href = "(.+)" download', link_html_obj).group(1)

                    # * encode theme picture into base64 string
                    image_base64 = DataManager.image_to_b64(f"./pics/{topic}/{pic_id}.png")

                    # * specify the filename (user will see this filename when they download)
                    file_name = f"2024-{month}-{topic}"

                    # * create download link by HTML structure & CSS setting
                    download_link = f"""
                    <style>
                    .hover-container {{
                        position: relative;
                        display: inline-block;
                    }}
                    .hover-container .hover-message {{
                        display: block;
                        visibility: hidden;
                        background-color: rgba(0, 0, 0, 0.65);
                        color: #fff;
                        text-align: center;
                        border-radius: 5px;
                        padding: 5px 10px;
                        position: absolute;
                        bottom: 10%; /* 提示文字出現在圖片上方 */
                        left: 50%;
                        transform: translateX(-50%);
                        opacity: 0;
                        transition: opacity 0.5s bottom 0.8s;
                        font-size: 12px;
                    }}
                    .hover-container:hover .hover-message {{
                        visibility: visible;
                        opacity: 1;
                    }}
                    .image:hover {{
                        opacity: 0.8;
                        filter: saturate(150%);
                        transition: opacity 0.5s, filter 0.5s;
                    }}

                    </style>
                    <div class="hover-container">
                        <a class="img-container" href="{pptx_base64}" download="{file_name}">
                            <img class="image" src="data:image/jpeg;base64,{image_base64}" alt="Download" style="width:500px;">
                        </a>
                        <div class="hover-message">Click to download</div>
                    </div>
                    """
                    
                    # * display it with st.markdown()
                    st.markdown(download_link, unsafe_allow_html = True)

                except Exception as e:
                    # st.write(e)
                    pass
    
    
    
    # * Function for loading STEEP +B monthly report in 2024 *
    def load_steep_2025(topic_selection, month, cl, cr):
        
        period = "-".join(st.session_state['ym_mapping']['2025'][month])
        try:
            filename_html = topic_selection + '_trends_' + period + '_html.txt'
            filename_pptx = topic_selection + '_trends_' + period + '.pptx'

            html_body = DataManager.get_files(filename_html, 'txt')
            pptx_body = DataManager.b64_to_pptx_IO(DataManager.get_files(filename_pptx, 'pptx'))

            with cl:
                download_btn_l = st.download_button(
                    label = "下載 HTML 檔案",
                    data = html_body,
                    file_name = topic_selection + '_trends_' + period + '.html',
                    type="primary",
                    icon=":material/download:",
                    mime="html"
                )
            with cr:
                download_btn_r = st.download_button(
                    label = "下載 Pptx 檔案",
                    data = pptx_body,
                    file_name = topic_selection + "_trends_" + period + '.pptx',
                    icon = ":material/download:",
                    mime = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )

            st.html(html_body)
        except Exception as e:
            st.warning("該主題之月報尚未生成！")
            st.warning(e)

        

    # * User choose the year month *
    # ym = st.selectbox("Choose a month to download the STEEP reports", st.session_state['ym_mapping'].keys())
    def render():
        tabs = st.tabs(list(st.session_state['ym_mapping'].keys())[::-1])

        for tab, ym in zip(tabs, list(st.session_state['ym_mapping'].keys())[::-1]):
            if ym.startswith("2024"):
                with tab:
                    month = st.selectbox("選擇月份", list(st.session_state['ym_mapping']['2024'].keys())[::-1], key = '2024_month')
                    load_steep_2024(month, st.session_state['ym_mapping']['2024'][month][2])
                    
            elif ym.startswith("2025"):
                with tab:
                    cl2025, cr2025 = st.columns(2)
                    with cl2025:
                        topic_selection = st.selectbox("選擇主題", ['social', 'economic', 'environmental', 'technological', 'political', 'business_and_investment'], key = '2025_topic')
                    with cr2025:
                        month = st.selectbox("選擇月份", st.session_state['ym_mapping']['2025'].keys(), key = '2025_month')
                    load_steep_2025(topic_selection, month, cl2025, cr2025)

    render()
    

    
    
    

    

# ------------------------------------------------------------------------------------------------------
# *** Authentication & Call the main function ***
            
if st.secrets['permission']['authenticate'] == True:

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

else:
    main()
    

