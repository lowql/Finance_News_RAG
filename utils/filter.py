from difflib import SequenceMatcher
from utils.decodeGoogleRss import decode_google_news_url
from utils.path_manager import get_filter_news_file,get_history_news_file
import pandas as pd

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def mark_similar_titles(df, threshold=0.6):
    titles = df['title'].tolist()
    is_similar = [0] * len(titles)  # 初始化所有標題為不相似
    
    for i in range(len(titles)):
        if is_similar[i] == 1:  # 如果已經標記為相似，跳過
            continue
        for j in range(i + 1, len(titles)):
            if similar(titles[i], titles[j]) >= threshold:
                is_similar[j] = 1  # 標記相似的標題
    
    return is_similar

# Process URLs for Yahoo rows
def process_url(row):
    url = decode_google_news_url(row['link'])
    if url.endswith('.html'):
        return pd.Series({'link': url, 'available': True})
    else:
        return pd.Series({'link': url, 'available': False})

# Example usage
if __name__ == "__main__":
    csv_file = get_history_news_file(code=6125)
    df = pd.read_csv(csv_file,index_col=0)
    
    df['is_similar'] = 0  # Initialize with False
    
    # Process rows where source is 'Yahoo奇摩股市'
    yahoo_mask = df['source'] == 'Yahoo奇摩股市'
    df.loc[yahoo_mask, 'is_similar'] = mark_similar_titles(df[yahoo_mask], threshold=0.8)
    
    df.loc[yahoo_mask, ['link', 'available']] = df.loc[yahoo_mask].apply(process_url, axis=1)

    # 保存結果
    output_file = get_filter_news_file(code=6125)
    
    no_similar = df['is_similar'] == 0
    is_available = df['available'] ==  True

    df = df.loc[yahoo_mask&no_similar&is_available]
    df.to_csv(output_file, index=False)

    print(f"處理完成，結果已保存到 {output_file}")
    print(f"相似標題數量: {df['is_similar'].sum()}")
    print(f"不相似標題數量: {len(df) - df['is_similar'].sum()}")
    print(f"可使用連結: {df['available'].sum()}")
    print(f"不可使用連結: {len(df) - df['available'].sum()}")