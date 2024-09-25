from llama_index.core import Document
from utils.path_manager import get_news_content_file
documents = []
with open(get_news_content_file(6125),'r',encoding='utf8') as csvfile:
    import csv
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        documents.append(Document(
            text=row['content'],
            metadata={'author':row['author'],'headline':row['headline']},
            metadata_seperator="\n",
            metadata_template="{key} [ {value} ] ",
            text_template="Metadata:\n {metadata_str}\n-----\nContent: {content}",
            ))
        
from llama_index.core import Settings

from llama_index.embeddings.ollama import OllamaEmbedding
ollama_embedding = OllamaEmbedding(
    model_name="yi",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0}
)
Settings.embed_model = ollama_embedding

from llama_index.llms.ollama import Ollama
llm = Ollama(model='yi',request_timeout=360)
Settings.llm = llm

from llama_index.core import PropertyGraphIndex
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from config import Neo4j_URI,Neo4j_USER,Neo4j_PWD
graph_store = Neo4jPropertyGraphStore(
            username=Neo4j_USER,
            password=Neo4j_PWD,
            url=Neo4j_URI,
        )
index = PropertyGraphIndex.from_existing(property_graph_store=graph_store,use_async=False)
def test_base_retriever():
    # Define retriever
    retriever = index.as_retriever(
        include_text=False,  # include source text in returned nodes, default True
    )
    results = retriever.retrieve("廣運的兢爭對手?")
    for record in results:
        print(record.text)
def test_LLMSynonymRetriever():
    from llama_index.core.indices.property_graph import LLMSynonymRetriever

    prompt = (
        "Given some initial query, generate synonyms or related keywords up to {max_keywords} in total, "
        "considering possible cases of capitalization, pluralization, common expressions, etc.\n"
        "Provide all synonyms/keywords separated by '^' symbols: 'keyword1^keyword2^...'\n"
        "Note, result should be in one-line, separated by '^' symbols."
        "----\n"
        "QUERY: {query_str}\n"
        "----\n"
        "KEYWORDS: "
    )


    def parse_fn(self, output: str) -> list[str]:
        matches = output.strip().split("^")

        # capitalize to normalize with ingestion
        return [x.strip().capitalize() for x in matches if x.strip()]


    synonym_retriever = LLMSynonymRetriever(
        index.property_graph_store,
        llm=llm,
        # include source chunk text with retrieved paths
        include_text=False,
        synonym_prompt=prompt,
        output_parsing_fn=parse_fn,
        max_keywords=10,
        # the depth of relations to follow after node retrieval
        path_depth=1,
    )

    retriever = index.as_retriever(sub_retrievers=[synonym_retriever])
def test_TextToCypherRetriever():
    from llama_index.core.indices.property_graph import TextToCypherRetriever

    DEFAULT_RESPONSE_TEMPLATE = (
        "Generated Cypher query:\n{query}\n\n" 
        "Cypher Response:\n{response}"
       
        
    )
    DEFAULT_ALLOWED_FIELDS = ["text", "label", "type"]

    from llama_index.core.prompts import PromptTemplate
    from utils.path_manager import get_llama_index_template
    with open(get_llama_index_template('cypher'), 'r',encoding='utf8') as template_file:
        TEXT_TO_CYPHER_TEMPLATE_STR =  template_file.read()
        
    DEFAULT_TEXT_TO_CYPHER_TEMPLATE = PromptTemplate(TEXT_TO_CYPHER_TEMPLATE_STR)
    print(DEFAULT_TEXT_TO_CYPHER_TEMPLATE)
    
    
    cypher_retriever = TextToCypherRetriever(
        index.property_graph_store,
        # customize the LLM, defaults to Settings.llm
        llm=llm,
        # customize the text-to-cypher template.
        # Requires `schema` and `question` template args
        text_to_cypher_template=DEFAULT_TEXT_TO_CYPHER_TEMPLATE,
        # customize how the cypher result is inserted into
        # a text node. Requires `query` and `response` template args
        response_template=DEFAULT_RESPONSE_TEMPLATE,
        # an optional callable that can clean/verify generated cypher
        cypher_validator=None,
        # allowed fields in the resulting
        allowed_output_field=DEFAULT_ALLOWED_FIELDS,
    )
    print(f"\n Graph Schema: {graph_store.get_schema_str()}\n\n")
    print(f"\n cypher template: {graph_store.text_to_cypher_template}\n\n")
    
    from llama_index.core.schema import QueryBundle
    # Create a query bundle
    query_bundle = QueryBundle(
        query_str =["廣運"]
    )

    # Retrieve nodes from the graph store using the vector store query
    nodes_with_scores = cypher_retriever.retrieve_from_graph(query_bundle)
    print(nodes_with_scores)
    graph_store.close()
    
    
def test_CypherTemplateRetriever():
    # NOTE: current v1 is needed
    from pydantic import BaseModel, Field
    from llama_index.core.indices.property_graph import CypherTemplateRetriever

    # write a query with template params
    cypher_query = """
        MATCH (c:Chunk)-[:MENTIONS]->(o)
        WHERE o.name IN $names
        RETURN c.text, o.name, o.label;
    """


    # create a pydantic class to represent the params for our query
    # the class fields are directly used as params for running the cypher query
    class TemplateParams(BaseModel):
        """Template params for a cypher query."""

        names: list[str] = Field(
            description="A list of entity names or keywords to use for lookup in a knowledge graph."
        )


    template_retriever = CypherTemplateRetriever(
        index.property_graph_store, TemplateParams, cypher_query
    )
    return template_retriever
def test_add_sub_retriever():
    # create a retriever
    retriever = index.as_retriever(sub_retrievers=[retriever1, retriever2, ...])

if __name__ == "__main__":
    print('\n\n',test_CypherTemplateRetriever(),'\n\n')