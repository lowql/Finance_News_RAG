from flask import request,jsonify
from flask import Flask,render_template,Response
from flask import send_from_directory   
from waitress import serve  
import os 
from pipeline.news import News
from retrievers.pg_query import stream_query_response
from llama_index.core.response_synthesizers import ResponseMode
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
def query_index():
    # http://localhost:5000/query?text="廣運的產品是?"
    query_text = request.args.get("text", None)
    print(f"Get Client Message: {query_text}")
    if query_text is None:
        return (
            "No text found, please include a ?text=blah parameter in the URL",
            400,
        )
    # response = pg_retriever_query(query_text,ResponseMode.REFINE)
    stream_response = stream_query_response(query_txt=query_text,response_mode=ResponseMode.REFINE)
    def response_generator():
        for text in stream_response.response_gen:
            yield text
    if stream_response.source_nodes == []:
        return "資料庫中未有相關資訊，故無法回應此問題"
    return Response(
        response=response_generator(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            # 'Connection': 'keep-alive' # AssertionError: Connection is a "hop-by-hop" header; it cannot be used by a WSGI application (see PEP 3333)
        })
    
app.debug = True
if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)