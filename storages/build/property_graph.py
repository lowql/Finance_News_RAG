from llama_index.core import PropertyGraphIndex
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from config.db_config import Neo4j_USER,Neo4j_PWD,Neo4j_URI
from typing import Literal
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import Settings
ollama_embedding = OllamaEmbedding(
    model_name="yi",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0}
)
# AttributeError: 'OpenAIEmbedding' object has no attribute '__pydantic_private__'. Did you mean: '__pydantic_complete__'?
Settings.embed_model = ollama_embedding
from llama_index.llms.ollama import Ollama
llm = Ollama(model='yi',request_timeout=360)
Settings.llm = llm
class BuildPropertyGraph:
    
    def __init__(self):
        self.graph_store = Neo4jPropertyGraphStore(
            username=Neo4j_USER,
            password=Neo4j_PWD,
            url=Neo4j_URI,
        )
        self.entities = Literal["Company", "News","Items"]
        self.relations = Literal["有", "研發", "使用", "提及", "影響","有關"]
        self.validation_schema = {
            "Company": ["研發", "使用"],
            "News": ["影響"],
            "Items": ["有關"],
        }
        self.max_knowledge_triplets = 3
        # self.neo4j_prompt 
        self.kg_extract_templete = ""
        self.text_qa_template = ""
        self.refine_template = ""
        self.index = PropertyGraphIndex.from_documents
    def set_prompt_template(self):
        from utils.path_manager import get_llama_index_template
        from jinja2 import Template

        with open(get_llama_index_template('kg_extract'), 'r',encoding='utf8') as template_file:
            template = Template(template_file.read())
            max_knowledge_triplets = 3
            self.kg_extract_templete = template.render(max_knowledge_triplets=max_knowledge_triplets)
            
        with open(get_llama_index_template('refine'), 'r',encoding='utf8') as template_file:
            template = Template(template_file.read())
            self.refine_template = template.render()
        with open(get_llama_index_template('text_qa'), 'r',encoding='utf8') as template_file:
            template = Template(template_file.read())
            self.text_qa_template = template.render
        

    def _schema_llm_extractor(self):
        from llama_index.core.indices.property_graph import SchemaLLMPathExtractor
        neo4j_prompt = neo4j_prompt.format(max_knowledge_triplets=self.max_knowledge_triplets)
        kg_schema_extractor = SchemaLLMPathExtractor(
            strict=False,  # Set to False to showcase why it's not going to be the same as DynamicLLMPathExtractor
            possible_entities=self.entities,  # USE DEFAULT ENTITIES (PERSON, ORGANIZATION... etc)
            possible_relations=self.relations,  # USE DEFAULT RELATIONSHIPS
            kg_validation_schema=self.validation_schema,
            extract_prompt=neo4j_prompt,
            possible_relation_props=[
                "額外備註關係"
            ],  # Set to `None` to skip property generation
            possible_entity_props=[
                "額外備註"
            ],  # Set to `None` to skip property generation
            num_workers=10,
        )
        return kg_schema_extractor
    def _dynamic_llm_extractor(self):
        from llama_index.core.indices.property_graph import DynamicLLMPathExtractor
        """ 
        neo4j.exceptions.ClientError: 
        {code: Neo.ClientError.Procedure.ProcedureCallFailed} 
        {message: Failed to invoke procedure `apoc.create.addLabels`: Caused by: org.neo4j.internal.kernel.api.exceptions.schema.IllegalTokenNameException: '' is not a valid token name. Token names cannot be empty or contain any null-bytes.}
        """
        kg_dynamic_extractor = DynamicLLMPathExtractor(
                    max_triplets_per_chunk=5,
                    num_workers=4,
                    allowed_entity_types=["Company", "News","Items"],
                )
        return kg_dynamic_extractor
    def build_index_from_documents(self,documents):
        kg_extractor = self._dynamic_llm_extractor()
        index = PropertyGraphIndex.from_documents(
            documents[:3],
            use_async = False,
            kg_extractors=[
                kg_extractor,
            ],
            property_graph_store=self.graph_store,
            show_progress=True,
                
        )
        return index
    
