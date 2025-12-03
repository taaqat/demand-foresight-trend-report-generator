from dotenv import dotenv_values                                   # read api key in .env file
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# from langchain.schema import HumanMessage
from langchain_core.messages import HumanMessage
import streamlit as st
import json
import time
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection

from .data_manager import DataManager


# Read in environmental variables at local (API keys)
# config = dotenv_values('.env')
# CLAUDE_KEY = config['CLAUDE_KEY']
# OPENAI_KEY = config['OPENAI_KEY']
# *** Read in API key at Streamlit (by streamlit.secrets) ***

class LlmManager:
    if 'KEY_verified' not in st.session_state:
        st.session_state['KEY_verified'] = False


    @staticmethod
    @st.dialog("請選擇欲使用的語言模型")
    def model_selection():
        st.subheader("模型配置選項")
        
        use_same = st.radio(
            "選擇模型配置方式",
            ["分析與報表使用同一模型", "分析與報表使用不同模型"],
            index=0
        )
        
        if use_same == "分析與報表使用同一模型":
            model_selected = st.selectbox(
                "請選擇欲使用的語言模型", 
                ["claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219", "gpt-5.1"]
            )
            if st.button("確認"):
                st.session_state['use_same_model'] = True
                st.session_state['analysis_model_type'] = model_selected
                st.session_state['report_model_type'] = model_selected
                st.session_state['model_type'] = model_selected  # 保留向後兼容
                st.rerun()
        else:
            analysis_model = st.selectbox(
                "分析使用的模型",
                ["claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219", "gpt-5.1"],
                key="analysis_model_select"
            )
            report_model = st.selectbox(
                "報表生成使用的模型",
                ["claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219", "gpt-5.1"],
                key="report_model_select"
            )
            if st.button("確認"):
                st.session_state['use_same_model'] = False
                st.session_state['analysis_model_type'] = analysis_model
                st.session_state['report_model_type'] = report_model
                st.session_state['model_type'] = analysis_model  # 預設使用分析模型
                st.rerun()
    

    # * initialize model
    @staticmethod
    def init_model():
        CLAUDE_KEY = st.session_state['CLAUDE_KEY']
        OPENAI_KEY = st.session_state['OPENAI_KEY']
       
        
        if st.session_state['model_type'] == 'claude-3-7-sonnet-20250219':
            model = ChatAnthropic(model = 'claude-3-7-sonnet-20250219',
                                    api_key = CLAUDE_KEY,
                                    max_tokens = 8000,
                                    temperature = 0.0,
                                    verbose = True
                                    )
            return model
        elif st.session_state['model_type'] == 'claude-sonnet-4-20250514':
            model = ChatAnthropic(model = 'claude-sonnet-4-20250514',
                                    api_key = CLAUDE_KEY,
                                    max_tokens = 8000,
                                    temperature = 0.0,
                                    verbose = True
                                    )
            return model
        elif st.session_state['model_type'] == 'gpt-5.1':
            model = ChatOpenAI(model = 'gpt-5.1',
                               api_key = OPENAI_KEY,
                               max_tokens = 16000,
                               temperature = 0.0,
                               verbose = True)
            return model
        
        else:
            return None
    
    # * initialize analysis model
    @staticmethod
    def init_analysis_model():
        CLAUDE_KEY = st.session_state['CLAUDE_KEY']
        OPENAI_KEY = st.session_state['OPENAI_KEY']
        model_type = st.session_state.get('analysis_model_type', st.session_state.get('model_type', ''))
        
        if model_type == 'claude-3-7-sonnet-20250219':
            return ChatAnthropic(
                model='claude-3-7-sonnet-20250219',
                api_key=CLAUDE_KEY,
                max_tokens=8000,
                temperature=0.0,
                verbose=True
            )
        elif model_type == 'claude-sonnet-4-20250514':
            return ChatAnthropic(
                model='claude-sonnet-4-20250514',
                api_key=CLAUDE_KEY,
                max_tokens=8000,
                temperature=0.0,
                verbose=True
            )
        elif model_type == 'gpt-5.1':
            return ChatOpenAI(
                model='gpt-5.1',
                api_key=OPENAI_KEY,
                max_tokens=16000,
                temperature=0.0,
                verbose=True
            )
        return None
    
    # * initialize report model
    @staticmethod
    def init_report_model():
        CLAUDE_KEY = st.session_state['CLAUDE_KEY']
        OPENAI_KEY = st.session_state['OPENAI_KEY']
        model_type = st.session_state.get('report_model_type', st.session_state.get('model_type', ''))
        
        if model_type == 'claude-3-7-sonnet-20250219':
            return ChatAnthropic(
                model='claude-3-7-sonnet-20250219',
                api_key=CLAUDE_KEY,
                max_tokens=8000,
                temperature=0.0,
                verbose=True
            )
        elif model_type == 'claude-sonnet-4-20250514':
            return ChatAnthropic(
                model='claude-sonnet-4-20250514',
                api_key=CLAUDE_KEY,
                max_tokens=8000,
                temperature=0.0,
                verbose=True
            )
        elif model_type == 'gpt-5.1':
            return ChatOpenAI(
                model='gpt-5.1',
                api_key=OPENAI_KEY,
                max_tokens=16000,
                temperature=0.0,
                verbose=True
            )
        return None
    
    # * test if the api key is valid
    @staticmethod
    def api_key_verify(model):
        response = model([HumanMessage(content = "Hello, how are you?")])
        st.session_state['KEY_verified'] = True
        return response

    @staticmethod
    @st.dialog("請輸入您的 API Key")
    def customize_token(model_selected):

        model_alias = {"claude-3-7-sonnet-20250219": "Claude_3.7",
                       "gpt-5.1": "OpenAI"}[model_selected]
        model_key = {"claude-3-7-sonnet-20250219": "CLAUDE_KEY",
                       "gpt-5.1": "OPENAI_KEY"}[model_selected]

        tk = st.text_input(f"請輸入您的 {model_alias} API Key")
        if st.button("確認"):
            st.session_state[model_key] = tk
            with st.spinner("Verifying API key..."):
                try:
                    st.session_state['model'] = LlmManager.init_model()
                    LlmManager.api_key_verify(st.session_state['model'])
                    st.rerun()

                except Exception as e:
                    st.warning("Invalid API key")
            

    # Implement Anthropic API call 
    # *** input: chain(prompt | model), in_message(str) ***
    # *** output: json ***
    @staticmethod
    def llm_api_call(chain, in_message):

        summary_json = ""                      # initialize output value

        # This function ensures the return value from LLM is complete
        def run_with_memory(chain, in_message) -> str:
            memory = ""

            if not in_message or in_message.strip() == "":
                return "Error: Empty input message"
            
            response = chain.invoke({"input": in_message, "memory": memory})
            while response.usage_metadata["output_tokens"] >= 5000:
                memory += response.content
                response = chain.invoke({"input": in_message, "memory": memory})
            memory += str(response.content)
            return memory
        
        summary_json = DataManager.find_json_object(run_with_memory(chain, in_message))
        # st.write(summary_json)

        fail_count = 0
        while (summary_json in ["null", "DecodeError", None]):
            # While encountering error, first let Claude rest for 10 secs
            time.sleep(10)

            memory = ""

            cutting_points = [i * (len(in_message) // 2) for i in range(1, 2)]
            intermediate = [
                run_with_memory(chain, in_message[:cutting_points[0]]),
                run_with_memory(chain, in_message[cutting_points[0]:])
            ]

            response = chain.invoke({"input": "\n\n".join(intermediate), "memory": memory})
            while response.usage_metadata["output_tokens"] >= 5000:
                memory += response.content
                response = chain.invoke({"input": "\n\n".join(intermediate), "memory": memory})
            memory += str(response.content)
            summary_json = DataManager.find_json_object(memory)

            fail_count += 1

            if fail_count == 10:
                print("Claude model crushed more than 10 times during runtime. Please consider re-running...")

        return summary_json
        
    @staticmethod
    def create_prompt_chain(sys_prompt, model):

        # *** Create the Prompt ***
        prompt_obj = ChatPromptTemplate.from_messages(
            [
                ("system", sys_prompt),
                ("human", "{input}"),
                ("assistant", "{memory}")
            ]
        )

        # *** Create LLM Chain ***
        chain = prompt_obj | model

        return chain
    

    











