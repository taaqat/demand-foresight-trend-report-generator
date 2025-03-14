import streamlit as st 
import requests
from managers.data_manager import DataManager
from managers.export_manager import ExportManager
from managers.session_manager import SessionManager

# * page layout
if "page_config_set" not in st.session_state:
    st.set_page_config(page_title='Demand Foresight Tools', page_icon=":material/home:", layout="wide")
    st.session_state["page_config_set"] = True

st.title("ARCHIVE")

    
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
div.stDownloadButton > button {
    width: 80%;  /* 設置按鈕寬度為頁面寬度的 50% */
    height: 67px;
    margin-left: 0;
    margin-right: auto;
}
div.stDownloadButton > button:hover {
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
        st.sidebar.page_link("https://demand-foresight-citation-energy.streamlit.app/", label = "與文件對話", icon = ':material/link:')

# if st.secrets['permission']['visualization'] == True:
    #      st.sidebar.write("**視覺化界面**")
    #     st.sidebar.page_link("[小賴做的視覺化界面]", label = "", icon = ':material/add_circle:')

with st.sidebar:
    SessionManager.fetch_IP()

# **************************************************************************************************************

# TAB_HTML, TAB_DOWNLOAD = st.tabs(['STEEP Slides', 'All Available Archives'])

# with TAB_HTML:
#     left_col, right_col, but_col = st.columns((0.45, 0.45, 0.1))
#     month_df = SessionManager.steep_database('fetch').iloc[::-1]

#     with left_col:
#         topic_selection = st.selectbox("選擇主題", ['social', 'economic', 'environmental', 'technological', 'political', 'business_and_investment'])
#     with right_col:
#         period_selection = st.selectbox("選擇時間區段", (month_df['start_date'] + '-' + month_df['end_date']).unique())
    

#     filename = topic_selection + '_trends_' + period_selection + '_html.txt'
    
#     try:
#         html_body = DataManager.get_files(filename, 'txt')
#         with but_col:
#             download_btn = st.download_button(
#                 label = "",
#                 data = html_body,
#                 file_name = topic_selection + '_trends_' + period_selection + '.html',
#                 type="primary",
#                 icon=":material/download:",
#                 mime="html"
#             )
#         st.html(html_body)
        
        
#     except Exception as e:
#         st.error("所選主題與時間段並無 HTML 簡報檔案！")

# with TAB_DOWNLOAD:
left_col, right_col = st.columns((1/2, 1/2))
with right_col:
    right_box = st.container(border = True, height = 465)

with right_box:
    st.subheader("Download links")
    # st.info("在公司的資料庫中，同一檔名的檔案，新的會覆蓋舊的檔案。因此此處所查詢到的資料皆為最新版本。")

# ******** Left Column - User Input ********
with left_col:
    # *** STEEP Archive ***
    st.subheader("STEEP Archive")
    month_df = SessionManager.steep_database('fetch')
    month_selected = st.selectbox("Choose the time period that you want to get archive files from",
                                    month_df[['start_date', 'end_date']].agg("_".join, axis = 1).unique())
    start_date = month_selected.split("_")[0]
    end_date = month_selected.split("_")[1]

    steep_submit = st.button("Search STEEP Archive", type = "primary")

    st.divider()

    # *** Self Select Archive ***
    st.subheader("自選主題 Archive")
    projects = SessionManager.self_select_database('fetch')
    project_selected = st.selectbox("Choose the project that you want to get archive files from", 
                    projects['primary_key'].unique())
    
    proj_name, proj_start, proj_end = tuple(projects[projects['primary_key'] == project_selected][['project_name', 'start_date', 'end_date']].iloc[0].tolist())
    self_select_submit = st.button("Search all downloadable files for this project", type = "primary")


# *** STEEP Archive Searching ***
if steep_submit:
    with right_box:
        with st.spinner("Loading files..."):
            # Get the trend report PPTx
            with st.expander("Trend Reports Slides", icon = ':material/slide_library:'):
                for topic in ['social', 'technological', 'environmental', 'economic', 'political', 'business_and_investment']:
                    try:
                        
                        # getFiles(f"{topic}_trends_{start_date}-{end_date}.pptx", 'pptx')
                        st.markdown(DataManager.get_output_download_link(start_date, end_date, topic, 'pptx', 'steep'), unsafe_allow_html = True)
                    except:
                        pass
                

            # Get the trend report in JSON
            with st.expander("Trend Reports JSON", icon = ':material/code:'):
                for topic in ['social', 'technological', 'environmental', 'economic', 'political', 'business_and_investment']:
                    try:
                        # json_return = getFiles(f"{topic}_trend_report_{start_date}-{end_date}.json", 'json')
                        # json_string = json.dumps(json_return)
                        # b64_json = base64.b64encode(json_string.encode()).decode()
                        # st.markdown(f'<a href="data:application/json;base64,{b64_json}" download="{topic}_trend_report_{start_date}-{end_date}.json"> Download {topic}_trend_report_{start_date}-{end_date}.json</a>', unsafe_allow_html = True)
                        st.markdown(DataManager.get_output_download_link(start_date, end_date, topic, 'json', 'steep'), unsafe_allow_html = True)

                    except:
                        pass
            # Get the trend report in excel
            with st.expander("Trend Reports Excel (Aggregated)", icon = ':material/table:'):
                try:
                    # getFiles(f"{start_date}-{end_date}_STEEP.xlsx", 'xlsx')
                    # st.markdown(get_Excel_download_link(start_date, end_date), unsafe_allow_html = True)
                    st.markdown(DataManager.get_output_download_link(start_date, end_date, topic, 'xlsx', 'steep'), unsafe_allow_html = True)
                except:
                    pass

            # Get monthly summary excel
            with st.expander("Monthly Summary (xlsx)", icon = ':material/table:'):
                try:
                    # getFiles(f"Summary_{start_date}-{end_date}.xlsx", 'xlsx')
                    # st.markdown(summary_raw_download_link(start_date, end_date), unsafe_allow_html = True)
                    st.markdown(DataManager.get_summary_download_link(start_date, end_date, topic = None), unsafe_allow_html = True)
                    
                except:
                    pass
                
            # Get daily summary json
            # with st.expander("Daily Summary (json, per day, utf-8 encoded)", icon = ':material/code:'):
            #     for date in pd.date_range(start = start_date, end = end_date):
            #         try:
            #             json_return = getFiles(f"Daily_Summary_{date.date()}.json", 'json')
            #             json_string = json.dumps(json_return)
            #             b64_json = base64.b64encode(json_string.encode()).decode()
                            
            #             st.markdown(f'<a href="data:application/json;base64,{b64_json}" download="Daily_Summary_{date.date()}.json"> Download Daily_Summary_{date.date()}.json</a>', unsafe_allow_html = True)
            #         except:
            #             pass

# *** SelfSelect Archive Searching ***
if self_select_submit:
    with right_box:
        with st.spinner("Loading files..."):
            # Get the trend report PPTx
            with st.expander("Trend Reports Slides", icon = ':material/slide_library:'):
                try:
                    # getFiles(f"{proj_name}_trends_{proj_start}-{proj_end}.pptx", 'pptx')
                    # st.markdown(get_Pptx_download_link(proj_start, proj_end, proj_name), unsafe_allow_html = True)

                    st.markdown(DataManager.get_output_download_link(proj_start, proj_end, proj_name, 'pptx', 'self_select'), unsafe_allow_html = True)

                except:
                    pass

            # Get the trend report in JSON
            with st.expander("Trend Reports JSON" , icon = ':material/code:'):
                try:
                    # json_return = getFiles(f"{proj_name}_trend_report_{proj_start}-{proj_end}.json", 'json')
                    # json_string = json.dumps(json_return)
                    # b64_json = base64.b64encode(json_string.encode()).decode()
                        
                    # st.markdown(f'<a href="data:application/json;base64,{b64_json}" download="{proj_name}_trend_report_{proj_start}-{proj_end}.json"> Download {proj_name}_trend_report_{proj_start}-{proj_end}.json</a>', unsafe_allow_html = True)
                    st.markdown(DataManager.get_output_download_link(proj_start, proj_end, proj_name, 'json', 'self_select'), unsafe_allow_html = True)
                
                except:
                    pass
            # Get the trend report in excel
            with st.expander("Trend Reports Excel", icon = ':material/table:'):
                try:
                    # excel_filename = f'{proj_name}_{proj_start}-{proj_end}_trend_report.xlsx'
                    
                    # getFiles(excel_filename, 'xlsx')
                
                    # with open(f'./output/{proj_name}_{proj_start}-{proj_end}_trend_report.xlsx', "rb") as file:
                    #     contents = file.read()
                    # b64_excel = base64.b64encode(contents).decode()
                    
                    # os.remove(f'./output/{excel_filename}')
                    # st.markdown(f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_excel}" download="{excel_filename}">Download {proj_name} trend report from {proj_start} to {proj_end}</a>', unsafe_allow_html = True)
                    st.markdown(DataManager.get_output_download_link(proj_start, proj_end, proj_name, 'xlsx', 'self_select'), unsafe_allow_html = True)

                except:
                    pass

            # Get monthly summary excel
            with st.expander("Monthly Summary (xlsx)", icon = ':material/table:'):
                try:
                    # excel_filename = f"Summary_{proj_name}_{proj_start}-{proj_end}.xlsx"
                    # getFiles(excel_filename, 'xlsx')
                    
                    # with open(f"./output/{excel_filename}", "rb") as file:
                    #     contents = file.read()

                    # b64_excel = base64.b64encode(contents).decode()
                    # url = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_excel}" download="{excel_filename}">Download summary data for {proj_name} project from {start_date} to {end_date}</a>'
                    # st.markdown(url, unsafe_allow_html = True)
                    st.markdown(DataManager.get_summary_download_link(proj_start, proj_end, proj_name), unsafe_allow_html = True)
                except:
                    pass

