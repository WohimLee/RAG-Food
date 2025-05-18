import json
from flask import Flask, request, Response
from milvus_build_local import MilvusDatabase
from dataset import Recipe

app = Flask(__name__)


# 定义一个路由 "/search"，仅支持 POST 请求
@app.route("/search", methods=["POST"])
def search_recipe():
    # 从请求中获取 JSON 数据
    data = request.json

    # 从 JSON 数据中提取 "query" 字段的值，如果不存在则默认为空字符串
    query_text = data.get("query", "")

    # 检查 query_text 是否为空
    if not query_text:
        # 如果 query_text 为空，返回一个错误响应：
        # - 使用 json.dumps 将错误信息转换为 JSON 字符串，并设置 ensure_ascii=False 以确保非 ASCII 字符（如中文）正常显示
        # - 返回 HTTP 状态码 400（Bad Request）
        # - 设置响应头 Content-Type 为 application/json; charset=utf-8，确保客户端正确解析 JSON 数据
        return json.dumps({"error": "Query text is required"}, ensure_ascii=False), 400, {'Content-Type': 'application/json; charset=utf-8'}

    # 调用 database.search 方法，传入 query_text 进行搜索，获取结果
    results = database.search(query_text)

    # 返回搜索结果：
    # - 使用 json.dumps 将结果转换为 JSON 字符串，并设置 ensure_ascii=False 以确保非 ASCII 字符（如中文）正常显示
    # - 使用 Response 对象包装 JSON 数据，并设置 mimetype 为 application/json; charset=utf-8，确保客户端正确解析 JSON 数据
    return Response(json.dumps(results, ensure_ascii=False), mimetype='application/json; charset=utf-8')



if __name__ == "__main__":
    # 初始化数据库
    model_path = "/Users/azen/Desktop/llm/models/bge-base-zh-v1.5"
    data_path = "/Users/azen/Desktop/llm/RAG-Tutorial/data/recipe_corpus_full.json"
    dataset = Recipe(data_path, num=1000)
    database = MilvusDatabase(model_path, dataset)
    
    # collection_name = "food"
    # if database.client.has_collection(collection_name):
    #     database.client.load_collection(collection_name) 
    #     stats = database.client.get_collection_stats(collection_name)
    #     # 获取总的插入数据量
    #     count = stats["row_count"]
    #     print(f"集合 {collection_name} 中的数据量：", count)
    # else:
    #     print(f"集合 {collection_name} 不存在！")
    app.run(host="127.0.0.1", port=18888)

