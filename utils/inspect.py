""" 
單純好奇 fetch_yahoo 中 URL DECODE 的結果 BAD & OK URL 的差異性
結論是沒差，所以會導致不是所有新聞都可以被載入到資料庫。
"""
def inspect_overlapping(ok_urls,bad_urls):
    print(f"len of ok_urls {len(ok_urls)}")
    print(f"len of bad_urls {len(bad_urls)}")
    # 首先，我們需要從 ok_urls 和 bad_urls 中提取所有的 title
    ok_titles = set(row[3] for row in ok_urls)
    bad_titles = set(row[3] for row in bad_urls)

    # 找出重疊的 titles
    overlapping_titles = ok_titles.intersection(bad_titles)

    # 打印結果
    if overlapping_titles:
        print("以下 titles 在 ok_urls 和 bad_urls 中都出現了：")
        for title in overlapping_titles:
            print(title)
    else:
        print("ok_urls 和 bad_urls 中沒有重疊的 titles。")

    # 如果你想知道重疊的數量，可以使用：
    print(f"重疊的 title 數量: {len(overlapping_titles)}")

    # 如果你想知道各自獨有的 title 數量，可以使用：
    print(f"只在 ok_urls 中出現的 title 數量: {len(ok_titles - bad_titles)}")
    print(f"只在 bad_urls 中出現的 title 數量: {len(bad_titles - ok_titles)}")

def inspect_similar(ok_urls,bad_urls,threshold=0.8):
    from difflib import SequenceMatcher

    # 使用 lambda 定義相似度函數
    similar = lambda a, b, threshold=threshold: SequenceMatcher(None, a, b).ratio() > threshold

    # 提取標題
    ok_titles = [row[3] for row in ok_urls]
    bad_titles = [row[3] for row in bad_urls]

    # 使用列表推導式和 lambda 找出相似的標題
    similar_titles = [(ok, bad) for ok in ok_titles for bad in bad_titles if similar(ok, bad)]

    # 打印結果
    if similar_titles:
        print("以下是相似的標題對：")
        for ok_title, bad_title in similar_titles:
            print(f"ok_urls: {ok_title}")
            print(f"bad_urls: {bad_title}")
            print("---")
    else:
        print("沒有找到相似的標題。")

    # 打印相似標題對的數量
    print(f"相似標題對的數量: {len(similar_titles)}")
