from pydantic import BaseModel, EmailStr, HttpUrl, Field
from llama_index.core.program import LLMTextCompletionProgram

from typing import List, Optional,Union
from llama_index.llms.ollama import Ollama
llm = Ollama(model='yi',request_timeout=360)
from llama_index.core.settings import Settings
Settings.llm = llm
class CompanyInfo(BaseModel):
    company_name: Optional[str] = Field(description="上市公司名稱 i.e. 廣運")
    company_id: Optional[int] = Field(description="上市公司代碼 i.e. 6125")
    products: Optional[Union[str, List[str]]] = Field(description="公司產品、公司業務")

class News(BaseModel):
    author: Optional[str] = Field(description="新聞記者")
    outline: Optional[str] = Field(description="新聞大綱")

prompt_template_str = """\
    使用繁體中文生成一段跟上市公司有關的新聞，內容包含公司名稱、公司ID、公司產品、新聞記者、新聞大綱 \
    請以上市公司 {company_full_name} 作為主題發想.\
    """
def test_PydanticOutputParser():
    from llama_index.core.output_parsers import PydanticOutputParser
    output_parser=PydanticOutputParser(output_cls=CompanyInfo)
    output = """
    {
        "company_name": "廣運",
        "company_id": 6125,
        "products": "水冷散熱"
    }
    """

    parsed_output = output_parser.parse(output)
    print(parsed_output)
    
    unescaped_format = output_parser.get_format_string()
    print(unescaped_format)
        
def test_LLMTextCompletionProgram():
    program = LLMTextCompletionProgram.from_defaults(
        output_cls=CompanyInfo,
        prompt_template_str=prompt_template_str,
        verbose=True,
    )

    output = program(company_full_name="廣運(6125)")

    print(output)

def test_LLMTextCompletionProgram_with_PydanticOutputParser():
    from llama_index.core.output_parsers import PydanticOutputParser
    """ 
    Using PydanticOutputParser: By initializing with a PydanticOutputParser, 
    you encapsulate the parsing logic within the parser itself. 
    This allows for greater control over how the output is processed and validated against the Pydantic model. 
    It also enables additional functionalities, 
    1. custom parsing rules 
    2. error handling
    """
    program = LLMTextCompletionProgram.from_defaults(
        output_parser=PydanticOutputParser(output_cls=CompanyInfo),
        prompt_template_str=prompt_template_str,
        verbose=True,
    )

    output = program(company_full_name="廣運(6125)")
    print(output)



# from llama_index.core.output_parsers import ChainableOutputParser
# class CustomAlbumOutputParser(ChainableOutputParser):
#     """Custom Album output parser.

#     Assume first line is name and artist.

#     Assume each subsequent line is the song.

#     """

#     def __init__(self, verbose: bool = False):
#         self.verbose = verbose

#     def parse(self, output: str) -> Album:
#         """Parse output."""
#         if self.verbose:
#             print(f"> Raw output: {output}")
#         lines = output.split("\n")
#         name, artist = lines[0].split(",")
#         songs = []
#         for i in range(1, len(lines)):
#             title, length_seconds = lines[i].split(",")
#             songs.append(Song(title=title, length_seconds=length_seconds))

#         return Album(name=name, artist=artist, songs=songs)

# def test_ChainableOutputParser():
#     prompt_template_str = """\
#     Generate an example album, with an artist and a list of songs. \
#     Using the movie {movie_name} as inspiration.\

#     Return answer in following format.
#     The first line is:
#     , 
#     Every subsequent line is a song with format:
#     , 

#     """
#     program = LLMTextCompletionProgram.from_defaults(
#         output_parser=CustomAlbumOutputParser(verbose=True),
#         output_cls=Album,
#         prompt_template_str=prompt_template_str,
#         verbose=True,
#     )
#     output = program(movie_name="The Dark Knight")
#     print(output)