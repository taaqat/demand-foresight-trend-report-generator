import streamlit as st

# *** Import utilities
from managers.data_manager import DataManager
from managers.export_manager import ExportManager
from managers.llm_manager import LlmManager
from managers.prompt_manager import PromptManager
from managers.session_manager import SessionManager

from scripts.self_select_executor import Executor
import datetime as dt
import pandas as pd
import requests

# * page layout
if "page_config_set" not in st.session_state:
    st.set_page_config(page_title='Demand Foresight Tools', page_icon=":material/home:", layout="wide")
    st.session_state["page_config_set"] = True

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
    st.page_link('index.py', label = 'STEEP 月報', icon = ':material/add_circle:')

if st.secrets['permission']['trend_report_generator'] == True:
    st.sidebar.write("**趨勢報告產生器**")
    with st.sidebar:
        st.page_link('pages/page_demo.py', label = 'DEMO Videos', icon = ':material/add_circle:')
        st.page_link('pages/page_steep.py', label = 'STEEP 月報產生器', icon = ':material/add_circle:')
        st.page_link('pages/page_self_select.py', label = '特定主題報告產生器', icon = ':material/add_circle:')
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
# ***********************************************************************************************************

# ********* config **********
st.title("自選主題")
if 'self_select_params' not in st.session_state:
    st.session_state['self_select_params'] = {}

if 'stage' not in st.session_state:
    st.session_state['stage'] = 'step1'

if 'self_select_raw_data' not in st.session_state:
    st.session_state['self_select_raw_data'] = pd.DataFrame()

if 'CLAUDE_KEY' not in st.session_state:
    st.session_state['CLAUDE_KEY'] = " "

if 'OPENAI_KEY' not in st.session_state:
    st.session_state['OPENAI_KEY'] = ""

if 'KEY_verified' not in st.session_state:
    st.session_state['KEY_verified'] = False

if "model_type" not in st.session_state:
    st.session_state['model_type'] = ""

# *** 模型選擇
if st.session_state['model_type'] == "":
    st.info("**請先選擇欲使用的語言模型**")
    if st.button("點擊開啟選單"):
        LlmManager.model_selection()



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
    
    
def main():

    # ********* Basic info input *********
    with st.container(key = 'basic_info'):
        st.subheader("基本資料輸入")
        box1_left,box1_mid, box1_right = st.columns((1/3, 1/3, 1/3))
        with box1_left:
            project_name = st.text_input("Name this project with a concise name 👇")
        with box1_mid:
            user_name = st.text_input("你的暱稱")
        with box1_right:
            user_email = st.text_input("電子郵件地址")
            



    # ***  column: user input; right column: progress and results
    left_col, right_col = st.columns((1/2, 1/2))
    with left_col:
        step1_box = st.empty()
        step2_box = st.empty()

    with right_col:
        step1_result = st.empty()
        step2_console = st.empty()
        step2_output = st.empty()

        

    # ******** Step 1: Filter News *********
    def s1_filter_news():

        st.subheader("Step1: 篩選新聞來源")
        st.code("""根據您的專案需求，從資料庫中透過關鍵字搜尋出您需要的新聞。
    您可以在這一步中先確認新聞數量與內容是否符合您的需求，再決定是否進行後續的趨勢推論。
                """)

        # *** Date input ***
        st.markdown("<h5>請選擇新聞來源之時間範圍</h5>", unsafe_allow_html = True)
        col1, col2 = st.columns((1/2, 1/2))
        with col1:
            try:
                start_input = st.date_input('Starting Date', st.session_state['self_select_params']['start_date'])
            except:
                start_input = st.date_input('Starting Date')

        with col2:
            try:
                end_input = st.date_input('Ending Date', st.session_state['self_select_params']['end_date'])
            except:
                end_input = st.date_input('Ending Date')

        # *** Keywords input ***
        block1, block2 = st.columns((1/2, 1/2))
        with block1:
            try:
                keywords_input = st.text_area("Please input some keywords", st.session_state['self_select_params']['keywords'], height = 100)
            except:
                keywords_input = st.text_area("Please input some keywords", height = 100)
            search_scope = st.multiselect("Search scope (Multiple Choice)", ['title', 'content'])
        with block2:
            st.text_area("Example", height = 100, value = """Ex: 想要查詢包含「AI」和「美國」或是包含「科技股」的新聞：\nAI AND 美國\n科技股""", disabled = True)
            developers = st.multiselect("Please choose developer options if needed", 
                                    ["Show debugging messeges", "Show returned news titles"])
        debug, show_titles = False, False
        if "Show debugging messeges" in developers:
            debug = True
        if "Show returned news titles" in developers:
            show_titles = True

        
        
        # *** check if the project has already been created
        existing_projects = SessionManager.self_select_database('fetch')
        if '_'.join([project_name, str(start_input), str(end_input)]) in existing_projects['primary_key'].tolist():
            st.warning("該專案名稱與日期之組合已經存在於資料庫中（可以於 Archive 頁面查詢）。若要重新製作，會覆蓋掉舊的資料。若仍要執行請繼續。", icon = '⚠️')
                

        # *** Flow control based on session state
        query = st.button("Query", key = 'query')
        # * 1. Querying data from database with keywords input & update the fetched data to st.session_state
        if query:
            if not user_name:
                st.warning("請輸入您的暱稱")
                st.stop()
            if not user_email:
                st.warning("請輸入您的 email")
                st.stop()
            if not keywords_input:
                st.warning("請輸入至少一個關鍵字")
                st.stop()
            if not search_scope:
                st.warning("請至少選擇一個搜尋範圍")
                st.stop()
            if not start_input <= dt.date.today():
                st.warning("開始日期不得晚於今日")
                st.stop()
            if not end_input <= dt.date.today():
                st.warning("結束日期不得晚於今日")
                st.stop()
            if not start_input < end_input:
                st.warning("開始日期須早於結束日期")
                st.stop()
            if (keywords_input != "") & (search_scope != []):
                try:
                    with st.status("Processing"):
                        data = DataManager.fetch(start_date = start_input, end_date = end_input, output_format = 'fulltext',
                            keywords = keywords_input, search_scope = ",".join(search_scope), debug = debug, show_titles = show_titles)
                    st.session_state['self_select_raw_data'] = data.reset_index()
                    st.info(f'There are {len(data)} news related with the keywords that you type in')
                    # st.session_state['stage'] = 'step1'
                    
                except:
                    st.warning("No matched news found")


        # * 2. update parameters to st.session_state
        st.session_state['self_select_params'].update(
            {'keywords': keywords_input,
            'start_date': start_input,
            'end_date': end_input}
        )

        # * 3. staging with undo button
        placeholder = st.empty()
        proceed, undo = False, False
        with placeholder.container():
            if not st.session_state['self_select_raw_data'].empty:
                l, r = st.columns((0.8, 0.2))
                with l:
                    proceed = st.button("Proceed", type = "primary", key = 'proceed')
                with r:
                    undo = st.button("Undo", key = 'Undo')
        if undo:          
            st.session_state['self_select_raw_data'] = pd.DataFrame()
            placeholder.empty()
            step1_result.empty()

        if proceed:
            st.session_state['stage'] = 'step2'
            step1_box.empty()
            


    # ******** Step 2: Customization and Generate *********
    def s2_customization():

        # *** User input (step2_box)
        with step2_box.container():
            # *** connect step 1 and step 2
            keywords = st.session_state['self_select_params']['keywords']
            start_date = st.session_state['self_select_params']['start_date']
            end_date = st.session_state['self_select_params']['end_date']


            st.subheader("Step2. 客製化調整與執行")

            st.subheader("請選擇輸出格式")
            output_format = st.multiselect("You can choose multiple output formats", ["總結過後的新聞摘要（EXCEL；無趨勢報告）",
                                                                        "選取主題之趨勢報告（PPT；單一主題）",
                                                                        "選取主題之趨勢報告（EXCEL；所有主題）"])
            output_format_mapping = {
                "選取主題之趨勢報告（EXCEL；所有主題）": False,
                "選取主題之趨勢報告（PPT；單一主題）": False,
                "總結過後的新聞摘要（EXCEL；無趨勢報告）": False
            }

            for _format_ in output_format:
                output_format_mapping[_format_] = True

            summary_output = output_format_mapping["總結過後的新聞摘要（EXCEL；無趨勢報告）"]        
            ppt = output_format_mapping["選取主題之趨勢報告（PPT；單一主題）"]      
            excel = output_format_mapping["選取主題之趨勢報告（EXCEL；所有主題）"] 

            
            # *** User Flexible Output Format Selection ***
            st.subheader("其他調整")
            cols = st.multiselect("Choose all sections that you need for the inference (default: all)",
                                    ["<f>未來產品或服務機會點", "<g>關鍵驅動因素", "<h>微弱信號", "<i>時間尺度", "<j>趨勢總結洞察"],
                                    default = ["<f>未來產品或服務機會點", "<g>關鍵驅動因素", "<h>微弱信號", "<i>時間尺度", "<j>趨勢總結洞察"])
            color_block, additional_prompt_block = st.columns((0.2, 0.8))
            with color_block:
                color = st.color_picker("Pick a color", "#A69151")
            with additional_prompt_block:
                additional = st.text_area("Please input additional prompt if needed.")

            
            # *** staging with goback button (if clicked, go back to step 1)
            placeholder = st.empty()
            with placeholder.container():
                l, r = st.columns((0.8, 0.2))
                with l:
                    submission = st.button("Submit", type = 'primary', key = 'submit')
                with r:
                    goback = st.button("Undo", key = 'back_to_step1')
            if goback:       
                st.session_state['stage'] = 'step1'
                try:
                    SessionManager.session_state_clear('self-select')
                except:
                    pass
                st.rerun()
        
        # *** submission -> run and render ***
        if submission:
            
            # Check if the input is valid
            
            if ([summary_output, ppt, excel] == [False, False, False]):
                st.warning('請選擇至少一種輸出格式')

            else: 
                # ******************************** Console Box *************************************
                with step2_console.container(border = True):
                    st.markdown("<h5>進度報告</h5>", unsafe_allow_html = True)
                    try:
                        raw_data = st.session_state['self_select_raw_data']

                        with st.spinner("Processing..."):
                            # *** main function for inference and generating trend report ***
                            Executor.self_select_run(
                                user_name, user_email, project_name, keywords, start_date, end_date, raw_data, cols, additional, 
                                None, excel, ppt, color
                            )

                    except:
                        SessionManager.send_notification_email(user_name, user_email, type = 'failed')
                        raise NotImplementedError("Something went wrong... Please trace back to debug.")
                    

                # ******************************** Output Box *************************************
                # *** check the output format, read from cache folders, and generate download link ***
                with step2_output.container(border = True):
                    st.markdown("<h5>成果下載連結</h5>", unsafe_allow_html = True)
                    if ppt:

                        st.success("Ppt slides created! You can download now💥")
                        st.markdown(DataManager.get_output_download_link(start_date, end_date, project_name, 'pptx', 'self_select'), unsafe_allow_html = True)

                    if excel:
                        
                        st.success("Excel file created! You can download now💥")
                        st.markdown(DataManager.get_output_download_link(start_date, end_date, project_name, 'xlsx', 'self_select'), unsafe_allow_html = True)

                    if summary_output:
                        st.success("Here is the daily summary for the period you requested💥")
                        st.markdown(DataManager.get_summary_download_link(start_date, end_date, project_name), unsafe_allow_html = True)

                st.success("Completed!")
        


    # ******* Execute UI functions *******
    if st.session_state['stage'] == 'step1':
        with step1_box.container():
            s1_filter_news()

        with step1_result.container(border = False):
            st.markdown("<h5>查詢結果</h5>", unsafe_allow_html = True)
            st.write(st.session_state['self_select_raw_data'])

    if st.session_state['stage'] == 'step2':
        with step2_box.container():
            step1_result.empty()
            s2_customization()
        with step2_console.container():
            pass





# ** user_token switch: if the user is required to input their own api token
if st.secrets['permission']['user_token'] == True:
    # ** Ensure that the model type is selected
    if st.session_state['model_type'] == "":
        st.stop()

    # ** Verify API token
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