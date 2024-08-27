from difflib import SequenceMatcher
from decodeGoogleRss import decode_google_news_url
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

# Example usage
if __name__ == "__main__":
    csv_file = "..\\dataset\\news\\6125_history_news.csv"
    df = pd.read_csv(csv_file)
    
    # 添加新列 'is_similar'
    df['is_similar'] = mark_similar_titles(df, threshold=0.8)
    df['link'] = df['link'].apply(decode_google_news_url)

    # 保存結果
    output_file = "..\\dataset\\news\\6125_history_news_with_similarity.csv"
    df.to_csv(output_file, index=False)

    print(f"處理完成，結果已保存到 {output_file}")
    print(f"相似標題數量: {df['is_similar'].sum()}")
    print(f"不相似標題數量: {len(df) - df['is_similar'].sum()}")