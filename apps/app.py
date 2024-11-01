from flask import request,jsonify
from flask import Flask,render_template,Response
from flask import send_from_directory   
from waitress import serve  
import os 
import json
from pipeline.news import News
from llama_index.core.response_synthesizers import ResponseMode
from retrievers.pg_query import query_from_neo4j,summary_news
app = Flask(__name__)


@app.route("/",methods = ['GET','POST'],endpoint="welcome page")
def index():
    return render_template('index.html',message="hello this is RAG Ollama")

@app.route('/favicon.ico') 
def favicon(): 
    path = os.path.join(app.root_path, 'static')
    print(path)
    return send_from_directory(path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.get("/retriever/vector",endpoint="retriever of vector ")
def vector_retriever():
    return "vector_retriever from neo4j"

@app.get("/retriever/graph",endpoint="retriever of property graph")
def graph_retriever():
    return "graph_retriever from neo4j"

@app.get("/companys")
def get_company_list():
    from pipeline import utils
    codes = utils.get_codes()
    return jsonify(codes)

@app.get("/news/<int:stock_id>")
def get_news(stock_id):
    news = News(stock_id)
    contents = news.fetch_content()
    return jsonify(contents)
    
@app.get("/query")
def query_use_backend_data():
    # http://localhost:5000/query?text="廣運的產品是?"
    query_text = request.args.get("text", None)
    print(f"Get Client Message: {query_text}")
    if query_text is None:
        return (
            "No text found, please include a ?text=blah parameter in the URL",
            400,
        )
    # response = pg_retriever_query(query_text,ResponseMode.REFINE)
    stream_response = query_from_neo4j(query_txt=query_text,response_mode=ResponseMode.REFINE)
    def response_generator():
        for text in stream_response.response_gen:
            yield text
    if stream_response.source_nodes == []:
        return "目前尚未掌握相關資訊，故無法回應此問題"
    return Response(
        response=response_generator(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            # 'Connection': 'keep-alive' # AssertionError: Connection is a "hop-by-hop" header; it cannot be used by a WSGI application (see PEP 3333)
        })
    
def serialize_node(node):
        # Extract relevant fields from NodeWithScore object
        return {
            'metadata':node.metadata,
            'text': node.get_text(),
            'score': str(node.get_score()),
        }
@app.get("/query/summary")
def summary_frontend_data():
    from pipeline.news import News
    news = News(6125)
    documents = news.fetch_documnets()
    query_text = request.args.get("text", None)
    print(f"Get Client Message: {query_text}")
    if query_text is None:
        return (
            "No text found, please include a ?text=blah parameter in the URL",
            400,
        )
    stream_response = summary_news(documents=documents[:3],query_txt=query_text)
    if stream_response.source_nodes == [] :
        return json.dumps({'responese':"根據使用者提供的資料，無法回應使用者問題"},ensure_ascii=False)
    serialized_nodes = [serialize_node(node) for node in stream_response.source_nodes]
    json_responese = json.dumps({'source_nodes':serialized_nodes,'responese':stream_response.response},ensure_ascii=False)
    
    def response_generator():
        for text in stream_response.response_gen:
            yield text
    streaming = False
    if streaming:    
        return Response(
            response=response_generator(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                # 'Connection': 'keep-alive' # AssertionError: Connection is a "hop-by-hop" header; it cannot be used by a WSGI application (see PEP 3333)
            })
    else:
        return app.response_class(
            response=json_responese,
            status=200,
            mimetype='application/json'
        )

app.debug = True
if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)