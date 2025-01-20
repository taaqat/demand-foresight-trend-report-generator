from managers.data_manager import DataManager
from managers.llm_manager import LlmManager
from managers.session_manager import SessionManager
from managers.prompt_manager import PromptManager

# necessary modules
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
import datetime as dt
import tqdm
import time
import streamlit as st
import openpyxl
import json, base64, os
from io import BytesIO


def in_group_summarize(in_message, title, batch):

    chain = LlmManager.create_prompt_chain(sys_prompt = PromptManager.SELF_SELECT.step1_prompt(title, batch),
                                           model = st.session_state['model'])

    return LlmManager.llm_api_call(chain, in_message)


def summarize_all(raw_data, user_name, user_email, title, start_date, end_date, summary_output = True):

    
    summary_out = {}
    # progress bar at terminal
    st_bar = st.progress(0, "(0%) Summarizing news...")            # progress bar on streamlit UI

    # *** Divide the raw data into groups. Each group has 100 rows ***
    chunk_size = len(raw_data) // 5 if len(raw_data) // 5 != 0 else len(raw_data)
    chunks = [raw_data.iloc[i:i + chunk_size] for i in range(0, len(raw_data), chunk_size)]
  
    # *** Summarization ***
    for i, chunk in enumerate(chunks):
        contents = []
        for index, row in chunk.iterrows():
            # print(f"Row {index}: date={row['date']}, 重點摘要={row['重點摘要']}, 關鍵數據={row['關鍵數據']}")
            if row["重點摘要"] != "" :
                contents.append(row["重點摘要"] + "\n" + str(row["關鍵數據"]))
                
        in_message = f"****** Batch {i + 1} ******" + "\n" +"\n\n".join(contents) + "\n\n" + "*"*100
        response = in_group_summarize(in_message, title, i + 1)
        summary_out.update(response)
        st_bar.progress((i + 1)/len(chunks), f"({round((i + 1)/len(chunks) * 100)}%) Summarizing news...")

    st_bar.empty()
    st.write("Summary Completed!!")

    # * transform the dictionary format into panda dataframe
    summary_out = pd.DataFrame.from_dict(summary_out, orient = 'index').reset_index()
    summary_out.columns = ['batch', "重點新聞摘要"]

    # * store the monthly summary data in session state
    st.session_state['self_select_summary'] = summary_out

    # * post the file back to III database
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine = 'openpyxl') as writer:
        summary_out.to_excel(writer, index = False, sheet_name = 'Sheet1')
    excel_buffer.seek(0)  # Move to the beginning of the buffer
    b64_excel = base64.b64encode(excel_buffer.read()).decode('utf-8')
    DataManager.post_files(f"Summary_{title.replace(' ', '_')}_{start_date}-{end_date}.xlsx",
                           b64_excel,
                           str(dt.datetime.today() + dt.timedelta(90)),
                           user_name,
                           user_email)
    
    return summary_out
    
    