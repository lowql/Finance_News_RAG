import chardet
import httpx
from bs4 import BeautifulSoup
import re
import pandas as pd
from typing import List,Dict,Any
import os

class Interactive:
    def __init__(self):
        self.dataset_path = './dataset/base/company_relations.csv'
        self.baseurl = "https://stockchannelnew.sinotrade.com.tw/z/zc/zc0/zc00/zc00_{code}.djhtm"
        self.type_map = ['suppliers','competitor','customers','reinvestment','invested','strategic_alliance']
        self.Interactive_types = {'suppliers':[],'competitor':[],'customers':[],'reinvestment':[],'invested':[],'strategic_alliance':[]}
        self.code = 0
        
        "累加機制: "
        self.relation_codes:List[Dict[str, Any]] = []
    def save_soup(self,code,soup):
        with open(f'{code}_interactive.html','w',encoding="utf-8") as f:
            f.write(str(soup))
            
    def detect_encoding(self,HTML_content):
        "避免使用到錯誤的編碼解析格式"
        result = chardet.detect(HTML_content.content)
        encoding = result['encoding']
        HTML_content.encoding = encoding
        return HTML_content      

    def fix_encoding(self,data=None):
        # 原始數據
        # 5223 安力-KY , 6720 久昌
        data = ['6720¤[©÷\r\n', '¦w¤O-KY']
        # 將字符串進行解碼和替換
        fixed_data = []
        for item in data:
            # 嘗試解碼並清理字符串
            print(item.encode('utf8'))
            cleaned_item = item.encode('big5')
            fixed_data.append(cleaned_item)
        
        return fixed_data
    
    def parse_from_url(self,code):
        response = self.detect_encoding(httpx.get(self.baseurl.format(code=code)))
        soup = BeautifulSoup(response.text,'html.parser')
        content = soup.find('div',id="SysJustIFRAMEDIV")
        self.code = code
        # self.save_soup(self.code,str(content))
        return self.parse_interactive_html(str(content))
        
    def parse_from_file(self,file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return self.parse_interactive_html(content)

    def parse_interactive_html(self,content):
        soup = BeautifulSoup(content, 'html.parser')
        """ 
		<td align="center" class="t10" colspan="3">建準(2421)公司互動</td>
        """
        name = soup.find('td',{'class':'t10'}).text[:-4]
        
        tables = soup.find_all('td', {'class': 't3t1', 'bgcolor': 'white', 'valign': 'top'})
        type_map = self.type_map
        Interactive_types = {'suppliers':[],'competitor':[],'customers':[],'reinvestment':[],'invested':[],'strategic_alliance':[]}
        
        interactives = {t: Interactive_types[t] for t in type_map}
        interactives['name'] = name
        relation_codes = {}
        for i,table in enumerate(tables):
            # print(f"\n---------{type_map[i]}---------\n")
            content = table.find('div',{'class':'t3t1'})
            """ 
            <!--GenLink2stk('AS2478','大毅');//-->
            """
            genlink_calls = re.findall(r"GenLink2stk\('([^']+)',\s*'([^']+)'\)", str(content))
            genlink_content =  [item[1] for item in genlink_calls]
            relation_codes[type_map[i]] = [item[0][2:] for item in genlink_calls]
            """ 
            <img .../> JinkoSolar Middle East
            """
            pattern = re.compile(r'<img[^>]*>\s*([^\s<]+[^<]*)')
            base_content = pattern.findall(str(content))
            
            """ 
            <a href="/z/zn/zne/zne.djhtm?a=000725.SZ" target="_self">京東方Ａ</a>
            """
            try:
                url_content = content.find_all('a',{'target':"_self"})
                url_content = [link.text for link in url_content]
            except:
                """ AttributeError: 'NoneType' object has no attribute 'find_all' """
                url_content = []
                
            Interactive_type = [*base_content,*url_content,*genlink_content] #HACK : *list is python deconstructure magic
            
            # print(Interactive_type)
            """ ['6720久昌\r\n', '安力-KY'] (叛逆小夥)"""
            Interactive_type = [item.rstrip('\r\n') if item.endswith('\r\n') else item for item in Interactive_type]
            Interactive_types[type_map[i]].append(Interactive_type)

        # [ ]: 回傳相關的上市公司代碼 
        self.relation_codes.append({name:relation_codes})
        return interactives
        
    def save_as_csv(self,company_list:list):
        """ 預期儲存格式
        code,name,suppliers,competitor,customers,reinvestment,invested,strategic_alliance
        6125,廣運,[..,..,..],...
        1301,台塑,[..,..,..],...
        2303,聯電,[..,..,..],...
        """
        Interactive_info = []   

        for code in company_list:
            result = inter.parse_from_url(int(code))
            company_data = {
                'code': code,
                'name': result.get('name',None),
                'suppliers': result.get('suppliers', [None])[0],
                'competitor': result.get('competitor', [None])[0],
                'customers': result.get('customers', [None])[0],
                'reinvestment': result.get('reinvestment', [None])[0],
                'invested': result.get('invested', [None])[0],
                'strategic_alliance': result.get('strategic_alliance', [None])[0]
            }
            Interactive_info.append(company_data)
            
        df = pd.DataFrame(Interactive_info)

        filename = self.dataset_path 
        file_exists = os.path.isfile(filename)
        if file_exists:
            # 如果文件存在，追加数据而不写入头部
            df.to_csv(filename, mode='a', header=False, index=False)
        else:
            # 如果文件不存在，创建新文件并写入头部
            df.to_csv(filename, index=False)

        print(company_list,"資料下載完成")
    "Duplicates 重複"
    def csv_rm_duplicates(self):
        "if company_list[...] 會出現重複的資料"
        df = pd.read_csv(self.dataset_path)
        df.drop_duplicates(inplace = True) 
if __name__ == '__main__':
    inter = Interactive()
    inter.csv_rm_duplicates()
    """ inter.relation_codes[0]
    # {'廣運(6125)': {'suppliers': ['2478',...],... }} 
    """
    
    """ 專注於 6125 
    inter.save_as_csv(company_list=[6125])
    print("dealing with ",6125)
    """
    
    """ company_list[0] aka 6125 延伸的公司
    for name,interactives in inter.relation_codes[0].items():
        for interactive,codes in interactives.items():
            print("dealing with ",codes)
            inter.save_as_csv(company_list=codes)
    """
    
    

    
    
