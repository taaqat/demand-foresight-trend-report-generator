from dotenv import dotenv_values                                   # read api key in .env file
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
#from langchain.schema import HumanMessage
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


if "debug_mode" not in st.session_state:
    st.session_state['debug_mode'] = False

class LlmManager:
    if 'KEY_verified' not in st.session_state:
        st.session_state['KEY_verified'] = False


    @staticmethod
    @st.dialog("請選擇欲使用的語言模型")
    def model_selection():

        model_selected = st.selectbox("請選擇欲使用的語言模型", ["claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219", "gpt-4o"])
        if st.button("確認"):
            st.session_state['model_type'] = model_selected
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
        elif st.session_state['model_type'] == 'gpt-4o':
            model = ChatOpenAI(model = 'gpt-4o',
                               api_key = OPENAI_KEY,
                               max_tokens = 16000,
                               temperature = 0.0,
                               verbose = True)
            return model
        
        else:
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
                       "gpt-4o": "OpenAI"}[model_selected]
        model_key = {"claude-3-7-sonnet-20250219": "CLAUDE_KEY",
                       "gpt-4o": "OPENAI_KEY"}[model_selected]

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

        in_message = in_message.strip()

        summary_json = ""                      # initialize output value

        # This function ensures the return value from LLM is complete
        def run_with_memory(chain, in_message, retry_count=0, max_retries=5) -> str:
            memory = ""
            
            try:
                response = chain.invoke({"input": in_message, "memory": memory})
                while response.usage_metadata["output_tokens"] >= 5000:
                    memory += response.content
                    response = chain.invoke({"input": in_message.strip() if isinstance(in_message, str) else "N/A", "memory": memory})
                memory += str(response.content)

                if st.session_state['debug_mode']:
                    st.write(memory)
                    
                return memory
            
            except Exception as e:
                # Exponential backoff: 5, 10, 20, 40, 80 seconds
                wait_time = 5 * (2 ** retry_count)
                
                if retry_count < max_retries:
                    st.warning(f"API call failed (attempt {retry_count + 1}/{max_retries + 1}): {str(e)}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    return run_with_memory(chain, in_message, retry_count + 1, max_retries)
                else:
                    st.error(f"API call failed after {max_retries + 1} attempts. Error: {str(e)}")
                    raise Exception(f"Claude API failed after {max_retries + 1} attempts: {str(e)}")
        
        try:
            summary_json = DataManager.find_json_object(run_with_memory(chain, in_message))
        except Exception as e:
            st.error(f"Initial API call failed completely: {str(e)}")
            summary_json = None
            
        if st.session_state['debug_mode']:
            st.write(summary_json)

        fail_count = 0
        max_retries = 10
        
        while (summary_json in ["null", "DecodeError", None]) and fail_count < max_retries:
            # Exponential backoff for retry attempts
            wait_time = 10 * (1.5 ** fail_count)  # 10, 15, 22.5, 33.75, 50.6... seconds
            st.warning(f"Invalid JSON response (attempt {fail_count + 1}/{max_retries}). Retrying with split strategy in {wait_time:.1f} seconds...")
            time.sleep(wait_time)

            try:
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
                
            except Exception as e:
                st.warning(f"Retry attempt {fail_count + 1} failed: {str(e)}")
                summary_json = None

            fail_count += 1

            if fail_count >= max_retries:
                error_msg = f"Claude model failed {max_retries} times during runtime. Please check your API key, rate limits, or try again later."
                st.error(error_msg)
                raise Exception(error_msg)

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
    

    











