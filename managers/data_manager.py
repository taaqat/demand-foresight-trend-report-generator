import requests
import pandas as pd
import datetime
import json
import os
import streamlit as st
import datetime as dt
import base64
import time
import re
from pypdf import PdfReader
from time import sleep

import urllib3
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
from io import BytesIO

# from module_manager import ModuleManager
# ModuleManager.import_modules()


# from contextlib import contextmanager, redirect_stdout


class DataManager:
    
    # *************************************************
    # *** Functions that interact with III database ***

    # --- Fetch processed news data from III database 
    #     by keywords and date
    @staticmethod
    def fetch(
        start_date, 
        end_date, 
        output_format = 'fulltext', 
        keywords = None, 
        search_scope = 'title,content',
        debug = False, 
        show_titles = False,
        ):

        url = 'http://61.64.60.30/news-crawler/api/news_summary/?'

        headers = {
            'Authorization': st.secrets['III_KEY']
        }

        result_dfs = []


        # *** Set up retries for the connection ***
        retry_strategy = Retry(
            total=3,  # Number of retries
            status_forcelist=[429, 500, 502, 503, 504]  # Retry on these status codes
        )

        adapter = HTTPAdapter(max_retries = retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)
            
        # *** Fetching data recursively until return ***
        st.write(f'Fetching daily news data from {start_date} to {end_date}...')

        # *** First check if there is keywords input
        if keywords != None:
            keywords = keywords.split("\n")

            # *** 自選主題（允許使用者自定義關鍵字）：捨棄公司資料庫布林邏輯算法。對每個關鍵字跑一次 fetch 再將最後的 dataframe 去除重複列，也可以達成一樣效果，但效能快很多。
            for keyword in keywords:
                dfs = []
                page = 1
                while True:
        
                    end_point_params = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'output_format': output_format,
                    'search_scope': search_scope,
                    'boolean_or_separator': '|',
                    'page': page,
                    'keyword': keyword}

                    # Debug 部份（看送出的 url）
                    if debug == True:
                        request = requests.Request('POST', url, params = end_point_params, headers = headers)
                        prepared_request = http.prepare_request(request)
                        st.write(f"URL: {prepared_request.url}")
                    
                    try:
                        response = http.post(url, end_point_params, headers = headers, timeout=30)
                    except (urllib3.exceptions.NewConnectionError, 
                            requests.exceptions.ConnectionError,
                            requests.exceptions.Timeout) as e:
                        st.error(f"Connection failed: {e}")
                        st.warning("Retrying connection...")
                        continue
                    except Exception as e:
                        st.error(f"Unexpected error during request: {e}")
                        break
                    
                    # PRINT HTTPS Error Messege if we encounter errors
                    if response.status_code == 200:
                        pass 
                    else:
                        st.warning(f"HTTP Error {response.status_code}: {response.content}")
                        if response.status_code >= 500:
                            st.warning("Server error, retrying...")
                            continue

                    # Clean data into pd.DataFrame format
                    data = response.json()['data']

                    df = pd.DataFrame(data)
                    dfs.append(df)

                    # 使用者可以檢查搜尋到的前幾筆資料標題
                    if show_titles & (not df.empty):
                        st.write(df.iloc[0:3,:].title)

                    if data == []:
                        break

                    page += 1

                keyword_df = pd.concat(dfs)
                result_dfs.append(keyword_df)

        # *** 不允許使用者輸入關鍵字 -> 一般的 STEEP 頁面的 fetch（擷取特定時間段內的所有新聞）
        else:
            page = 1
            while True:
                # Keywords 使用者用換行分隔代表 OR，不過 https POST 時要記得改成用 pipeline 符號

                end_point_params = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'search_scope': search_scope,
                    'output_format': output_format,
                    'page': page}

                # Debug 部份（看送出的 url）
                if debug == True:
                    request = requests.Request('POST', url, params = end_point_params, headers = headers)
                    prepared_request = http.prepare_request(request)
                    st.write(f"URL: {prepared_request.url}")
                
                try:
                    response = http.post(url, end_point_params, headers = headers, timeout=30)
                except (urllib3.exceptions.NewConnectionError, 
                        requests.exceptions.ConnectionError,
                        requests.exceptions.Timeout) as e:
                    st.error(f"Connection failed: {e}")
                    st.warning("Retrying connection...")
                    continue
                except Exception as e:
                    st.error(f"Unexpected error during request: {e}")
                    break
                
                # PRINT HTTPS Error Messege if we encounter errors
                if response.status_code == 200:
                    pass 
                else:
                    st.warning(f"HTTP Error {response.status_code}: {response.content}")
                    if response.status_code >= 500:
                        st.warning("Server error, retrying...")
                        continue

                # Clean data into pd.DataFrame format
                data = response.json()['data']

                df = pd.DataFrame(data)
                result_dfs.append(df)

                # 使用者可以檢查搜尋到的前幾筆資料標題
                if show_titles & (not df.empty):
                    st.write(df.iloc[0:3,:].title)

                if data == []:
                    break

                page += 1
        
        # Concatenate all dataframes from all pages 
        result_df = pd.concat(result_dfs)
        # result_df = result_df.drop_duplicates(subset = ['title'])

        # Transform the publish time column to datetime 
        result_df['published_at'] = pd.to_datetime(result_df['published_at'])

        st.write(f"All required data collected. {len(result_df)} rows in total.")

        st.session_state['fetched_raw'] = result_df

        return result_df

    # --- Post completed files back to III database
    @staticmethod
    def post_files(
            file_name, 
            file_content, 
            expiration, 
            user_name, 
            user_email
            ):

        # form_values = '{"name": "%s", "email": %s"}'%(user_name, user_email)
        # print(form_values)
        url = 'http://61.64.60.30/news-crawler/api/file/?'

        headers = {
            'Authorization': st.secrets['III_KEY']
        }

        payload = {
            'file_name': file_name,
            'file_content': file_content,
            'expire_at': expiration,
            'form_values': {'name': user_name, 'email': user_email}
            }

        # *** Set up retries for the connection ***
        retry_strategy = Retry(
            total = 3,  # Number of retries
            status_forcelist = [429, 500, 502, 503, 504]  # Retry on these status codes
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter) 
        try:
            response = http.post(url, json = payload, headers = headers)
            st.info(f"File {json.loads(response.content)['file_name']} has been updated to III's database")
        except Exception as e:
            response = http.post(url, json = payload, headers = headers)

        return response
    

    # --- Get generated files from III database
    @staticmethod
    def get_files(
        filename, 
        ext):

        assert ext in ['pptx', 'xlsx', 'json', 'txt'], "Parameter 'ext' must be one of the following: ['pptx', 'xlsx', 'json', 'txt']"
        
        url = 'http://61.64.60.30/news-crawler/api/file/?'
        
        headers = {
            'Authorization': st.secrets['III_KEY']
        }

        end_point_params = {
            'file_name': filename
        }

        response = requests.get(url, params = end_point_params, headers = headers)
        
        if ext in ['pptx', 'xlsx', 'json']:
            try:
                response_b64 = response.json()['file_content']
                return response_b64
            except:
                raise ValueError("No such file in the database!")
        else:
            try:
                return response.json()['file_content']
            except Exception as e:
                # st.write(e)
                raise ValueError("No such file in the database!")
        
    # *****************************************
    # *** Functions for data transformation ***
        
    # --- Map the daily raw data from pd.DataFrame to string
    @staticmethod
    def return_daily_raw_str(
        day: str, 
        data: pd.DataFrame
        ) -> str:

        contents = []
        if type(day) == str:
            date = datetime.datetime.strptime(day, "%Y-%m-%d").date()
        else:
            date = day



        for index, row in data.iterrows():
            # print(f"Row {index}: date={row['date']}, 重點摘要={row['重點摘要']}, 關鍵數據={row['關鍵數據']}")
            if row["重點摘要"] not in ["", " ", None] and row["published_at"].date() == date:
                contents.append(row["重點摘要"] + "\n" + str(row["關鍵數據"]))
                
                if index % 10 == 0:
                    contents.append("\n" + str(date) + "\n")
        content = "\n" + f"**{str(date)}**'s news" + "\n\n" +"\n\n".join(contents) + "\n\n" + "*"*100

        return content

    # @staticmethod
    # def find_json_object(input_string):
    #     start_index = input_string.find('{')
    #     end_index = input_string.rfind('}')

    #     if start_index != -1 and end_index != -1:
    #         json_string = input_string[start_index:end_index+1]
    #         try:
    #             json_object = json.loads(json_string)
    #             return json_object
    #         except json.JSONDecodeError:
    #             return "DecodeError"

    #     return None

    # --- Find JSON object from a string 
    #     (Used with LlmManager.llm_api_call())
    @staticmethod
    def find_json_object(input_string):
        # Match JSON-like patterns
        input_string = input_string.replace("\n", '').strip()
        input_string = input_string.encode("utf-8").decode("utf-8")
        start_index = input_string.find('{')
        end_index = input_string.rfind('}')

        if start_index != -1 and end_index != -1:
            json_string = input_string[start_index:end_index+1]
            try:
                json_object = json.loads(json_string)
                return json_object
            except json.JSONDecodeError:
                return "DecodeError"
        # st.write(json_string)

        return None  # Return None if no valid JSON is found

# def gen_output_dir():
#     dir_name = f'output'
#     # current_directory = os.path.dirname(os.path.abspath(__file__))
#     # directory_path = os.path.join(current_directory, dir_name)

#     try:
#         os.makedirs(dir_name, exist_ok=True)
#     except OSError as e:
#         print(f"Error creating directory: {e}")

# gen_output_dir()

    # --- Merge two dicts to one
    @staticmethod
    def merge_dict(dict1, dict2):
        return {**dict1, **dict2}
    
    # --- Transform Base64 formatted spreadsheet to pd.Dataframe
    @staticmethod
    def b64_to_dataframe(b64_str):
        try:
            data = base64.b64decode(b64_str)
            data = BytesIO(data)
            data = pd.read_excel(data)
            data.fillna('', inplace=True)

            return data
        except:
            raise UnicodeDecodeError("Encountered Errors while tranforming base64 to dataframe. Please ensure the original data format to be 'xlsx'.")
        
    # --- Transform Base64 formatted pptx to proper Power point BytesIO format
    @staticmethod
    def b64_to_pptx_IO(b64_str):
        try:
            data = base64.b64decode(b64_str)
            data = BytesIO(data)

            return data
        except:
            raise UnicodeDecodeError("Encountered Errors while tranforming base64 to dataframe. Please ensure the original data format to be 'pptx'.")
        
    # --- Transform Base64 formatted json to Json format data
    @staticmethod
    def b64_to_json(b64_str):
        try:
            data = base64.b64decode(b64_str)
            data = json.loads(data)

            return data
        except:
            raise UnicodeDecodeError("Encountered Errors while tranforming base64 to dataframe. Please ensure the original data format to be 'pptx'.")
            

    # --- Get output download link (to render on UI with st.markdown())
    @staticmethod
    def get_output_download_link(start_date, end_date, topic, ext, page):
        
        assert ext in ['pptx', 'xlsx', 'json'], "Parameter 'ext' must be one of the following: ['pptx', 'xlsx', 'json']"

        mapping = {
            "steep": {
                "pptx": {
                    "filename": f"{topic}_trends_{start_date}-{end_date}.pptx",
                    "type": "vnd.openxmlformats-officedocument.presentationml.presentation",
                    "text": f"Download the {topic} trend report from {start_date} to {end_date} (Pptx Slides)"
                },
                "xlsx": {
                    "filename": f"{start_date}-{end_date}_STEEP.xlsx",
                    "type": "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "text": f"Download trend reports from {start_date} to {end_date} (Excel)"
                },
                "json": {
                    "filename": f"{topic}_trend_report_{start_date}-{end_date}.json",
                    "type": "json",
                    "text": f"Download {topic} trend report from {start_date} to {end_date} (JSON)"
                }
            },
            "self_select": {
                "pptx": {
                    "filename": f"{topic.replace(' ', '_')}_trends_{start_date}-{end_date}.pptx",
                    "type": "vnd.openxmlformats-officedocument.presentationml.presentation",
                    "text": f"Download the {topic} trend report from {start_date} to {end_date} (Pptx Slides)"
                },
                "xlsx": {
                    "filename": f"{topic.replace(' ', '_')}_{start_date}-{end_date}_trend_report.xlsx",
                    "type": "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "text": f"Download trend reports from {start_date} to {end_date} (Excel)"
                },
                "json": {
                    "filename": f"{topic}_trend_report_{start_date}-{end_date}.json",
                    "type": "json",
                    "text": f"Download {topic} trend report from {start_date} to {end_date} (JSON)"
                }
            }   
        }


        content_b64 = DataManager.get_files(mapping[page][ext]['filename'], ext)
        comps = (mapping[page][ext]['type'], mapping[page][ext]['filename'], mapping[page][ext]['text'])
        return f'<a href = "data:application/{comps[0]};base64,{content_b64}" download = "{comps[1]}"> {comps[2]}</a>'
    
    # --- Get summary output download link (to render on UI with st.markdown())
    @staticmethod
    def get_summary_download_link(start_date, end_date, topic = None):
        if topic:
            content_b64 = DataManager.get_files(f"Summary_{topic}_{start_date}-{end_date}.xlsx", 'xlsx')
            filename = f"Summary_{topic}_{start_date}-{end_date}.xlsx"
        else:
            content_b64 = DataManager.get_files(f"Summary_{start_date}-{end_date}.xlsx", 'xlsx')
            filename = f"Summary_{start_date}-{end_date}.xlsx"

        return f'<a href = "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{content_b64}" download = {filename}> Download Summary Data </a>'
        
    # --- Transform Picture to Base64
    @staticmethod
    def image_to_b64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    

    # --- Load user uploaded data
    @staticmethod
    @st.cache_data
    def load_news(uploaded):

        '''load news data from user upload with caching'''
        if uploaded is not None:
            try:
                return pd.read_csv(uploaded)
            except:
                return pd.read_excel(uploaded)
                    
        else:
            return None
        
    # --- Load user uploaded pdf data
    def load_pdfs(uploaded):

        '''load pdf data from user upload with caching'''
        reader = PdfReader(uploaded)
        number_of_pages = len(reader.pages)
        texts = []
        for i in range(number_of_pages):
            page = reader.pages[i]
            texts.append(f"【page {i}】\n" + page.extract_text())

        return texts
     