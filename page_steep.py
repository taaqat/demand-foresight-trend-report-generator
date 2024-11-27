import streamlit as st

# *** Import utilities
from managers.data_manager import DataManager
from managers.export_manager import ExportManager
from managers.llm_manager import LlmManager
from managers.prompt_manager import PromptManager
from managers.session_manager import SessionManager

from scripts.executor import Executor
import datetime as dt

# ***************************************** Config****************************************
st.title("STEEP +B")
st.session_state['steep_start'] = None
st.session_state['steep_end'] = None

# *****************************************************************************************
# ****************************************** GUI ******************************************
# *** left column: user input; right column: progress and results
left_col, right_col = st.columns((1/2, 1/2))
with left_col:
    st.info("We recommend read the instruction before implement")

with right_col:
    st.error("**執行後至完成前，請不要對頁面進行操作，以免直接重來。**", icon="⚠️")
    console_box = st.container(border = True)
    output_box = st.container(border = True)

with console_box:
    st.subheader("進度報告")

with output_box:
    st.subheader("產出結果下載連結")
    
    

# *************************** Left Column - User Input ***************************
with left_col:
    st.subheader("基本資料輸入")
    subcol1, subcol2 = st.columns((1/2, 1/2))
    with subcol1:
        user_name = st.text_input("Please type in your nickname 👇")
    # st.info("Please type in your email address so that we can send the results to you when completed")
    with subcol2:
        user_email = st.text_input("Please type in your email address 👇")
    # *** Date input ***
    st.subheader("請選擇新聞來源之時間範圍")
    subcol3, subcol4 = st.columns((1/2, 1/2))
    with subcol3:
        start_date = st.date_input('Starting Date')
        
    with subcol4:
        end_date = st.date_input('Ending Date')
        

    subcol5, subcol6 = st.columns((1/2, 1/2))
    # *** Output Format input ***
    with subcol5:
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

    # *** Topics input ***
    with subcol6:
        st.subheader("請選擇主題")
        topic_to_deal = []
        if ppt or excel:
            topic_to_deal = st.multiselect("You can choose multiple topics", ["social", "technological", "environmental", "economic", "political", "business_and_investment"])
        else:
            topic_to_deal = st.multiselect("You can choose multiple topics", ["social", "technological", "environmental", "economic", "political", "business_and_investment"], disabled = True)


# *** Check if the inputs are valid ***
# XOR1 - 7 為必須滿足的條件。XOR8 為建議滿足的條件。
existing_projects = SessionManager.steep_database(method = 'fetch')
XOR1 = user_name != ""
XOR2 = user_email != ""
XOR3 = start_date <= dt.date.today()
XOR4 = end_date <= dt.date.today()
XOR5 = start_date < end_date
XOR6 = not ([summary_output, ppt, excel] == [False, False, False])
XOR7 = not (ppt or excel) & (topic_to_deal == [])
XOR8 = sum([proj_name in existing_projects['primary_key'].tolist() for proj_name in [f'{start_date}_{end_date}_{topic}' for topic in topic_to_deal]]) == 0

# 如果該專案名稱與日期已經有製作過的紀錄 -> 提醒使用者
if not XOR8:
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
</style>
""", unsafe_allow_html=True)

with left_col:
    submission = st.button("Submit", type = "primary")


# *************************** Right Column - Console and Output placeholders ***************************
# *** After submission button is clicked
if submission:
    
    # *** first, check all input schema is required ***
    if not XOR1:
        with left_col:
            st.warning('Please input your nickname!')
    if not XOR2:
        with left_col:
            st.warning('Please input your email address!')
    if not XOR3:
        with left_col:
            st.warning('Starting Date should not be later than today!!')
    if not XOR4:
        with left_col:
            st.warning('Ending Date should not be later than today!!')
    if not XOR5:
        with left_col:
            st.warning('Starting Date should be prior to Ending Date!!')
    if not XOR6:
        with left_col:
            st.warning('Please select at least one output format!')
    if not XOR7:
        with left_col:
            st.warning('Please select at least one topic')

    
    # *** If the input date format is valid -> run
    if XOR1 & XOR2 & XOR3 & XOR4 & XOR5 & XOR6 & XOR7:

        if (start_date == st.session_state['steep_start']) & (end_date == st.session_state['steep_end']):
            st.cache_data.clear()

        st.session_state['steep_start'] = start_date
        st.session_state['steep_end'] = end_date

        # ******************************** Console Box *************************************
        # *** Render all progresses and results on the RHS ***
        with console_box:
            
            try:
                with st.spinner("Processing..."):
                    # *** main function for inference and generating trend report ***
                    Executor.steep_run(
                        user_name, user_email, start_date, end_date, topic_to_deal
                    )
            except:
                SessionManager.send_notification_email(user_name, user_email, type = 'failed')
                raise NotImplementedError("Something went wrong... Please trace back to debug.")
                
        # ******************************** Output Box *************************************
        # *** check the output format, read from cache folders, and generate download link ***
        with output_box:
            if ppt:

                st.success("Ppt slides created! You can download now💥")
                for topic in topic_to_deal:
                    st.markdown(DataManager.get_output_download_link(start_date, end_date, topic, 'pptx'), unsafe_allow_html = True)

            if excel:
                
                st.success("Excel file created! You can download now💥")
                st.markdown(DataManager.get_output_download_link(start_date, end_date, '', 'xlsx'), unsafe_allow_html = True)

            if summary_output:
                st.success("Here is the daily summary for the period you requested💥")
                st.markdown(DataManager.get_summary_download_link(start_date, end_date), unsafe_allow_html = True)

