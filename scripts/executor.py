# 
# ** Executor: define main functions to be run after user submits the form

from .self_select_summary import summarize_all
from .self_select_generate import gen_trend_report_customized
from .steep_summary import monthly_summary
from .steep_generate import gen_trend_report
from managers.data_manager import DataManager
from managers.export_manager import ExportManager
from managers.llm_manager import LlmManager
from managers.prompt_manager import PromptManager
from managers.session_manager import SessionManager

import datetime as dt
import pandas as pd
import streamlit as st
import time

class Executor:

    # ******* STEEP *******
    @staticmethod
    def steep_run(user_name, 
                  user_email, 
                  start_date, 
                  end_date, 
                  topics: list, 
                  excel_output = True, 
                  ppt_output = True):

        # *** generate summary data if not existing
        try:
            summary_data = st.session_state['steep_summary']
        except:
            try:
                summary_data = DataManager.b64_to_dataframe(DataManager.get_files(f"Summary_{start_date}-{end_date}.xlsx", 'xlsx'))
            except:
                summary_data = monthly_summary(start_date, end_date, user_name, user_email)

        # *** generate trend report
        sys_info = lambda x: f"Generating {x} trend report... "
        st_bar = st.progress(0, sys_info(""))
        counter = 0

        if [excel_output, ppt_output] != [False, False]:
            
            # *** run trend report generator and generate powerpoint
            for i, topic in enumerate(topics):

                st_bar.progress(counter, sys_info(topic))

                begin = time.time()
                result = gen_trend_report(topic, start_date, end_date, user_name, user_email, summary_data)
                finish = time.time()

                counter = i/len(topics)
                st_bar.progress(counter, sys_info(topic))
                
                st.write(f'💫 {topic} topic completed! {round(finish - begin, 3)} seconds spent.')

                res_pptx_bs = ExportManager.STEEP.create_pptx(topic, result)
                filename = f"{topic}_trends_{start_date}-{end_date}.pptx"
                DataManager.post_files(filename, res_pptx_bs, str(dt.datetime.today() + dt.timedelta(365)), user_name, user_email)
                
                SessionManager.steep_database('update', start_date, end_date, topic, user_name, user_email, dt.date.today())
                SessionManager.session_state_clear('steep')

            # *** generate excels and post
            b64_excel = ExportManager.STEEP.create_excel(start_date, 
                                                         end_date, 
                                                         ['social', 'technological', 'economic', 'environmental', 'political', 'business_and_investment'])   
            filename = f'{start_date}-{end_date}_STEEP.xlsx'
            DataManager.post_files(filename,
                                   b64_excel,
                                   str(dt.datetime.today() + dt.timedelta(365)), 
                                   user_name, 
                                   user_email)
            SessionManager.steep_database('update', start_date, end_date, "EXCEL", user_name, user_email, dt.date.today())
            
        else:
            pass
        st_bar.progress(1, "Complete!")
        st_bar.empty()
        SessionManager.send_notification_email(user_name, user_email, type = 'completed')

    # ******* 自選主題 *******
    @staticmethod
    def self_select_run(user_name, 
                        user_email, 
                        title, 
                        keywords,
                        start_date, 
                        end_date, 
                        raw_data, 
                        cols,                              # ** trend report 中想要的欄位（重要關係人、微弱信號 etc）（user input）
                        additional,                        # ** 額外的 prompt（user input）
                        summary_data = None, 
                        excel_output = True, 
                        ppt_output = True, 
                        color = "#F3B915"):
        
        # *** generate summary data if not existing
        try:
            summary_data = st.session_state['self_select_summary']
        except:
            try:
                summary_data = DataManager.b64_to_dataframe(DataManager.get_files(f"Summary_{title}_{start_date}-{end_date}.xlsx", 'xlsx'))
            except:
                summary_data = summarize_all(raw_data, user_name, user_email, title, start_date, end_date)        

        if [excel_output, ppt_output] != [False, False]:
            # *** generate trend report
            begin = time.time()
            result = gen_trend_report_customized(
                title, start_date, end_date, user_name, user_email, raw_data, cols, additional, summary_data
            )
            finish = time.time()
            
            st.write(f'💫 {title} trend report completed! {round(finish - begin, 3)} seconds spent.')

            res_pptx_bs = ExportManager.SELF_SELECT.create_pptx(color, title, result)
            filename = f"{title.replace(" ", "_")}_trends_{start_date}-{end_date}.pptx"
            DataManager.post_files(filename, res_pptx_bs, str(dt.datetime.today() + dt.timedelta(365)), user_name, user_email)
            
            SessionManager.self_select_database('update', title, keywords, start_date, end_date, user_name, user_email, dt.date.today())
            try:
                SessionManager.session_state_clear('self-select')
            except:
                pass
            
            # *** generate excels and post
            b64_excel = ExportManager.SELF_SELECT.create_excel(start_date, end_date, title)   
            filename = f'{title.replace(" ", "_")}_{start_date}-{end_date}_trend_report.xlsx' 
            DataManager.post_files(filename,
                                    b64_excel,
                                    str(dt.datetime.today() + dt.timedelta(365)), 
                                    user_name, 
                                    user_email)
            SessionManager.self_select_database('update', title.replace(" ", "_"), keywords, start_date, end_date, user_name, user_email, dt.date.today())
        else:
            pass

        st.success("Completed!!")
        SessionManager.send_notification_email(user_name, user_email, type = 'completed')