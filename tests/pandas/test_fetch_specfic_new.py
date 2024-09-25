import pandas as pd
from utils.test_tools import fetch_document_as_df
from pydantic import BaseModel,Field,field_validator
from typing import List,Optional
from datetime import datetime

class state(BaseModel):
    title: str = Field(description="說明的標題 i.e. .<number>. ...:")
    content: str = Field(description="跟在標題後面的內容 i.e. ...:")
class BoardResolution(BaseModel):
    date: str = Field("日期 i.e. %Y年%m月%d日")
    company_name: str = Field(description="上市公司名稱 i.e. 台積電")
    point: str = Field(description="主旨 i.e. 主 旨：...董事會決議通過XXX")
    spokesperson: str = Field(description="發言人 i.e. 王曉明")
    case_state: List[state] = Field(description="說明")
    
    @field_validator('date')
    def validate_date(cls, v):
        try:
            # 将中文日期格式转换为datetime对象
            date_obj = datetime.strptime(v, "%Y年%m月%d日")
            return v  # 返回原始字符串
        except ValueError:
            raise ValueError("日期格式无效，应为'YYYY年MM月DD日'")
    
    
df = fetch_document_as_df()
filtered_df = df[df['headline'].str.contains('【公告】')]
# 显示结果
print(filtered_df['content'].iloc[0])

prompt_template_str = """
我會給你一個董事會的決議書，按照指定格式提取資訊:
決議書 - {BoardResolution}
"""
def test_LLMTextCompletionProgram():
    from llama_index.core.program import LLMTextCompletionProgram

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=BoardResolution,
        prompt_template_str=prompt_template_str,
        verbose=True,
    )

    output = program(BoardResolution=filtered_df['content'].iloc[0])

    print(output)

