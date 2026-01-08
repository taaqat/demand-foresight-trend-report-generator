import datetime
import calendar

# *** Feature Flags ***
FEATURE_FLAGS = {
    # 是否使用 LLMs 將 JSON 轉成 HTML（預設 False，使用直接轉換）
    'use_llms_convert_json_to_html': False
}

def generate_ym_mapping():
    """
    自動生成年月對照表，從2024年到當前年月
    """
    mapping = {}
    current_date = datetime.date.today()
    current_year = current_date.year
    current_month = current_date.month
    
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    # 生成2024年的資料（保留原有的圖片ID）
    pic_ids_2024 = [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]
    mapping['2024'] = {}
    for month_idx in range(12):
        month_name = month_names[month_idx]
        year = 2024
        month_num = month_idx + 1
        
        # 取得該月的最後一天
        last_day = calendar.monthrange(year, month_num)[1]
        
        # 特殊處理：9月的結束日期原本是10-01，11月是11-27
        if month_num == 9:
            end_date = f"{year}-10-01"
        elif month_num == 11:
            end_date = f"{year}-11-27"
        else:
            end_date = f"{year}-{month_num:02d}-{last_day}"
        
        mapping['2024'][month_name] = [
            f"{year}-{month_num:02d}-01",
            end_date,
            pic_ids_2024[month_idx]
        ]
    
    # 生成2025年至今的資料
    mapping['2025'] = {}
    end_year = current_year if current_year >= 2025 else 2025
    
    for year in range(2025, end_year + 1):
        year_key = str(year)
        if year_key not in mapping:
            mapping[year_key] = {}
        
        # 決定要生成到哪個月
        max_month = current_month if year == current_year else 12
        
        for month_idx in range(max_month):
            month_name = month_names[month_idx]
            month_num = month_idx + 1
            
            # 取得該月的最後一天
            last_day = calendar.monthrange(year, month_num)[1]
            
            mapping[year_key][month_name] = [
                f"{year}-{month_num:02d}-01",
                f"{year}-{month_num:02d}-{last_day}"
            ]
    
    return mapping

# 自動生成年月對照表
ym_mapping = generate_ym_mapping()