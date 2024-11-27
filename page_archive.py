import streamlit as st 
from managers.data_manager import DataManager
from managers.export_manager import ExportManager
from managers.session_manager import SessionManager
st.title("ARCHIVE")


left_col, right_col = st.columns((1/2, 1/2))
with right_col:
    right_box = st.container(border = True, height = 465)

with right_box:
    st.subheader("Download links")
    st.info("在公司的資料庫中，同一檔名的檔案，新的會覆蓋舊的檔案。因此此處所查詢到的資料皆為最新版本。")
    
# 設定按鈕樣式
st.markdown("""<style>
    div.stButton > button {
        width: 100%;  /* 設置按鈕寬度為頁面寬度的 50% */
        height: 50px;
        margin-left: 0;
        margin-right: auto;
    }
    </style>
    """, unsafe_allow_html=True)

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
