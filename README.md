# STEEP + B Trend Report Automatic AI Generator
## Project Introduction

## Files
#### `main_code.py`
This file is the main program of our project. When we call the main function in this file, the whole process starts by connecting several functions in our project folder. 
#### `origin.py`
This file is where we import AI models and read in the API key from environment. 
1. `recursiveCallLLM(chain, in_messege: str) -> dict (json)`:
    This function takes **Prompt Chain** object in `langchain-anthropic` module as the first parameter.(`chain = system_prompt | model`)
    The second parameter is the user input prompt (the data that we want AI model to process for us).

    We store the return in `memory` varialbe to avoid too long output token. If the output token still exceeds the limit, we split the input message into two parts, deal with them separately, and then take the return values of the two iterations as input to form the complete return.

    It returns a json object data.

#### `prompt.py`
This file stores the **systematic** prompt for each step.

#### `s0_data_processing.py`
This file defines functions that obtain necessary data, clean and transform data, and allow other convenient data manipulation.

1. `fetch(start_date: str, end_date: str) -> pd.DataFrame`:
    This function fetches daily news that was scraped by the engineer in our team in advanced by using the API of the data base of our team. The function returns a pd.DataFrame object.

2. `return_daily_raw_str(day: str, data: pd.DataFrame) -> str`:
    As the LLM only takes "string" format data, we have to transform daily data into a long string. This function return the daily news data for a specific day in string format (so that we can use the return value to ask LLM to do summarization for us.)

3. `find_json_object(str) -> dict (json)`:
    This function finds the largest json object in the input string.

4. `gen_output_dir()`:
    This function generates the folder for storing output files.

5. `merge_dict(dict, dict) -> dict`:
    This function merges two dictionaries into one.

#### `s1_generate_monthly_summary.py`
This file defines two functions that generate the monthly summary from the raw input.

1. `daily_summarize(model: langchain model object, in_messege: str) -> dict (return by recursiveCallLLM())`:
    This function forms a prompt pipeline that connects the prompt that summarizes daily news with the model, and return the daily summary data in json format.

2. `monthly_summary(start_date: str, end_date: str, summary_output: bool) -> pd.DataFrame`:
    This function generates the pd.DataFrame object of monthly summary (not necessarily monthly. could be any time period.) by:
    
    - Gets all raw data with `fetch(start_date, end_date` function.
    - Run `daily_summarize()` for each day, and then return a cleaned dataframe with row = date, column = topic.

#### `s2_generate_trend_report.py`
This file defines the function that generates trend report by a series of prompt chains.
1. `gen_trend_report(topic: str, start_date: str, end_date: str, data = None) -> dict (json)`:
    This function is composed of a long prompt chain. It generates the final trend report for each topic. 

    - Check if the monthly summary data exists. If not, create the monthly summary data by `monthly_summary()` function.
    - Aggregate the summary data on topic across days, and ask AI model to create three versions of trend reports for us.
    - Ask AI to merge the three versions.
    - Classify representative events to corresponding trend.
    - Ask AI to do the inference part.
    - Final summarization -> json object (-> power point, excel)