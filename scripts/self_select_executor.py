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
            filename = f"{title.replace(' ', '_')}_trends_{start_date}-{end_date}.pptx"
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
        
        SessionManager.send_notification_email(user_name, user_email, type = 'completed')