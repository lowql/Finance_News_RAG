import pandas as pd
import uuid

# TODO: 建立具有可解釋與可搜索性的ID
def create_readable_id(row):
    name_part = f"{row['stock_id']}_{row['title'][:2]}"
    unique_part = str(uuid.uuid4())[:8]
    return f"{name_part}_{unique_part}"

def check_unique(df):
    if df['readable_id'].duplicated().any():
        print("warning: existing duplicated ID, regenerating...")
        df['readable_id'] = df.apply(create_readable_id,axis=1)
        
def search_use_index(index):
    # query index
    title_index = df.set_index('stock_id')
    return title_index.loc[index]

# 按ID搜索 (估計不會用到)
def search_by_id(readable_id):
    return df[df['readable_id'] == readable_id]
    
def save(df):
    df.to_csv('updated_file.csv',index=False)
    
if __name__ == "__main__":

    # ,date,stock_id,link,source,title
    csv_file = f"dataset\news\6125_history_news.csv"

    df = pd.read_csv(csv_file)

    df['readable_id'] = df.apply(create_readable_id,axis=1)
    
    result = search_use_index(6125)
    print(result)

    
    # 從 DataFrame 中提取數據
    documents = df['content'].tolist()
    metadatas = df[['source']].to_dict('records')

    # HACK: 
    ids = df['id'].tolist()

    # 使用提取的數據調用 add 方法
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )