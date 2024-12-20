import streamlit as st
import yaml
import streamlit as st
import re
import time
import random
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator import Hasher
from managers.session_manager import SessionManager
from managers.data_manager import DataManager


# *********** Config ***********
# * page layout
if "page_config_set" not in st.session_state:
    st.set_page_config(page_title='Demand Foresight Tools', page_icon=":tada:", layout="wide")
    st.session_state["page_config_set"] = True

# * user authentication data
if "config" not in st.session_state:
    with open("users.yaml") as file:
        st.session_state.config = yaml.load(file, Loader=SafeLoader)

# * configure the start-date, end-date, and theme picture path for year month in 2024
#  {'2024 MONTH': [START_DATE, END_DATE, PIC_PATH]}
st.session_state["ym_mapping"] = {
    '2024 January': ["2024-01-01", "2024-01-31", 1],
    '2024 February': ["2024-02-01", "2024-02-29", 2],
    '2024 March': ["2024-03-01", "2024-03-31", 3],
    '2024 April': ["2024-04-01", "2024-04-30", 1],
    '2024 May': ["2024-05-01", "2024-05-31", 2],
    '2024 June': ["2024-06-01", "2024-06-30", 3],
    '2024 July': ["2024-07-01", "2024-07-31", 1],
    '2024 August': ["2024-08-01", "2024-08-31", 2],
    '2024 September': ["2024-09-01", "2024-10-01", 3],
    '2024 October': ["2024-10-01", "2024-10-31", 1],
    '2024 November': ["2024-11-01", "2024-11-27", 2]
 }




# *** function that would be called after login (entry point of the app) ***
def main():

    st.title("WELCOME")
    

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
    </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------
    # *** navigation bar by st.page_link()
    st.session_state['logged_in'] = True

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
    
    # ----------------------------------------------------------------------------
    # *** STEEP Report GALLERY

    # * User choose the year month *
    ym = st.selectbox("Choose a month to download the STEEP reports", st.session_state['ym_mapping'].keys())

    # * Function for loading STEEP +B report dynamically *
    @st.cache_data                          # * cache the data to reduce data transmission burden
    def load_steep_download_pics(ym, pic_id):

        # * define six blocks (STEEP +B respectively)
        cols = [col for group in (st.columns(3), st.columns(3))for col in group]

        # * for each topic, get the powerpoint from III database, and the theme picture in /pic folder, then render it like a gallery
        for col, topic in zip(cols, ["social", "technological", "economic", "environmental", "political", "business_and_investment"]):
            with col:
                try:
                    # * fetch pptx based on start_date, end_date for corresponding month
                    link_html_obj = DataManager.get_output_download_link(st.session_state["ym_mapping"][ym][0],
                                                                        st.session_state["ym_mapping"][ym][1], 
                                                                        topic, 
                                                                        'pptx', 
                                                                        'steep')
                    
                    # * extract pptx base64 string
                    pptx_base64 = re.search('href = "(.+)" download', link_html_obj).group(1)

                    # * encode theme picture into base64 string
                    image_base64 = DataManager.image_to_b64(f"./pics/{topic}/{pic_id}.png")

                    # * specify the filename (user will see this filename when they download)
                    file_name = f"{ym}-{topic}"

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
    
    # * ym = ym: the year-month requested by users
    # * pic_id = st.session_state['ym_mapping'][ym][2]: 為了要讓每個月的照片不同，動態讀取 session_state 中的 pic path（本來用 randint 但這方法會讓 st.cache_data 失效）
    load_steep_download_pics(ym = ym, pic_id = st.session_state['ym_mapping'][ym][2])

    

# ------------------------------------------------------------------------------------------------------
# *** Authentication & Call the main function ***

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


