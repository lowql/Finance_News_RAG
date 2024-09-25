from pydantic import BaseModel, Field
from typing import List


class Artist(BaseModel):
    name: str
    birthday: str

class Manga(BaseModel):
    name: str
    artist: Artist
    character : List[str] = Field(min_items=3, max_items=10)

from setup import get_llm

# if isinstance(llm, HuggingFaceLLM):
# if isinstance(llm, LlamaCPP):
llm = get_llm()


def test_output():
    from llama_index.program.lmformatenforcer import (
        LMFormatEnforcerPydanticProgram,
    )
    program = LMFormatEnforcerPydanticProgram(
    output_cls=Manga,
    prompt_template_str=(
            "Your response should be according to the following json schema: \n"
            "{json_schema}\n"
            "請介紹 {manga_name}，包含漫畫名稱、漫畫作者、漫畫的登場腳色，使用"
            "只能使用繁體中文回應內容"
        ),
        llm=llm,
        verbose=True,
    )

    output = program(manga_name="七龍珠")
    print(output)

