import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import json
from io import BytesIO

from managers.data_manager import DataManager
from managers.llm_manager import LlmManager
from managers.sheet_manager import SheetManager
from managers.session_manager import SessionManager
from scripts.summarizer import Summarizor


@st.dialog("輸入基本資料：")
def user_info():
    user = st.text_input("你的暱稱")
    email = st.text_input("電子信箱")

    if st.button("Submit"):
        if user == None:
            st.warning("暱稱請勿留空")
        if email == None:
            st.warning("電子信箱請勿留空")
        if (not user == None) & (not email == None):
            st.session_state["user"] = user
            st.session_state["email"] = email
            st.session_state["user_recorded"] = True
            st.rerun()

# * --- Config
if ("set_page_config" not in st.session_state):
    st.session_state['set_page_config'] = True
    st.set_page_config(page_title='III Trend Report Generator', page_icon=":tada:", layout="wide")

st.title("新聞摘要產生器")
st.markdown("""<style>
    div.stButton > button {
        width: 100%;  /* 設置按鈕寬度為頁面寬度的 50% */
        height: 50px;
        margin-left: 0;
        margin-right: auto;
    }
    </style>
    """, unsafe_allow_html=True)

if "summarization_status" not in st.session_state:
    st.session_state["summarization_status"] = "not_started"

if "summary_done" not in st.session_state:
    st.session_state["summary_done"] = False

if "model_type" not in st.session_state:
    st.session_state["model_type"] = ""

def summary_done_switch():
    st.session_state["summary_done"] = True

if "news_to_be_summarized" not in st.session_state:
    st.session_state["news_to_be_summarized"] = pd.DataFrame()
# ------------------------------------------------------------------------------------------------------
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

with st.sidebar:
    @st.dialog("進階設定")
    def developer_option():
        if st.button("清除所有暫存"):
            st.cache_data.clear()
            for var in st.session_state.keys():
                if var not in ['authentication_status', 'authenticator', 'logout', 'init', 'config']:
                    del st.session_state[var]

            SessionManager.session_state_clear('steep')
            SessionManager.session_state_clear('self-select')

        if st.button("顯示所有暫存"):
            SessionManager.show_sessions()

        # *** Model Reset Button
        if st.button("重置模型設定"):
            for session in [
                "KEY_verified",
                "CLAUDE_KEY",
                "OPENAI_KEY",
                "model",
                "model_type"
            ]:
                del st.session_state[session]
            st.rerun()

    if st.button("進階設定"):
        developer_option()



# * 新聞資料上傳的表單
@st.dialog("上傳新聞資料")
def FORM_news_data_upload():
    uploaded = st.file_uploader("上傳新聞資料", key = 'news')
    raw = DataManager.summarizer_load_news(uploaded)                 
    with st.expander("預覽你上傳的資料"):
        st.dataframe(raw)

    # *** Data Column Rename
    try:
        rename_l, rename_m, rename_r= st.columns(3)
        with rename_l:
            id_col = st.selectbox("ID", raw.columns)
        with rename_m:
            title_col = st.selectbox("Title", raw.columns)
        with rename_r:
            content_col = st.selectbox("Content", raw.columns)
        st.caption(":blue[選擇要作為 id, title, content 的欄位後，點選**確認**]")
    except:
        st.info('請上傳"csv" 或 "xlsx" 格式，並且具有明確表頭的資料')

    if st.button("確認"):
        try:
            if pd.DataFrame(raw).empty:
                st.warning("請上傳新聞資料")
            else:
                raw_renamed = raw.rename(
                    columns = {
                        id_col: "id",
                        title_col: "title",
                        content_col: "content"
                    }
                )
                raw_renamed = raw_renamed[['id', 'title', 'content']]
                st.session_state["news_to_be_summarized"] = raw_renamed
            st.rerun()
        except ValueError:
            st.warning("請重新選擇欄位")
        except KeyError:
            st.warning("請重新選擇欄位")
        

# *****************************************  
# ***************** Main ******************
st.session_state['news_upload_button_label'] = {"uploaded": "重新上傳", "empty": "點擊上傳欲生成摘要的新聞資料"}
if 'lang' not in st.session_state:
    st.session_state['lang'] = '繁體中文'

if 'len_per_summary' not in st.session_state:
    st.session_state['len_per_summary'] = 30

st.session_state['news_uploaded'] = 'empty'
if not st.session_state['news_to_be_summarized'].empty:
    st.session_state['news_uploaded'] = 'uploaded'

def main():
    COL_LEFT, COL_RIGHT = st.columns(2)
    with COL_RIGHT:
        BOX_preview = st.empty()
        
    with COL_LEFT:
    
        BOX_stage_button = st.empty()
        
        if st.session_state['summarization_status'] == 'not_started':
            with BOX_preview.container():
                st.markdown('<h4>預覽新聞資料</h4>', unsafe_allow_html = True)
                st.dataframe(st.session_state["news_to_be_summarized"], width = 1000)

            with BOX_stage_button.container():
                if st.button(st.session_state['news_upload_button_label'][st.session_state['news_uploaded']]):
                    FORM_news_data_upload()

                c1, c2 = st.columns(2)
                with c1:
                    st.session_state['lang'] = st.selectbox("請選擇欲產生摘要的語言", ["繁體中文", "英文", "日文"])
                with c2:
                    st.session_state['len_per_summary'] = st.slider("請選擇每篇新聞摘要的理想**長度**", 30, 300, step = 5)

                sheet_url = st.text_input("請輸入可編輯之 Google Sheet 連結（Optional）")
                
                if st.button("確認送出，開始摘要", type = "primary"):
                    try:
                        SheetManager.SummaryGSDB.fetch(SheetManager.SummaryGSDB.authenticate_google_sheets(json.loads(st.secrets['gsheet-credits']['credits'])), sheet_url)
                    except Exception as e:
                        st.error(f"Error happened while connecting to the google sheet: **{e}**")
                        st.stop()
                    st.session_state['summarized_data'] = pd.DataFrame()
                    st.session_state['sheet_url'] = sheet_url
                    if not st.session_state["news_to_be_summarized"].empty:
                        BOX_stage_button.empty()
                        st.session_state['summarization_status'] = 'started'
                        st.rerun()
                    else:
                        st.warning("請上傳欲摘要的新聞資料")
                
        

        if st.session_state['summarization_status'] == 'started':
            with COL_RIGHT:
                st.markdown('<h4>新聞摘要結果</h4>', unsafe_allow_html = True)
                BOX_output = st.empty()

            with BOX_stage_button.container():
                
                if st.button("上一步"):
                    BOX_stage_button.empty()
                    st.session_state['summarization_status'] = 'not_started'
                    st.session_state['summary_done'] = False
                    st.rerun()

                if st.session_state['summary_done'] == False:
                    # * Initialize google sheet client
                    if 'sheet_url' in st.session_state:
                        sheet_client = SheetManager.SummaryGSDB.authenticate_google_sheets(json.loads(st.secrets['gsheet-credits']['credits']))
                        Summarizor.summarize(st.session_state["news_to_be_summarized"], BOX_output, sheet_client)
                    else:
                        Summarizor.summarize(st.session_state["news_to_be_summarized"], BOX_output)

                    
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine = "xlsxwriter") as writer:
                        st.session_state['summarized_data'].to_excel(writer, index = False)
                    buffer.seek(0)

                    st.download_button(
                        label = "下載完成檔案",
                        data = buffer,
                        file_name = "summary.xlsx",
                        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        on_click = summary_done_switch)
                    
                
                    
                elif st.session_state['summary_done'] == True:
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine = "xlsxwriter") as writer:
                        st.session_state["news_to_be_summarized"].to_excel(writer, index = False)
                    buffer.seek(0)

                    st.download_button(
                        label = "下載完成檔案",
                        data = buffer,
                        file_name = "summary.xlsx",
                        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        on_click = summary_done_switch)
                    

    if st.session_state['summarization_status'] == 'started':
        with BOX_output.container(height = 250):
            st.dataframe(st.session_state['summarized_data'], width = 1000)



# *** 模型選擇 
if st.session_state['model_type'] == "":
    st.info("**請先選擇欲使用的語言模型**")
    if st.button("點擊開啟選單"):
        LlmManager.model_selection()

# ** user_token switch: if the user is required to input their own token
if st.secrets['permission']['user_token'] == True:
    # ** Ensure that the model type is selected
    if st.session_state['model_type'] == "":
        st.stop()

    # ** Verify API key
    if st.session_state['KEY_verified'] == False:
        try:
            st.info("**請設定 API key**")
            if st.button("點擊設定 API key"):
                LlmManager.customize_token(st.session_state['model_type'])
        except:
            pass
    else:
        if st.session_state['model']:
            main()
            
        else:
            st.stop()

else:
    st.session_state['CLAUDE_KEY'] = st.secrets['CLAUDE_KEY']
    st.session_state['OPENAI_KEY'] = st.secrets['OPENAI_KEY']
    st.session_state['model'] = LlmManager.init_model()
    if st.session_state['model']:
        main()
        
    else:
        st.stop()