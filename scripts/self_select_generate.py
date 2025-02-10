from managers.data_manager import DataManager
from managers.llm_manager import LlmManager
from managers.session_manager import SessionManager
from managers.prompt_manager import PromptManager
from .self_select_summary import summarize_all

# necessary modules
import pandas as pd
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
import datetime as dt
import json
import tqdm
import time
import openpyxl
import base64
from io import BytesIO


def gen_trend_report_customized(title: str, start_date: str, end_date: str, user_name, user_email, raw_data, cols, additional, data = None, summary_update = None) -> json:


    # *** Try to import necessary data ***
    # if failed, generate by "monthly_summary()" function 
    if data is None:
        try:
            data = DataManager.b64_to_dataframe(DataManager.get_files(f"Summary_{title}_{start_date}-{end_date}.xlsx", 'xlsx'))  
        except:
            data = summarize_all(raw_data, user_name, user_email, title, start_date, end_date)
    # -------------------------------------------------------------------------------------
    st_bar = st.progress(0, text = f"Generating {title} trend report...")
    # *** Generate three versions of trend reports ***
    st_bar.progress(0, text = f"Generating {title} trend report (ver 1)")
    try:
        three_vers = st.session_state['self_select_three_vers']
    except:
        in_message = ""
        for index, row in data.iterrows():
            if row[f"重點新聞摘要"] != "" :
                in_message += row["batch"] + "\n" + '\n'.join(row[f"重點新聞摘要"]) + "\n"
    
        # progress bar: there are 6 steps so the denominator is 6
        st_bar.progress(0, text = f"Generating {title} trend report (three versions)...")
            
        three_vers = {}
        for ver in range(1, 4):
            chain = LlmManager.create_prompt_chain(PromptManager.SELF_SELECT.step2_prompt(title, ver, additional), st.session_state['model'])
            three_vers.update(LlmManager.llm_api_call(chain, in_message))
            
            st_bar.progress(1/5 * (ver/3), f"({round(1/5 * (ver/3) * 100)}%) Generating {title} trend report (ver {ver + 1})")
        st.session_state['self_select_three_vers'] = three_vers

    # -------------------------------------------------------------------------------------

    # *** Aggregate three versions into one ***
    st_bar.progress(1/5, text = f"(20%) Aggregating three version {title} trend report")
    try:
        trends_basic = st.session_state['self_select_trends_basic']
    except:

        in_message = ""
        for ver, value in three_vers.items():
            in_message = in_message + '\n' + ver + '\n\n' + json.dumps(value) + '\n\n'

        chain = LlmManager.create_prompt_chain(PromptManager.SELF_SELECT.step3_prompt(additional), 
                                               st.session_state['model'])
        trends_basic = LlmManager.llm_api_call(chain, in_message)

        st.session_state['self_select_trends_basic'] = trends_basic

    # -------------------------------------------------------------------------------------
    # *** Classify representative events to corresponding trend ***
    # events in the topic to be classified
    st_bar.progress(2/5, text = f"(40%) Classifying events to each trend...")
    try:
        trends_with_events = st.session_state['self_select_trends_with_events']
    except:
        events_message = ""
        for index, row in data.iterrows():
            if row[f"重點新聞摘要"] != "" :
                events_message += row["batch"] + "\n" + '\n'.join(row[f"重點新聞摘要"]) + "\n"

        # classify events to each trend
        trends_with_events = []
        count = 1
        for name, trend in trends_basic.items():
            trend_message = json.dumps(trend)
            in_message = f'''
            總共有這些事件。請分類：\n\n{events_message}\n\n----\n\n*****主要趨勢{count}（{name}）*****：\n\n{trend_message}
            '''
            chain = LlmManager.create_prompt_chain(PromptManager.SELF_SELECT.step4_prompt(additional),
                                                   st.session_state['model'])
            trends_with_events.append(LlmManager.llm_api_call(chain, in_message))
            st_bar.progress(2/5 + 1/5 * (count/len(trends_basic)), text = f"({round((2/5 + 1/5 * (count/len(trends_basic))) * 100)}%) Classifying events to each trend..." )
            count += 1

        st.session_state['self_select_trends_with_events'] = trends_with_events

    # -------------------------------------------------------------------------------------
    
    # *** Inference ! 重頭戲 ***
    st_bar.progress(3/5, text = f"(60%) Inferring {title} trend report...")
    try:
        trend_inference = st.session_state['self_select_trend_inference']
    except:
        trend_inference = {}
        count = 1
        for trend in trends_with_events:
            in_message = json.dumps(trend)
            chain = LlmManager.create_prompt_chain(PromptManager.SELF_SELECT.step5_prompt(cols, additional),
                                                   st.session_state['model'])
            trend_inference.update(LlmManager.llm_api_call(chain, in_message))
            st_bar.progress(3/5 + 1/5 * (count/len(trends_with_events)), text = f"({round((3/5 + 1/5 * (count/len(trends_with_events))) * 100)}%) Inferring {title} trend report..." )
            count += 1
        st.session_state['self_select_trend_inference'] = trend_inference
    # -------------------------------------------------------------------------------------

    # *** Final summarization *** 
    st_bar.progress(4/5, text = f"Concluding {title} trend report...")
    try:
        final_summary = st.session_state['self_select_final_summary']
        
    except:
        in_message = ""
        for name, trend in trend_inference.items():
            message = f'''{name}: \n\n1. 趨勢洞察：\n{trend['<a>趨勢洞察']}\n\n2. 重要關係人：\n{trend['<d>重要關係人']}\n\n3. 
            '''#缺口：{trend["<e>缺口"]}\n\n
            in_message += message

        chain = LlmManager.create_prompt_chain(PromptManager.SELF_SELECT.step6_prompt(additional),
                                               st.session_state['model'])
        final_summary = LlmManager.llm_api_call(chain, in_message)
        st.write('''    🤝 Final summarization completed! ''')
        st_bar.progress(1, text = f"(100%) Complete!")
        st_bar.empty()
        st.session_state['self_select_final_summary'] = final_summary
    # -------------------------------------------------------------------------------------
        

    result_json = DataManager.merge_dict(final_summary, trend_inference)
    encoded_json = base64.b64encode(json.dumps(result_json).encode('utf-8')).decode('utf-8')

    DataManager.post_files(file_name = f"{title}_trend_report_{start_date}-{end_date}.json", 
                           file_content = encoded_json, 
                            expiration = str(dt.datetime.today() + dt.timedelta(90)), 
                            user_name = user_name, 
                            user_email = user_email)

    return result_json

