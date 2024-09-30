import pandas as pd
from os import listdir
from os.path import isfile, join
from datetime import datetime
folder_path = r"dataset\download"
record_file = r"dataset\download\record.txt"
def check_code_range(file='6125_history_news.csv'):
    code = file.split('_')[0]
    print(f"file is {join(folder_path,file)}")
    file = join(folder_path,file)
    try:
        df = pd.read_csv(file)
        date = df.loc[:,'date'].tolist()
        print(f"from {date[0]} ~ {date[-1]}")
        last_date = datetime.strptime(date[-1], "%Y-%m-%d %H:%M:%S")
        if last_date > datetime(2024, 8, 1):
            return code
    except FileNotFoundError:
        print(f"This file: {file} does not exist")
    except Exception as e:
        print(f"An error occurred while processing {file}: {str(e)}")
    
    print()
    
def record(codes):
    print(codes)
    codes = ','.join(codes)
    print(f"record codes is {codes}")
    with open(record_file, "w") as f:
        f.write(codes)
def read_record():
    with open(record_file, "r") as f:
        records = f.read().split(',')
    return records


def need_to_download_company():
    """ 
        回傳下載目標還未達標的關係企業
    """
    record_codes_str = read_record()
    from utils.path_manager import get_company_relations
    relation_path = get_company_relations()
    relation_codes = pd.read_csv(relation_path,usecols=['code'])
    relation_codes = relation_codes['code'].tolist()
    relation_codes_str = [str(code) for code in relation_codes]
    # 使用集合操作去除重複代碼
    unique_codes = list(set(relation_codes_str) - set(record_codes_str))
    return unique_codes
if __name__ == '__main__':
    # Use Case 1
    # csv_files = [f for f in listdir(folder_path) if isfile(join(folder_path, f)) and f.endswith('.csv')]
    # codes = []
    # for file in csv_files:
    #     code = check_code_range(file)
    #     if code is not None:
    #         codes.append(code)
    # record(codes)
    
    # Use Case 2
    print(need_to_download_company())
    pass