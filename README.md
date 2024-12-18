# Demand Foresight Trend Report Generator
## Project Introduction

## Structures
```
/demand-foresight-trend-report-generator
├── README.md
├── index.py
├── managers
|  ├── data_manager.py
|  ├── export_manager.py
|  ├── llm_manager.py
|  ├── prompt_manager.py
|  └── session_manager.py
├── pages
|  ├── page_demo.py
|  ├── page_archive.py
|  ├── page_self_select.py
|  └── page_steep.py
├── requirements.txt
├── scripts
|  ├── executor.py
|  ├── self_select_generate.py
|  ├── self_select_summary.py
|  ├── steep_generate.py
|  └── steep_summary.py
├── pics
├── users.yaml
```

### index.py (entry point of the app)
This file serves as the application's entry point and is primarily responsible for the following three functions:

- User Authentication
- Introduction
- STEEP +B Trend Report Gallery

**NOTE**: If you want to update the gallery with the latest version (the latest month's trend report), you need to manually edit the start time, end time, and year-month in the Streamlit secret settings. To verify whether the trend report has been generated and to confirm the exact start and end dates for the month you want to update, you can check the ARCHIVE page.

### pages (front end)
Page files are python scripts that display UIs by streamlit, including:

#### page_demo.py:
This file demonstrates how to use the tool by youtube tutorial videos.

#### `page_steep.py`: 
This file displays the UI for STEEP trend report generation. User inputs include **nickname, email, desired period, topics, and output formats**. With such information, user can obtain trend reports in desired output format within 1 hour.

#### `page_self_select.py`:
This file displays the UI for SELF SELECT trend report generation. In addition to the basic user inputs, user should also name the generation session with a consice project name. 

First, user filters desired raw news data by **querying III database with keyword boolean combination**. User would be informed with the queried raw news data and then decide whether proceed or redo the query step.

Then, if user decided to proceed, the page that asks user to input options would be shown. Aside from output format, more customizable options are provided, including **desired analysis columns** and **theme color** of pptx slide.

Subsequent process of generation is basically the same with STEEP page.

#### `page_archive.py`:

This page allows user to query the generated output files by project name. The following five types of data are provided:

- Trend reports in PPTX format
- Trend reports in EXCEL format
- Trend reports in JSON format (utf-8 encoded)
- Monthly summary data in EXCEL format
- Daily summary data in JSON format (utf-8 encoded)

#### `index.py`:
This page is the entrance of our application. It manages user login and the navigation across the three pages as mentioned above.

### managers (back end)
This folder includes five python files for specific utilities. In each file, a class that has identical name with file name is established, with several tool functions defined by static method. 

#### `data_manager.py` -> `DataManager`

This file defines functions that associate with **data manipulation**, **data transformation** and **III database API calling**.

- Functions that interact with III database:
    
    - `fetch()`: Fetch processed news data from III database by keywords and date.

    - `post_files()`: Post completed files back to III database

    - `get_files()`: Get generated files from III database

- Functions for data transformation and manipulation:

    - `return_daily_raw_str()`: Convert the daily raw data from pd.DataFrame to string

    - `find_json_object()`: Find JSON object from a string (Used with `LlmManager.llm_api_call()`)

    - `merge_dict()`: Merge two dictionaries.

    - `b64_to_dataframe()`: Transform Base64 formatted spreadsheet to pd.Dataframe

    - `get_output_download_link()`: Return a HTML-like string object (to be rendered on UI with `st.markdown()`). 

    - `get_summary_download_link()`: Return a HTML-like string object (to be rendered on UI with `st.markdown()`). 

#### `export_manager.py` -> `ExportManager`

This file defines functions that associate with **data export**. Functions that convert JSON formatted AI response to EXCEL and PPTX are defined under this class. Two principal functions, `create_excel()` and `create_pptx()` are defined under both two sub-classes, `STEEP` and `SELF_SELECT`, as these two generators have different output format.

- `get_report_excels()`: Transform the JSON formatted output into `pd.DataFrame`.

- `create_pptx()`: Return a Base64 string of pptx formatted trend report (to be used together with `DataManager.post_data()`.)

- `create_excel()`: Return a Base64 string of xlsx formatted trend report (to be used together with `DataManager.post_data()`.)

#### `llm_manager.py` -> `LlmManager`

This file manages everything associated with LLM API call. We use Claude as our model.

- `llm_api_call()`: Call Claude API and return JSON formatted response. Parameter `chain` should be passed in as **LangChain runnable**  object that contains system prompt (which can be obtained by `LlmManager.create_prompt_chain()` function), and parameter `in_message` (user prompt in string format) should be passed in as well.

- `create_prompt_chain()`: Return a **LangChain runnable** object with system prompt (to be used in `LlmManager.llm_api_call()`). Parameter `sys_prompt` (system prompt) should be passed in.

#### `llm_manager.py` -> `LlmManager`

This file manages everything associated with LLM API call. We use Claude as our model.

- `llm_api_call()`: Call Claude API and return JSON formatted response. Parameter `chain` should be passed in as **LangChain runnable**  object that contains system prompt (which can be obtained by `LlmManager.create_prompt_chain()` function), and parameter `in_message` (user prompt in string format) should be passed in as well.

- `create_prompt_chain()`: Return a **LangChain runnable** object with system prompt (to be used in `LlmManager.llm_api_call()`). Parameter `sys_prompt` (system prompt) should be passed in.

#### `prompt_manager.py` -> `PromptManager`

This file manages all system prompts to be used. There are two subclasses, `STEEP` and `SELF_SELECT`, under which system prompts for all steps are defined.

#### `session_manager.py` -> `SessionManager`

This file manages functions associated with **st.session_state** management and **google sheet database connection, access and update**

- `steep_database()`: Fetch data from or update data to google sheet that stores all generation history of STEEP page.

- `self_select_database()`: Fetch data from or update data to google sheet that stores all generation history of SELF_SELECT page.

- `send_notification_email()`: Automatically send notification email while error occurs or while generation process is completed.

- `session_state_clear()`: Clear the session states based on the page parameter passed in.


### scripts (back end) 
This folders include five python scripts that control the workflow of trend report generation process.

#### `steep_summary.py`
- `monthly_summary()`: Summarize all news by **day** within specified period, and return in pd.DataFrame object with date as index, each STEEP theme as columns, and news summary as value. This function does not require raw data as parameter because it is nested by `DataManager.fetch()` function.

#### `steep_generate.py`
- `gen_trend_report()`: Generate trend report and return in JSON format based on specified topic and time period. 

#### `self_select_summary.py`
- `monthly_summary()`: Summarize filtered news by **group** within specified period, and return in pd.DataFrame object with date as index and news summary as value. Due to the session issue, this function requires raw data as parameter. (We let users confirm the result of raw data query, then proceed to the summary prosedure.)

#### `self_select_generate.py`
- `gen_trend_report()`: Generate trend report and return in JSON format based on the specified summary data. 

#### `executor.py`
This file links functions from the four python script files as mentioned above, serving as the interface that connects UI and back-end design. Specifically, `Executor` class has methods that receive user input, generate trend reports, export as pptx slides and excel, post the output files back to III database, update the generation history to google sheet database, send notification emails, and finally clear all related session state variables in progress. 

- `steep_run()`: Executor function fo STEEP page.
- `self_select_run()`: Executor function fo SELF SELECT page.