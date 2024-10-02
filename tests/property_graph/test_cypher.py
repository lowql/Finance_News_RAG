from retrievers.llama_index.pg_query import graph_store

def test_structured_query_1():
    graph_store.structured_query("""
        CREATE VECTOR INDEX entity IF NOT EXISTS
        FOR (m:`__Entity__`)
        ON m.embedding
        OPTIONS {indexConfig: {
            `vector.dimensions`:4096,
            `vector.similarity_function`: 'cosine'
        }}
    """)
    graph_store.close()
    
def test_structured_query_2():
    similarity_threshold = 0.9
    word_edit_distance = 5
    data = graph_store.structured_query("""
        MATCH (e:__Entity__)
        CALL {
        WITH e
        CALL db.index.vector.queryNodes('entity', 10, e.embedding)
        YIELD node, score
        WITH node, score
        WHERE score > toFLoat($cutoff)
            AND (toLower(node.name) CONTAINS toLower(e.name) OR toLower(e.name) CONTAINS toLower(node.name)
                OR apoc.text.distance(toLower(node.name), toLower(e.name)) < $distance)
            AND labels(e) = labels(node)
        WITH node, score
        ORDER BY node.name
        RETURN collect(node) AS nodes
        }
        WITH distinct nodes
        WHERE size(nodes) > 1
        WITH collect([n in nodes | n.name]) AS results
        UNWIND range(0, size(results)-1, 1) as index
        WITH results, index, results[index] as result
        WITH apoc.coll.sort(reduce(acc = result, index2 IN range(0, size(results)-1, 1) |
                CASE WHEN index <> index2 AND
                    size(apoc.coll.intersection(acc, results[index2])) > 0
                    THEN apoc.coll.union(acc, results[index2])
                    ELSE acc
                END
        )) as combinedResult
        WITH distinct(combinedResult) as combinedResult
        // extra filtering
        WITH collect(combinedResult) as allCombinedResults
        UNWIND range(0, size(allCombinedResults)-1, 1) as combinedResultIndex
        WITH allCombinedResults[combinedResultIndex] as combinedResult, combinedResultIndex, allCombinedResults
        WHERE NOT any(x IN range(0,size(allCombinedResults)-1,1) 
            WHERE x <> combinedResultIndex
            AND apoc.coll.containsAll(allCombinedResults[x], combinedResult)
        )
        RETURN combinedResult  
    """, param_map={'cutoff': similarity_threshold, 'distance': word_edit_distance})
    for row in data:
        print(row)
    graph_store.close()   