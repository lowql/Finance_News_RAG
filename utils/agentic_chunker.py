import uuid
from typing import Optional
from setup import get_llm

from llama_index.core import Document
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import ChatPromptTemplate

class AgenticChunker:
    def __init__(self, openai_api_key=None):
        self.chunks = {}
        self.id_truncate_limit = 5
        # Whether or not to update/refine summaries and titles as you get new information
        self.generate_new_metadata_ind = True
        self.print_logging = True
        self.llm = get_llm()

    def add_propositions(self, propositions):
        for proposition in propositions:
            self.add_proposition(proposition)
    
    def add_proposition(self, proposition):
        if self.print_logging:
            print (f"\nAdding: '{proposition}'")

        # If it's your first chunk, just make a new chunk and don't check for others
        if len(self.chunks) == 0:
            if self.print_logging:
                print ("No chunks, creating a new one")
            self._create_new_chunk(proposition)
            return

        chunk_id = self._find_relevant_chunk(proposition)

        # If a chunk was found then add the proposition to it
        if chunk_id:
            if self.print_logging:
                print (f"Chunk Found ({self.chunks[chunk_id]['chunk_id']}), adding to: {self.chunks[chunk_id]['title']}")
            self.add_proposition_to_chunk(chunk_id, proposition)
            return
        else:
            if self.print_logging:
                print ("No chunks found")
            # If a chunk wasn't found, then create a new one
            self._create_new_chunk(proposition)
        

    def add_proposition_to_chunk(self, chunk_id, proposition):
        # Add then
        self.chunks[chunk_id]['propositions'].append(proposition)

        # Then grab a new summary
        if self.generate_new_metadata_ind:
            self.chunks[chunk_id]['summary'] = self._update_chunk_summary(self.chunks[chunk_id])
            self.chunks[chunk_id]['title'] = self._update_chunk_title(self.chunks[chunk_id])

    def _update_chunk_summary(self, chunk):
        """
        If you add a new proposition to a chunk, you may want to update the summary or else they could get stale
        """
        summary_template =  [
             ChatMessage(content="""\nYou are the steward of a group of chunks which represent groups of sentences that talk about a similar topic
                一個新的 propositions 剛剛添加到您的一個 chunk 中，您應該產生一個非常簡短的一句話 summary ，它將告訴觀眾塊組的含義。
                一個好的 summary 會說明該 chunk 的內容，並給出有關添加到該 chunk 的內容的任何澄清說明。
                您將獲得一組位於該 chunk 中的 propositions 以及該 chunk 的當前 summary 。
                你的總結應該預見到概括性。
                如果你得到一個關於蘋果的建議，請將其推廣到食物。或月份，概括為「日期和時間」。
                例子：
                輸入： Proposition ：Greg 喜歡吃披薩
                輸出：此 chunk 包含有關格雷格喜歡吃的食物類型的信息。

                Only respond with the chunk new summary, nothing else.""", 
                role=MessageRole.SYSTEM),
             ChatMessage(content="""\n chunk  propositions:\n{proposition}\n\n 當前 chunk  summary:\n{current_summary}""",
                         role=MessageRole.USER)
            ]
        chat_template = ChatPromptTemplate(message_templates=summary_template)
        messages = chat_template.format(proposition=chunk['propositions'],current_summary=chunk['summary'])
        new_chunk_summary = self.llm.complete(messages)
        return new_chunk_summary
    
    def _update_chunk_title(self, chunk):
        """
        If you add a new proposition to a chunk, you may want to update the title or else it can get stale
        """
        summary_template = [
            ChatMessage(content="""
您是一組Chunk的管理員，這些Chunk代表談論相似主題的句子組
一個新的 propositions 剛剛添加到您的一個Chunk中，您應該產生一個非常簡短的更新Chunk title ，它將告知觀眾Chunk組的含義。
一個好的 title 會說明該Chunk的內容。
您將獲得一組位於大塊、大塊 summary 和大塊 title 中的 propositions 。
你的title應該要具有概括性。如果你得到一個關於蘋果的建議，請將其推廣到食物。
或月份，概括為「日期和時間」。
例子：
輸入： summary ：這一部分是關於作者談論的日期和時間
輸出：日期和時間
僅響應新的Chunk title，沒有其他內容。""",role=MessageRole.SYSTEM),
            ChatMessage(content= "Chunk's propositions:\n{proposition}\n\nChunk summary:\n{current_summary}\n\nCurrent chunk title:\n{current_title}",role=MessageRole.USER)
        ] 

        chat_template = ChatPromptTemplate(message_templates=summary_template)
        messages = chat_template.format(
            proposition=chunk['propositions'],
            current_summary=chunk['summary'],
            current_title=chunk['title']
            )
        new_chunk_summary = self.llm.complete(messages)
        return new_chunk_summary

    def _get_new_chunk_summary(self, proposition):
        summary_template =  [
             ChatMessage(content="""”“”
 您是一組 chunk 的管理員，這些 chunk 代表談論相似主題的句子組
 您應該產生一個非常簡短的一句話 summary ，它將告訴檢視者一個 chunk 組的含義。
 一個好的 summary 會說明該 chunk 的內容，並給出有關添加到該 chunk 的內容的任何澄清說明。
 您將收到一個proposition，該proposition將進入一個新的 chunk 。這個新 chunk 需要一個 summary 。
 你的總結應該預見到概括性。如果你得到一個關於蘋果的建議，請將其推廣到食物。
 或月份，概括為「日期和時間」。
 例子：
    輸入： proposition：Greg 喜歡吃披薩
    輸出：此 chunk 包含有關格雷格喜歡吃的食物類型的信息。
 僅響應新的 chunk  summary ，沒有其他內容。""", 
                role=MessageRole.SYSTEM),
             ChatMessage(content="Determine the summary of the new chunk that this proposition will go into:\n{proposition}",
                         role=MessageRole.USER)
            ]
        chat_template = ChatPromptTemplate(message_templates=summary_template)
        messages = chat_template.format(proposition=proposition)
        new_chunk_summary = self.llm.complete(messages)
        return new_chunk_summary
    
    def _get_new_chunk_title(self, summary):
        summary_template =  [
             ChatMessage(content="""\n您是一組 chunk 的管理員，這些 chunk 代表談論相似主題的句子組
 您應該產生一個非常簡短的幾個字的 chunk 標題，它將告訴觀眾 chunk 組的含義。
 一個好的 chunk 標題很簡短，但包含了 chunk 的內容
 您將獲得需要標題的 chunk 的 summary 
 你的標題應該預見到概括性。如果你得到一個關於蘋果的建議，請將其推廣到食物。
 或月份，概括為「日期和時間」。
 例子：
 輸入： summary ：這一部分是關於作者談論的日期和時間
 輸出：日期和時間
 僅響應新的 chunk 標題，沒有其他內容。""", 
                role=MessageRole.SYSTEM),
             ChatMessage(content=""""Determine the title of the chunk that this summary belongs to:\n{summary}""",
                         role=MessageRole.USER)
            ]
        chat_template = ChatPromptTemplate(message_templates=summary_template)
        messages = chat_template.format(summary=summary)
        new_chunk_title = self.llm.complete(messages)
        return new_chunk_title

    def _create_new_chunk(self, proposition):
        new_chunk_id = str(uuid.uuid4())[:self.id_truncate_limit] # I don't want long ids
        new_chunk_summary = self._get_new_chunk_summary(proposition)
        print(f"\nnew_chunk_summary:\n {new_chunk_summary} \n")
        new_chunk_title = self._get_new_chunk_title(new_chunk_summary)
        print(f"\new_chunk_title:\n {new_chunk_title} \n")

        self.chunks[new_chunk_id] = {
            'chunk_id' : new_chunk_id,
            'propositions': [proposition],
            'title' : new_chunk_title,
            'summary': new_chunk_summary,
            'chunk_index' : len(self.chunks)
        }
        if self.print_logging:
            print (f"Created new chunk ({new_chunk_id}): {new_chunk_title}")
    
    def get_chunk_outline(self):
        """
        Get a string which represents the chunks you currently have.
        This will be empty when you first start off
        """
        chunk_outline = ""

        for chunk_id, chunk in self.chunks.items():
            single_chunk_string = f"""Chunk ID: {chunk['chunk_id']}\nChunk Name: {chunk['title']}\nChunk Summary: {chunk['summary']}\n\n"""
        
            chunk_outline += single_chunk_string
        
        return chunk_outline

    def _find_relevant_chunk(self, proposition):
        current_chunk_outline = self.get_chunk_outline()
        summary_template =  [
            ChatMessage(content="""確定「 propositions 」是否應屬於任何現有 chunk 。
 一個 propositions 應該屬於它們的意義、方向或意圖相似的一個塊。
 目標是將相似的 propositions 和 chunk 分組。
 如果您認為一個 propositions 應該與一個 chunk 連接，請返回 chunk  ID。
 如果您認為某個項目不應與現有 chunk 連接，只需返回“No chunks”
 例子：
 輸入：
 -  propositions ：“格雷格真的很喜歡漢堡”
 - 目前 chunk ：
 -  chunk  ID：2n4l3d
 -  chunk 名稱：舊金山的地點
 - 大塊 summary ：與舊金山地點相關的事物概述

 -  chunk  ID：93833k
 - 塊名稱：格雷格喜歡的食物
 - 塊 summary ：格雷格喜歡的食物和菜餚的列表
 輸出：93833k""", 
               role=MessageRole.SYSTEM),
            ChatMessage(content="Current Chunks:\n--Start of current chunks--\n{current_chunk_outline}\n--End of current chunks--",
                        role=MessageRole.USER),
            ChatMessage(content="Determine if the following statement should belong to one of the chunks outlined:\n{proposition}",
                         role=MessageRole.USER),
             
             
            ]
        chat_template = ChatPromptTemplate(message_templates=summary_template)
        messages = chat_template.format(
            proposition =  proposition,
            current_chunk_outline = current_chunk_outline
        )
        chunk_found = self.llm.complete(messages)
        from llama_index.core.extractors import PydanticProgramExtractor
        from pydantic import BaseModel
        class ChunkID(BaseModel):
            """Extracting the chunk id"""
            chunk_id: Optional[str]

        extractor = PydanticProgramExtractor(ChunkID)
        document = Document(text=chunk_found)
        extracted_data = extractor.extract(document)

        if extracted_data:
            chunk_id = extracted_data[0].chunk_id
            if chunk_id and len(chunk_id) == self.id_truncate_limit:
                return chunk_id
        return chunk_found

    def get_chunks(self, get_type='dict'):
        """
        This function returns the chunks in the format specified by the 'get_type' parameter.
        If 'get_type' is 'dict', it returns the chunks as a dictionary.
        If 'get_type' is 'list_of_strings', it returns the chunks as a list of strings, where each string is a proposition in the chunk.
        """
        if get_type == 'dict':
            return self.chunks
        if get_type == 'list_of_strings':
            chunks = []
            for chunk_id, chunk in self.chunks.items():
                chunks.append(" ".join([x for x in chunk['propositions']]))
            return chunks
    
    def pretty_print_chunks(self):
        print (f"\nYou have {len(self.chunks)} chunks\n")
        for chunk_id, chunk in self.chunks.items():
            print(f"Chunk #{chunk['chunk_index']}")
            print(f"Chunk ID: {chunk_id}")
            print(f"Summary: {chunk['summary']}")
            print(f"Propositions:")
            for prop in chunk['propositions']:
                print(f"    -{prop}")
            print("\n\n")

    def pretty_print_chunk_outline(self):
        print ("Chunk Outline\n")
        print(self.get_chunk_outline())

if __name__ == "__main__":
    ac = AgenticChunker()

    ## Comment and uncomment the propositions to your hearts content
    propositions = [
        '今天是宣布美元降息',
        '上市公司廣運接到Nvidia的訂單',
        '股東會宣布上市公司廣運的董事長明年即將卸任',
        '廣運的今天財報營利較去年高30%',
        '廣運的今天財報營利較前年100%',
    ]
    ac.add_propositions(propositions)
    ac.pretty_print_chunks()
    # ac.pretty_print_chunk_outline()
    # print (ac.get_chunks(get_type='list_of_strings'))