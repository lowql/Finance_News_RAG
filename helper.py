import argparse

# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')
# Required positional argument
parser.add_argument('--var', type=str,
                    help='請輸入要查詢的變數名稱')

parser.add_argument('-k','--KeywordExtract', type=str,
                    help='請輸入要提取關鍵字的文章')

args = parser.parse_args()
print(args)


from setup import get_llm
llm = get_llm()
def query(query_txt):
    completions = llm.stream_complete(query_txt)
    for completion in completions:
        print(completion.delta, end="")
        
if args.var !=  None:
    prompt = "請直接幫我相對應的程式變數命名，並給出後續可能會用到的單詞(i.e. var (chinese))"
    query_txt = args.var + prompt
    query(query_txt)
    
if args.KeywordExtract != None:
    prompt = "請提取出文章中的關鍵詞並附加關鍵詞前後連接詞(i.e. 再開發、轉型、出售、吸引)，用條列形式呈現"
    query_txt = args.KeywordExtract + prompt
    query(query_txt)
    








