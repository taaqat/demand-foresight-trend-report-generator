class ModuleManager:

    import streamlit as st

    @staticmethod
    @st.cache_data
    def import_modules():
        import streamlit as st
        import pandas as pd
        import os
        import requests
        import datetime
        import json
        import datetime as dt
        import base64
        import time
        import re
        import sys
        import tqdm
        import time
        import openpyxl
        import io
        from io import BytesIO
        import base64
        from time import sleep

        # ** utils for export manager
        import collections 
        import collections.abc
        import subprocess
        from pptx import Presentation
        from pptx.util import Pt, Inches
        from pptx.enum.text import MSO_AUTO_SIZE
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN
        from pptx.enum.shapes import MSO_SHAPE
        try:
            from pptx import Presentation
        except ModuleNotFoundError:
            print("Module 'pptx' not found. Installing it now...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx"])
            from pptx import Presentation
            print("Module 'pptx' installed successfully.")

        # ** utils for sending emails
        import urllib3
        from urllib3.util.retry import Retry
        from requests.adapters import HTTPAdapter
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        import requests

        # ** utils for llm
        from dotenv import dotenv_values                          
        from langchain_anthropic import ChatAnthropic
        from langchain_core.prompts import ChatPromptTemplate

        # ** utils for GS connection
        from streamlit_gsheets import GSheetsConnection
        

        