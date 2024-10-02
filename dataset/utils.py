import pandas as pd
from utils.path_manager import get_news_content_file
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm

# headline,author,time,content
def inspect(df,pattern):
    print('='*30,pattern,'='*30)
    match_df = df[df['headline'].str.contains(pat = pattern, regex = True)].loc[:,['author','headline','content']]
    for i in range(len(match_df.index)):
        print(f"【消息源({df.iloc[i]['author']}) :: {match_df.iloc[i]['headline']}】")
        print(match_df.iloc[i]['content'])
        print("="*100,'\n')
    
def inspects(df):
    pattern_list = ['【.*】','營收','盤中速報','焦點股','熱門股','《.*》']
    for pattern in pattern_list:
        inspect(df,pattern)
        
def fetch_news(code):
    path = get_news_content_file(code)
    return pd.read_csv(path)

# TODO: (不必要::BUG狀態)顯示新聞消息的分布
def plot_time_line(df):
    # 設置中文字體
    # 尋找系統中支持中文的字體
    chinese_fonts = [f.name for f in fm.fontManager.ttflist if 'Noto Sans CJK' in f.name or 'Microsoft YaHei' in f.name or 'SimHei' in f.name or 'SimSun' in f.name or 'WenQuanYi' in f.name]

    if chinese_fonts:
        plt.rcParams['font.sans-serif'] = chinese_fonts
        print(f"使用字體: {chinese_fonts[0]}")
    else:
        print("警告: 未找到支持中文的字體，文字可能無法正確顯示")
    plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示負號
    import numpy as np

    dates = ["2007-6-29", "2008-7-11", "2009-6-29", "2010-9-21", "2011-10-14", "2012-9-21", "2013-9-20",
            "2014-9-19", "2015-9-25", "2016-3-31", "2016-9-16", "2017-9-22", "2017-11-3", "2018-9-21",
            "2018-10-26", "2019-9-20", "2020-11-13", "2021-9-24", "2022-9-16"
            ]
    phones = ["iPhone", "iPhone-3G", "iPhone-3GS", "iPhone 4", "iPhone 4S", "iPhone 5", "iPhone 5C/5S",
            "iPhone 6/6 Plus", "iPhone 6S/6s Plus", "iPhone SE", "iPhone 7/7 Plus", "iPhone 8/8 Plus",
            "iPhone X", "iPhone Xs/Max", "iPhone XR", "iPhone 11/Pro/Max", "iPhone 12 Pro", "iPhone 13 Pro",
            "iPhone 14 Plus/Pro Max"
            ]
    dates = df['time'].tolist()
    phones = df['headline'].tolist()
    
    iphone_df = pd.DataFrame(data={"Date": dates, "Product": phones})
    # iphone_df["Date"] = pd.to_datetime(iphone_df["Date"])
    iphone_df["Date"] = pd.to_datetime(df["time"])
    iphone_df["Level"] = [np.random.randint(-6,-2) if (i%2)==0 else np.random.randint(2,6) for i in range(len(iphone_df))]

        
    with plt.style.context("fivethirtyeight"):
        fig, ax = plt.subplots(figsize=(9,18))

        ax.plot([0,]* len(iphone_df), iphone_df.Date, "-o", color="black", markerfacecolor="white")
        
        # ax.set_yticks(pd.date_range("2007-1-1", "2023-1-1", freq="YS"), range(2007, 2024))
        ax.set_yticks(pd.date_range("2023-1-1", "2024-10-1", freq="YS"), range(2023, 2024))
        ax.set_xlim(-7,7)

        for idx in range(len(iphone_df)):
            dt, product, level = iphone_df["Date"][idx], iphone_df["Product"][idx], iphone_df["Level"][idx]
            dt_str = dt.strftime("%b-%Y")
            ax.annotate(dt_str + "\n" + product, xy=(0.1 if level>0 else -0.1, dt),
                        xytext=(level, dt),
                        arrowprops=dict(arrowstyle="-",color="red", linewidth=0.8),
                        va="center"
                    );

        ax.spines[["left", "top", "right", "bottom"]].set_visible(False)
        ax.spines[["left"]].set_position(("axes", 0.5))
        ax.xaxis.set_visible(False);
        ax.set_title("iPhone Release Dates", pad=10, loc="left", fontsize=25, fontweight="bold")
        ax.grid(False)
        plt.show()
        

class Analyze:
    def __init__(self,code) -> None:
        self.code = code
        self.path = get_news_content_file(code)
        self.df = pd.read_csv(self.path)
    def publish_distribution(self,resample_mode='QE',period_mode='Q'):
        df = self.df
        df['time'] = pd.to_datetime(df['time'])
        df = df.set_index('time')
        print(df.resample(resample_mode).size().to_period(period_mode))
        
    def Publication(self):
        pass
        

if __name__ == '__main__':
    import os
    news = os.listdir('./dataset/news/')
    codes = [new.split('_')[0] for new in news]
    for code in codes:
        print(f"analyze {code}")
        analyze = Analyze(code)
        inspects(analyze.df)
        # analyze.publish_distribution()
        # print("="*50)