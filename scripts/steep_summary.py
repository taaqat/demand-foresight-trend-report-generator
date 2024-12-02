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

def daily_summarize(in_message):

    chain = LlmManager.create_prompt_chain(sys_prompt = PromptManager.STEEP.step1_prompt)

    return LlmManager.llm_api_call(chain, in_message)

def monthly_summary(start_date: str, end_date: str,  user_name, user_email):

    # start = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
    # end = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
    start = start_date
    end = end_date
    now = start

    # Input end date should not be exceeding current time
    assert end <= dt.datetime.now().date(), "End date should not be later than today!"
    
    # Get the raw data by predefined api function
    try:
        month_raw = st.session_state['fetched_raw']
    except:
        month_raw = DataManager.fetch(start, end)
    
    month_out = {}
    
    st.write(f"Summarizing news within {start_date} to {end_date}...")
    max = (end - start).days
    counter = 0

    # *** Summarization ***
    # while loop to iterate over all days within the given period
    st_bar = st.progress(0, "Summarizing news within a given period...")            # progress bar on streamlit UI
    while now < end:
        st_bar.progress(counter/max, f"Summarizing news for {now}") # !!!

        # todo 這邊之後要改回來
        # first try to fetch the daily summary data from database
        try:
            response = DataManager.get_files(f"Daily_Summary_{now}.json", 'json') 
            month_out.update(json.loads(base64.b64decode(response)))

        # if objective file does not exist, create one with daily_summarize() and return it back to database
        except:
            in_message = DataManager.return_daily_raw_str(now, month_raw)
            response = daily_summarize(in_message)
            month_out.update(response)

            # Step 2: Convert JSON data to a string and then to bytes
            json_string = json.dumps(response)  # Convert JSON to a string
            json_bytes = json_string.encode('utf-8')  # Convert the string to bytes

            # Step 3: Encode the byte string to Base64
            encoded_json = base64.b64encode(json_bytes)

            # Step 4: Optionally, convert Base64 bytes to a string for easy storage
            encoded_json_str = encoded_json.decode('utf-8')


            DataManager.post_files(file_name = f"Daily_Summary_{now}.json", file_content = encoded_json_str, 
                        expiration = str(dt.datetime.today() + dt.timedelta(90)), user_name = user_name, user_email = user_email)
            
        now += dt.timedelta(days = 1)   # !!!
        counter += 1
    
    st_bar.empty()
    st.write("Summary Completed!!")

    # * transform the dictionary format into panda dataframe
    month_out = pd.DataFrame.from_dict(month_out, orient = 'index').reset_index()
    month_out.columns = ['date', 'social', 'technological', 'economic', 'environmental', 'political', 'business_and_investment']

    # * update info to steep database
    SessionManager.steep_database("update", start_date, end_date, "Summary", user_name, user_email, dt.date.today())

    # * store the monthly summary data in session state
    st.session_state['steep_summary'] = month_out

    # * post the file back to III database
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine = 'openpyxl') as writer:
        month_out.to_excel(writer, index=False, sheet_name='Sheet1')
    excel_buffer.seek(0)  # Move to the beginning of the buffer
    b64_excel = base64.b64encode(excel_buffer.read()).decode('utf-8')
    DataManager.post_files(f"Summary_{start}-{end}.xlsx",
                           b64_excel,
                           str(dt.datetime.today() + dt.timedelta(90)),
                           user_name,
                           user_email)
    return month_out