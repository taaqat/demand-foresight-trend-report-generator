import streamlit as st
import importlib

# *** Import utilities
from scripts.executor import Executor
from managers.data_manager import DataManager
from managers.export_manager import ExportManager
from managers.llm_manager import LlmManager
from managers.prompt_manager import PromptManager
from managers.session_manager import SessionManager

from scripts.steep_generate import gen_trend_report_1, gen_trend_report_2

import datetime as dt
import json
import time

import streamlit as st
from code_editor import code_editor






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

with st.sidebar:
        if st.button("清除所有暫存"):
            st.cache_data.clear()
            for var in st.session_state.keys():
                if var not in ['authentication_status', 'authenticator', 'logout', 'init', 'config']:
                    del st.session_state[var]

            SessionManager.session_state_clear('steep')
            SessionManager.session_state_clear('self-select')

            st.rerun()

        if st.button("顯示所有暫存"):
            SessionManager.show_sessions()



#*******************************************************************************************************************


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

# ***************************************** Config****************************************
st.title("STEEP +B")
if 'steep_start' not in st.session_state:
    st.session_state['steep_start'] = None
if 'steep_end' not in st.session_state:
    st.session_state['steep_end'] = None
if 'steep_topic' not in st.session_state:
    st.session_state['steep_topic'] = None
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = None
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None
if 'CLAUDE_KEY' not in st.session_state:
    st.session_state['CLAUDE_KEY'] = ""
if 'OPENAI_KEY' not in st.session_state:
    st.session_state['OPENAI_KEY'] = ""
if 'KEY_verified' not in st.session_state:
    st.session_state['KEY_verified'] = False
if "model_type" not in st.session_state:
    st.session_state['model_type'] = ""
if 'steep_running' not in st.session_state:
    st.session_state['steep_running'] = False



# *** 模型選擇 
if st.session_state['model_type'] == "":
    st.info("**請先選擇欲使用的語言模型**")
    if st.button("點擊開啟選單"):
        LlmManager.model_selection()





def main():
    # *** Model Reset Button
    with st.sidebar:
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

    # *** left column: user input; right column: progress and results
    left_col, right_col = st.columns((1/2, 1/2))
    with left_col:
        st.info("使用前請至 DEMO Videos 頁面觀看說明影片")

    with right_col:
        st.error("**執行後至完成前，請不要對頁面進行操作，以免直接重來。**", icon="⚠️")
        console_box_1 = st.empty()
        console_box_2 = st.empty()
        output_box = st.empty()

    with console_box_1.container():
        st.subheader("進度報告")

    with output_box.container():
        st.subheader("產出結果下載連結")
        
        

    # *************************** Left Column - User Input ***************************
    with left_col:
        st.subheader("基本資料輸入")
        subcol1, subcol2 = st.columns((1/2, 1/2))
        with subcol1:
            user_name = st.text_input("你的暱稱")
        # st.info("Please type in your email address so that we can send the results to you when completed")
        with subcol2:
            user_email = st.text_input("電子郵件地址")
        # *** Date input ***
        st.subheader("選擇新聞來源之時間範圍")
        subcol3, subcol4 = st.columns((1/2, 1/2))
        with subcol3:
            start_date = st.date_input('Starting Date')
            
        with subcol4:
            end_date = st.date_input('Ending Date')
            

        subcol5, subcol6 = st.columns((1/2, 1/2))
        # *** Output Format input ***
        with subcol5:
            st.subheader("輸出格式")
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

        # *** Topics input ***
        with subcol6:
            st.subheader("選擇主題")
            topic_to_deal = []
            if ppt or excel:
                topic_to_deal = st.selectbox("Choose one topic", ["social", "technological", "environmental", "economic", "political", "business_and_investment"])
            else:
                topic_to_deal = st.selectbox("Choose one topic", ["social", "technological", "environmental", "economic", "political", "business_and_investment"], disabled = True)
            daily_regen = st.toggle("是否重新產生每日摘要")

    # *** Check if the inputs are valid ***
    # COND1 - 7 為必須滿足的條件。COND8 為建議滿足的條件。
    existing_projects = SessionManager.steep_database(method = 'fetch')
    COND1 = user_name != ""
    COND2 = user_email != ""
    COND3 = start_date <= dt.date.today()
    COND4 = end_date <= dt.date.today()
    COND5 = start_date < end_date
    COND6 = not ([summary_output, ppt, excel] == [False, False, False])
    COND7 = not (ppt or excel) & (topic_to_deal == [])
    COND8 = sum([proj_name in existing_projects['primary_key'].tolist() for proj_name in [f'{start_date}_{end_date}_{topic}' for topic in topic_to_deal]]) == 0

    # 如果該專案名稱與日期已經有製作過的紀錄 -> 提醒使用者
    if not COND8:
        with left_col:
            st.warning("該時間段之 STEEP 趨勢報告已經存在於資料庫中（可以於 Archive 頁面查詢）。若要重新製作，會覆蓋掉舊的資料。若仍要執行請按 submit。", icon = '⚠️')


    # ******** Submission, Console Log, and Outputs ********
    # *** Submit and Run ***
    st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 50px;
        font-size: 20px;
        align-items: center;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        transition: transform 0.05s;
    }
    </style>
    """, unsafe_allow_html=True)

    with left_col:
        submission = st.button("Submit", type = "primary")


    # *************************** Right Column - Console and Output placeholders ***************************
    # *** After submission button is clicked
    if submission:
        
        # *** first, check all input schema is required ***
        if not COND1:
            with left_col:
                st.warning('Please input your nickname!')
        if not COND2:
            with left_col:
                st.warning('Please input your email address!')
        if not COND3:
            with left_col:
                st.warning('Starting Date should not be later than today!!')
        if not COND4:
            with left_col:
                st.warning('Ending Date should not be later than today!!')
        if not COND5:
            with left_col:
                st.warning('Starting Date should be prior to Ending Date!!')
        if not COND6:
            with left_col:
                st.warning('Please select at least one output format!')
        if not COND7:
            with left_col:
                st.warning('Please select at least one topic')

        
        # *** If the input date format is valid -> run
        if COND1 & COND2 & COND3 & COND4 & COND5 & COND6 & COND7:

            if (start_date == st.session_state['steep_start']) & (end_date == st.session_state['steep_end']):
                st.cache_data.clear()

            st.session_state['steep_start'] = start_date
            st.session_state['steep_end'] = end_date
            st.session_state['steep_topic'] = topic_to_deal
            st.session_state['user_name'] = user_name
            st.session_state['user_email'] = user_email
            if 'steep_summary' in st.session_state:
                del st.session_state['steep_summary']
            if 'fetched_raw' in st.session_state:
                del st.session_state['fetched_raw']

            st.session_state['steep_running'] = 'step1'

    # *** Step1: News Summary, Generate three version trend reports, Aggregation, Event Classification
    if st.session_state['steep_running'] == 'step1':
        console_box_1.empty()
        console_box_2.empty()
        with console_box_1.container():

            st.subheader("進度報告")
            # * Undo button
            if st.button("Undo", key = 'back_to_step0'):
                st.session_state['steep_running'] = False
                for session in ["steep_trend_basic", "steep_three_vers", "steep_trends_with_events", "steep_trends_with_events_modified"]:
                    try:
                        del st.session_state[session]
                    except:
                        pass
                st.rerun()

            try:
                gen_trend_report_1(st.session_state['steep_topic'],
                        st.session_state['steep_start'],
                        st.session_state['steep_end'],
                        st.session_state['user_name'],
                        st.session_state['user_email'])
                SessionManager.send_notification_email(st.session_state['user_name'], st.session_state['user_email'], 'step_1_completed')
            except Exception as error:
                st.error('some error happened..')
                st.warning(error)
                SessionManager.send_notification_email(st.session_state['user_name'], st.session_state['user_email'], 'failed', error)


            # ** 生成基本趨勢報告框架和分類事件之後，開啟 code editor 以供使用者調整內容。後續推論將以使用者修改過後的內容為基礎。
            st.info("趨勢報告的基礎架構已生成，如下。請確認是否有要修改的地方。\n\n若有修改，記得點擊右側儲存按鈕後再送出。")
            bs = [{
                "name": "→點擊儲存變更",
                "feather": "Save",
                "alwaysOn": True,
                "commands": ["submit"],
                "style": {"top": "0.46rem", "right": "0.4rem"},
                "hasText": True
                }]         # * -> code editor 右上角的 Save 按鈕。點擊後，使用者變更後的資料將被存放置 session_state。

            response_dict = code_editor(json.dumps({"trends_with_events": st.session_state['steep_trends_with_events']}, indent = 4, ensure_ascii = False), lang = 'json',
                                        buttons = bs,
                                        height=[10, 20],
                                        options = {"wrap": True})

            if st.button("送出，開始推論:red[**（送出前記得點擊右上角按鈕儲存變更）**]"):

                try:
                    st.session_state['steep_trends_with_events_modified'] = json.loads(response_dict['text'])['trends_with_events']
                    st.session_state['steep_running'] = 'step2'
                    st.rerun()

                except json.decoder.JSONDecodeError:
                    st.warning("JSON 結構無效。請**點擊儲存變更**，並確保內容為有效 JSON 格式")
                    st.stop()


    # *** Step2: Inference, and final summary -> json -> pptx/excel
    elif st.session_state['steep_running'] == 'step2':
        console_box_1.empty()
        console_box_2.empty()
        with console_box_2.container():
            st.subheader("進度報告")

            # * Undo button
            if st.button("Undo", key = 'back_to_step1'):
                st.session_state['steep_running'] = 'step1'
                for session in ["steep_trend_inference", "steep_final_summary"]:
                    try:
                        del st.session_state[session]
                    except:
                        pass
                st.rerun()

            # * Execute
            try:
                result = gen_trend_report_2(st.session_state['steep_topic'],
                        st.session_state['steep_start'],
                        st.session_state['steep_end'],
                        st.session_state['user_name'],
                        st.session_state['user_email'])
            except Exception as error:
                st.error('some error happened..')
                st.warning(error)
                SessionManager.send_notification_email(st.session_state['user_name'], st.session_state['user_email'], 'failed', error)
            
            
            # ** Create Ppt slides && Post back to DB && record in Google Sheet
            try:
                res_pptx_bs = ExportManager.STEEP.create_pptx(st.session_state['steep_topic'], result)
                filename = f"{st.session_state['steep_topic']}_trends_{st.session_state['steep_start']}-{st.session_state['steep_end']}.pptx"
                DataManager.post_files(filename, 
                                        res_pptx_bs, 
                                        str(dt.datetime.today() + dt.timedelta(365)), 
                                        st.session_state['user_name'], 
                                        st.session_state['user_email'])
                
                SessionManager.steep_database('update', 
                            st.session_state['steep_start'], 
                            st.session_state['steep_end'], st.session_state['steep_topic'], st.session_state['user_name'], st.session_state['user_email'], dt.date.today())
            except Exception as error:
                st.error('some error happened..')
                st.warning(error)
                SessionManager.send_notification_email(st.session_state['user_name'], st.session_state['user_email'], 'failed', error)

            # ** Create excel && Post back to DB && record in Google Sheet
            try:
                b64_excel = ExportManager.STEEP.create_excel(
                                st.session_state['steep_start'], 
                                st.session_state['steep_end'], ['social', 'technological', 'economic', 'environmental', 'political', 'business_and_investment'])   
                filename = f'{st.session_state['steep_start']}-{st.session_state['steep_end']}_STEEP.xlsx'
                DataManager.post_files(filename,
                                        b64_excel,
                                        str(dt.datetime.today() + dt.timedelta(365)), 
                                        st.session_state['user_name'], 
                                        st.session_state['user_email'])
                SessionManager.steep_database('update', 
                                st.session_state['steep_start'], 
                                st.session_state['steep_end'], "EXCEL", st.session_state['user_name'], st.session_state['user_email'], dt.date.today())
            except Exception as error:
                st.error('some error happened..')
                st.warning(error)
                SessionManager.send_notification_email(st.session_state['user_name'], st.session_state['user_email'], 'failed', error)

        with output_box.container():
            st.subheader("產出結果下載連結")
            try:
                if ppt:

                    st.success("Ppt slides created! You can download now💥")
                    st.markdown(DataManager.get_output_download_link(
                        st.session_state['steep_start'], 
                        st.session_state['steep_end'], 
                        st.session_state['steep_topic'], 'pptx', 'steep'), unsafe_allow_html = True)

                if excel:
                    
                    st.success("Excel file created! You can download now💥")
                    st.markdown(DataManager.get_output_download_link(st.session_state['steep_start'], 
                                    st.session_state['steep_end'], '', 'xlsx', 'steep'), unsafe_allow_html = True)

                if summary_output:
                    st.success("Here is the daily summary for the period you requested💥")
                    st.markdown(DataManager.get_summary_download_link(st.session_state['steep_start'], 
                                    st.session_state['steep_end']), unsafe_allow_html = True)
                    
                SessionManager.send_notification_email(st.session_state['user_name'], st.session_state['user_email'], 'completed')
                
            except Exception as error:
                st.error('some error happened..')
                st.warning(error)
                SessionManager.send_notification_email(st.session_state['user_name'], st.session_state['user_email'], 'failed', error)

        SessionManager.session_state_clear('steep')




# ** user_token switch: if the user is required to input their own token
if st.secrets['permission']['user_token'] == True:
    # ** Ensure that the model type is selected
    if st.session_state['model_type'] == "":
        st.stop()

    # ** Verify API token
    if st.session_state['KEY_verified'] == False:
        try:
            st.info("**請設定 API key**")
            if st.button("點擊設定 API key"):
                LlmManager.customer_token(st.session_state['model_type'])
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
    