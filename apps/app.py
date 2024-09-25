from flask import request
from flask import Flask,render_template
from flask import send_from_directory     
import os 


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

@app.get("/news/<int:stock_id>")
def get_news(stock_id):
    return f"These are {stock_id} news"


@app.get("/query")
def query_index():
    # http://localhost:5000/query?text=廣運的產品是?
    query_text = request.args.get("text", None)
    import sys
    print(sys.path)
    # ['D:\\_Research\\Finance_News_RAG\\apps', 'D:\\_Research\\Finance_News_RAG', ]

    print(f"Get Client Message: {query_text}")
    if query_text is None:
        return (
            "No text found, please include a ?text=blah parameter in the URL",
            400,
        )
    # Now you can import your modules
    from retrievers.llama_index.pg_query import query
    response = query(query_text)
    return str(response), 200

app.run()