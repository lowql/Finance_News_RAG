```python
BASE_ENTITY_LABEL = "__Entity__"
BASE_NODE_LABEL = "__Node__"
EXCLUDED_LABELS = ["_Bloom_Perspective_", "_Bloom_Scene_"]
EXCLUDED_RELS = ["_Bloom_HAS_SCENE_"]
EXHAUSTIVE_SEARCH_LIMIT = 10000
# Threshold for returning all available prop values in graph schema
DISTINCT_VALUE_LIMIT = 10
CHUNK_SIZE = 1000
VECTOR_INDEX_NAME = "entity"
```
## upsert_relations()

```python
self.structured_query(
                f"""
                UNWIND $data AS row
                MERGE (source: {BASE_NODE_LABEL} {{id: row.source_id}})
                ON CREATE SET source:Chunk
                MERGE (target: {BASE_NODE_LABEL} {{id: row.target_id}})
                ON CREATE SET target:Chunk
                WITH source, target, row
                CALL apoc.merge.relationship(
	                source, row.label, {{}}, row.properties, target
                ) YIELD rel
                RETURN count(*)
                """,
                param_map={"data": chunked_params},
            )
```