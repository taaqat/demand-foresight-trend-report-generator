import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SessionManager:

    @staticmethod
    def session_states_ls():
        for _ss_ in st.session_state:
            st.write(_ss_)

    # *** This function communicates with STEEP Google Sheet Database ***
    @staticmethod
    @st.cache_data
    def steep_database(method: str, 
                       start_date = None, 
                       end_date = None, 
                       topic = None, 
                       user_name = None, 
                       user_email = None, 
                       generated_date = None):
        
        assert method in ['fetch', 'update'], "parameter 'method' must be either 'fetch' or 'update'."

        if method == 'fetch':
            conn = st.connection("gsheets2", type = GSheetsConnection)
            df = conn.read(worksheet = '工作表1', ttl = 0)
            df['primary_key'] = df[['start_date', 'end_date', 'topic']].agg("_".join, axis = 1)
            st.session_state['gs_steep'] = df
            return df
        
        elif method == 'update':
            assert None not in [start_date, end_date, user_name, user_email, generated_date], "'update' method requires complete user inputs (start_date, end_date, ...)"
            conn = st.connection("gsheets2", type = GSheetsConnection)
            df = conn.read(worksheet = '工作表1', ttl = 0)

            if f"{start_date}_{end_date}_{topic}" not in (df['start_date'] + "_" + df['end_date'] + "_" + df['topic']).tolist():
                df_append = pd.DataFrame([{'start_date': start_date,
                        'end_date': end_date,
                        'topic': topic,
                        'user_name': user_name,
                        'user_email': user_email,
                        'generated_time': generated_date}])
                df_updated = conn.update(worksheet = '工作表1',
                                    data = pd.concat([df, df_append], ignore_index = True))
            else:
                df.loc[(df["start_date"] == start_date) & (df["end_date"] == end_date) & (df["topic"] == topic), :] = [start_date, end_date, topic, user_name, user_email, generated_date]
                df_updated = conn.update(worksheet = "工作表1", data = df)
    
    # *** This function communicates with Self Select Google Sheet Database ***
    @staticmethod
    def self_select_database(method: str, 
                             project_name = None, 
                             keywords = None, 
                             start_date = None, 
                             end_date = None, 
                             user_name = None, 
                             user_email = None, 
                             generated_date = None):
        assert method in ['fetch', 'update'], "parameter 'method' must be either 'fetch' or 'update'."

        if method == 'fetch':
            conn = st.connection("gsheets", type = GSheetsConnection)
            df = conn.read(worksheet = 'worksheet1', ttl = 0)
            df['primary_key'] = df[['project_name', 'start_date', 'end_date']].agg("_".join, axis = 1)
            st.session_state['gs_self_select'] = df
            return df
        
        elif method == 'update':
            assert None not in [project_name, keywords, start_date, end_date, user_name, user_email, generated_date], "'update' method requires complete user inputs (start_date, end_date, ...)"
        
            conn = st.connection("gsheets", type = GSheetsConnection)
            df = conn.read(worksheet = 'worksheet1', ttl = 0)
            df['primary_key'] = df[['project_name', 'start_date', 'end_date']].agg("_".join, axis = 1)
            st.session_state['gs_self_select'] = df

            df_to_append = pd.DataFrame(
                [{'project_name': project_name,
                'input_keywords': keywords,
                'start_date': start_date,
                'end_date': end_date,
                'user_name': user_name,
                'user_email': user_email,
                'generated_date': generated_date}])
            
            df_updated = conn.update(worksheet = 'worksheet1',
                            data = pd.concat([df.drop(columns = ['primary_key']), df_to_append], ignore_index = True))
            
    # *** This function return the list of authorized username from google sheet database ***
    # !!!! Not being used
    @staticmethod
    @st.cache_data
    def gs_auth_database():
        conn = st.connection("gsauth", type = GSheetsConnection)
        df = conn.read()
        return df

    # *** This function sends Notification Email to User's Address ***
    @staticmethod
    def send_notification_email(receiver_nickname, receiver_email, type):

        assert type in ['completed', 'failed'], "parameter 'type' should be one of ['completed', 'failed']"

        sender_email = "taaqat93@gmail.com"
        type_mapping = {"completed": """Your trend reports have been generated! Remember to download it from the page before the links disappear!
                                <br /><br />Sincerely,<br /><strong>III Trend Report Generator</strong>""",
                        "failed": """Something went wrong while running... Please go back to the page of Trend Report Generator and run it again!
                                <br /><br />Sincerely,<br /><strong>III Trend Report Generator</strong>"""}

        # * email_content *
        mail_content = f"""
        <!doctype html>
        <html>
        <head>
        <meta charset='utf-8'>
        <title>HTML mail</title>
        </head>
        <body>
            <p style="font-size:18px; "> 
            Dear {receiver_nickname}: <br /><br />
            {type_mapping[type]}</p>
        </body>
        </html>
        """

        # * Create email object *
        msg = MIMEMultipart()
        msg['From'] = "III demand-foresight trend report generator"
        msg['To'] = receiver_email
        msg['Subject'] = f"[III] Trend Reports {type.capitalize()}!"
        msg.attach(MIMEText(mail_content, 'html'))

        # SMTP Config
        smtp_server = "smtp.gmail.com"
        port = 587
        password = st.secrets['GMAIL_SENDER']  

        try:
            # 建立與伺服器的安全連線並發送電子郵件
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls()  # 開啟安全連接
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
                # print("Notification mail sent to your email address!")
        except Exception:
            st.warning(f"Failed to send the email: {Exception}")

    # *** This function cleans the intermediate output in session states ***
    @staticmethod
    def session_state_clear(page):
        assert page in ['steep', 'self-select'], "parameter 'page' should be either 'steep' or 'self-select'"

        if page == 'steep':
            ls = ['steep_three_vers', 'steep_trend_inference', 'steep_final_summary', 
                  'steep_trends_basic', 'steep_trends_with_events', 'steep_trends_with_events_modified']
            
        elif page == 'self-select':
            ls = ['self_select_three_vers', 'self_select_inference', 'self_select_final_summary', 
                  'self_select_trends_basic', 'self_select_trends_with_events']
            
        for key in ls:
            try:
                del st.session_state[key]
            except: 
                pass
    # *** function that return IP address for the deployed url
    @staticmethod
    def fetch_IP():
        response = requests.get("https://api.ipify.org?format=json")
        public_ip = response.json()["ip"]

        st.caption(f"Deployed IP Address: **:blue[{public_ip}]**")

    @staticmethod
    @st.dialog("Session States", width = 'large')
    def show_sessions():
        session_df = pd.DataFrame(columns = ['session', 'content'])
        for key, value in st.session_state.items():
            if key not in  ['CLAUDE_KEY', 'OPENAI_KEY', 'ym_mapping', 'gs_steep']:
                session_df.loc[len(session_df), ['session', 'content']] = [key, value]
        st.data_editor(session_df.sort_values('session').reset_index().drop('index', axis = 1),
                       width = 1000,
                       column_config = {
                           'session': st.column_config.TextColumn(
                               "Session Name",
                               disabled = True

                           ),
                           'content': st.column_config.Column(
                               "Session Value",
                               disabled = True
                           )
                       })