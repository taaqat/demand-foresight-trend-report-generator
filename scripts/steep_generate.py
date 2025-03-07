from managers.data_manager import DataManager
from managers.llm_manager import LlmManager
from managers.session_manager import SessionManager
from managers.prompt_manager import PromptManager
from .steep_summary import monthly_summary

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



def gen_trend_report(topic: str, start_date: str, end_date: str, user_name, user_email, data = None, daily_regen = False) -> json:

    # *** Try to import necessary data ***
    # if failed, generate by "monthly_summary()" function 
    if data is None:
        try:
            data = DataManager.b64_to_dataframe(DataManager.get_files(f"Summary_{start_date}-{end_date}.xlsx", 'xlsx'))  
        except:
            data = monthly_summary(start_date, end_date, user_name, user_email, daily_regen)
    # -------------------------------------------------------------------------------------
    st_bar = st.progress(0, text = f"({0}%) Generating {topic} trend report (three versions)...")
    # *** Generate three versions of trend reports ***
    st_bar.progress(0, f"(0%) Generating {topic} trend report (ver 1)")
    try:
        three_vers = st.session_state['steep_three_vers']
    except:
        in_message = ""
        
        for index, row in data.iterrows():
            if row[f"{topic}"] != "" :
                in_message += row["date"] + "\n" + row[f"{topic}"] + "\n"
            
        three_vers = {}
        
        for ver in range(0, 3):
            st_bar.progress(1/5 * (ver/3), f"({round(1/5 * (ver/3) * 100)}%) Generating {topic} trend report (ver {ver + 1})")
            
            chain = LlmManager.create_prompt_chain(PromptManager.STEEP.step2_prompt(topic, ver + 1),
                                                   st.session_state['model'])
            three_vers.update(LlmManager.llm_api_call(chain, in_message))
            
            time.sleep(3)

        st.session_state['steep_three_vers'] = three_vers
    # -------------------------------------------------------------------------------------

    # *** Aggregate three versions into one ***
    st_bar.progress(1/5, text = f"(20%) Aggregating three version {topic} trend report")
    try:
        trends_basic = st.session_state['steep_trends_basic']
    except:
        in_message = ""
        for ver, value in three_vers.items():
            in_message = in_message + '\n' + ver + '\n\n' + json.dumps(value) + '\n\n'

        chain = LlmManager.create_prompt_chain(PromptManager.STEEP.step3_prompt(topic),
                                               st.session_state['model'])
        trends_basic = LlmManager.llm_api_call(chain, in_message)

        st.session_state['steep_trends_basic'] = trends_basic
    # -------------------------------------------------------------------------------------

    # *** Classify representative events to corresponding trend ***
    st_bar.progress(2/5, text = f"(40%) Classifying events to each trend...")
    try:
        trends_with_events = st.session_state['steep_trends_with_events']
    except:
        events_message = ""
        for index, row in data.iterrows():
            if row[f"{topic}"] != "" :
                events_message += row["date"] + "\n" + row[f"{topic}"] + "\n"

        # classify events to each trend
        trends_with_events = []
        count = 1
        for name, trend in trends_basic.items():
            trend_message = json.dumps(trend)
            in_message = f'''
            總共有這些事件。請分類：\n\n{events_message}\n\n----\n\n*****主要趨勢{count}（{name}）*****：\n\n{trend_message}
            '''
            chain = LlmManager.create_prompt_chain(PromptManager.STEEP.step4_prompt,
                                                   st.session_state['model'])
            trends_with_events.append(LlmManager.llm_api_call(chain, in_message))
            st_bar.progress(2/5 + 1/5 * (count/len(trends_basic)), text = f"({round((2/5 + 1/5 * (count/len(trends_basic))) * 100)}%) Classifying events to each trend..." )
            count += 1

        st.session_state['steep_trends_with_events'] = trends_with_events
    # -------------------------------------------------------------------------------------
    
    # *** Inference ! 重頭戲 ***
    st_bar.progress(3/5, text = f"(60%) Inferring {topic} trend report...")
    try:
        trend_inference = st.session_state['steep_trend_inference']
    except:
        trend_inference = {}
        count = 1
        for trend in trends_with_events:
            in_message = json.dumps(trend)
            chain = LlmManager.create_prompt_chain(PromptManager.STEEP.step5_prompt,
                                                   st.session_state['model'])
            trend_inference.update(LlmManager.llm_api_call(chain, in_message))
            st_bar.progress(3/5 + 1/5 * (count/len(trends_with_events)), text = f"({round((3/5 + 1/5 * (count/len(trends_with_events))) * 100)}%) Inferring {topic} trend report..." )
            count += 1

        st.session_state['steep_trend_inference'] = trend_inference
    # -------------------------------------------------------------------------------------

    # *** Final summarization *** 
    st_bar.progress(4/5, text = f"(80%) Concluding {topic} trend report...")
    try:
        final_summary = st.session_state['steep_final_summary']
    except:
        in_message = ""
        for name, trend in trend_inference.items():
            message = f'''{name}: \n\n1. 趨勢洞察：\n{trend['<a>趨勢洞察']}\n\n2. 重要關係人：\n{trend['<d>重要關係人']}\n\n3. 缺口：{trend["<e>缺口"]}\n\n
            '''
            in_message += message
        
        chain = LlmManager.create_prompt_chain(PromptManager.STEEP.step6_prompt,
                                               st.session_state['model'])
        final_summary = LlmManager.llm_api_call(chain, in_message)
        st.write('''    🤝 Final summarization completed! ''')
        st_bar.progress(1, text = f"(100%) Complete!")
        st_bar.empty()
        st.session_state['steep_final_summary'] = final_summary
    # -------------------------------------------------------------------------------------
    
    result_json = DataManager.merge_dict(final_summary, trend_inference)
    encoded_json = base64.b64encode(json.dumps(result_json).encode('utf-8')).decode('utf-8')

    DataManager.post_files(file_name = f"{topic}_trend_report_{start_date}-{end_date}.json", 
                           file_content = encoded_json, 
                            expiration = str(dt.datetime.today() + dt.timedelta(90)), 
                            user_name = user_name, 
                            user_email = user_email)

    return result_json


def gen_trend_report_1(topic: str, start_date: str, end_date: str, user_name, user_email, data = None, daily_regen = False) -> json:

    # *** Try to import necessary data ***
    # if failed, generate by "monthly_summary()" function 
    if data is None:
        try:
            data = DataManager.b64_to_dataframe(DataManager.get_files(f"Summary_{start_date}-{end_date}.xlsx", 'xlsx'))  
        except:
            data = monthly_summary(start_date, end_date, user_name, user_email, daily_regen)
    # -------------------------------------------------------------------------------------
    st_bar = st.progress(0, text = f"({0}%) Generating {topic} trend report (three versions)...")
    # *** Generate three versions of trend reports ***
    st_bar.progress(0, f"(0%) Generating {topic} trend report (ver 1)")
    try:
        three_vers = st.session_state['steep_three_vers']
    except:
        in_message = ""
        
        for index, row in data.iterrows():
            if row[f"{topic}"] != "" :
                in_message += row["date"] + "\n" + row[f"{topic}"] + "\n"
            
        three_vers = {}
        
        for ver in range(0, 3):
            st_bar.progress(1/5 * (ver/3), f"({round(1/5 * (ver/3) * 100)}%) Generating {topic} trend report (ver {ver + 1})")
            chain = LlmManager.create_prompt_chain(PromptManager.STEEP.step2_prompt(topic, ver),
                                                   st.session_state['model'])
            three_vers.update(LlmManager.llm_api_call(chain, in_message))
            
            
            time.sleep(3)

        st.session_state['steep_three_vers'] = three_vers
    # -------------------------------------------------------------------------------------

    # *** Aggregate three versions into one ***
    st_bar.progress(1/5, text = f"(20%) Aggregating three version {topic} trend report")
    try:
        trends_basic = st.session_state['steep_trends_basic']
    except:
        in_message = ""
        for ver, value in three_vers.items():
            in_message = in_message + '\n' + ver + '\n\n' + json.dumps(value) + '\n\n'

        chain = LlmManager.create_prompt_chain(st.session_state['steep_prompt_3'],
                                               st.session_state['model'])
        
        trends_basic = LlmManager.llm_api_call(chain, in_message)

        st.session_state['steep_trends_basic'] = trends_basic
    # -------------------------------------------------------------------------------------

    # *** Classify representative events to corresponding trend ***
    st_bar.progress(2/5, text = f"(40%) Classifying events to each trend...")
    try:
        trends_with_events = st.session_state['steep_trends_with_events']
        st_bar.progress(3/5, text = f"(60%) Classified Events to Trends. Please Check & Proceed. (PAUSED)" )

    except:
        events_message = ""
        for index, row in data.iterrows():
            if row[f"{topic}"] != "" :
                events_message += row["date"] + "\n" + row[f"{topic}"] + "\n"

        # classify events to each trend
        trends_with_events = []
        count = 1
        for name, trend in trends_basic.items():
            trend_message = json.dumps(trend)
            in_message = f'''
            總共有這些事件。請分類：\n\n{events_message}\n\n----\n\n*****主要趨勢{count}（{name}）*****：\n\n{trend_message}
            '''
            chain = LlmManager.create_prompt_chain(st.session_state['steep_prompt_4'],
                                                   st.session_state['model'])
            trends_with_events.append(LlmManager.llm_api_call(chain, in_message))
            st_bar.progress(2/5 + 1/5 * (count/len(trends_basic)), text = f"({round((2/5 + 1/5 * (count/len(trends_basic))) * 100)}%) Classifying events to each trend..." )
            count += 1

        st_bar.progress(3/5, text = f"(60%) Classified Events to Trends. Please Check & Proceed. (PAUSED)" )
        st.session_state['steep_trends_with_events'] = trends_with_events
    # -------------------------------------------------------------------------------------

    

def gen_trend_report_2(topic: str, start_date: str, end_date: str, user_name, user_email, data = None, daily_regen = False) -> json:
    trends_with_events = st.session_state['steep_trends_with_events_modified']

    # *** Inference ! 重頭戲 ***
    st_bar = st.progress(3/5, text = f"(60%) Inferring {topic} trend report...")
    try:
        trend_inference = st.session_state['steep_trend_inference']
    except:
        trend_inference = {}
        count = 1
        for trend in trends_with_events:
            in_message = json.dumps(trend)
            chain = LlmManager.create_prompt_chain(st.session_state['steep_prompt_5'],
                                                   st.session_state['model'])
            trend_inference.update(LlmManager.llm_api_call(chain, in_message))
            st_bar.progress(3/5 + 1/5 * (count/len(trends_with_events)), text = f"({round((3/5 + 1/5 * (count/len(trends_with_events))) * 100)}%) Inferring {topic} trend report..." )
            count += 1

        st.session_state['steep_trend_inference'] = trend_inference
    # -------------------------------------------------------------------------------------

    # *** Final summarization *** 
    st_bar.progress(4/5, text = f"(80%) Concluding {topic} trend report...")
    try:
        final_summary = st.session_state['steep_final_summary']
        st_bar.progress(1, text = f"(100%) Complete!")
        st_bar.empty()
    except:
        in_message = ""
        for name, trend in trend_inference.items():
            message = f'''{name}: \n\n1. 趨勢洞察：\n{trend['<a>趨勢洞察']}\n\n2. 重要關係人：\n{trend['<d>重要關係人']}\n\n3. 缺口：{trend["<e>缺口"]}\n\n
            '''
            in_message += message
        
        chain = LlmManager.create_prompt_chain(st.session_state['steep_prompt_6'],
                                               st.session_state['model'])
        final_summary = LlmManager.llm_api_call(chain, in_message)
        st.write('''    🤝 Final summarization completed! ''')
        st_bar.progress(1, text = f"(100%) Complete!")
        st_bar.empty()
        st.session_state['steep_final_summary'] = final_summary
    # -------------------------------------------------------------------------------------
    
    result_json = DataManager.merge_dict(final_summary, trend_inference)
    encoded_json = base64.b64encode(json.dumps(result_json).encode('utf-8')).decode('utf-8')

    DataManager.post_files(file_name = f"{topic}_trend_report_{start_date}-{end_date}.json", 
                           file_content = encoded_json, 
                            expiration = str(dt.datetime.today() + dt.timedelta(90)), 
                            user_name = user_name, 
                            user_email = user_email)

    return result_json