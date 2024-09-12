from flask import Flask,render_template

app = Flask(__name__)

@app.route("/",methods = ['GET','POST'],endpoint="welcome page")
def index():
    return render_template('index.html',message="hello this is RAG Ollama")

@app.get("/retriever/vector",endpoint="retriever of vector ")
def vector_retriever():
    return "vector_retriever from neo4j"

@app.get("/retriever/graph",endpoint="retriever of property graph")
def graph_retriever():
    return "graph_retriever from neo4j"

@app.get("/news/<int:stock_id>")
def get_news(stock_id):
    return f"These are {stock_id} news"