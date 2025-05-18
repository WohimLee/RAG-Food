from pymilvus import MilvusClient, DataType
from sentence_transformers import SentenceTransformer
import torch
from tqdm import tqdm
import json
from flask import Flask, request, jsonify
app = Flask(__name__)


@app.route('/milvus', methods=['POST'])
def milvus():
    data = request.json  #

    input_text = data["input_text"]
    topk = data["topk"]

    res = database.search(input_text,topk)

    return res

class MyDocument:
    def __init__(self,path,num=10000):
        self.all_cookbook = []
        self.all_process = []
        self.all_sub_food = []
        self.all_author = []

        with open(path,encoding="utf-8") as f:

            for idx,data in tqdm(enumerate(f.readlines())):
                data = json.loads(data)
                cookbook = data["name"]
                process = "；".join(data['recipeInstructions'])
                sub_food = "；".join(data['recipeIngredient'])
                author = data["author"]

                self.all_cookbook.append(cookbook)
                self.all_process.append(process)
                self.all_sub_food.append(sub_food)
                self.all_author.append(author)

                if idx >= num:
                    break

    def __len__(self):
        return  len(self.all_cookbook)

class MyEmbModel:
    def __init__(self,emb_model_path):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(emb_model_path).to(self.device)
    def to_emb(self,sentence):
        return self.model.encode(sentence)

class MyDatabase:

    def __init__(self,emb_model_path,document_path,name="food"):
        self.name = name
        self.emb_model = MyEmbModel(emb_model_path)
        self.document = MyDocument(document_path,1000)

        if client.has_collection(self.name):
            client.drop_collection(self.name)

        schema = MilvusClient.create_schema(auto_id=False)

        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=768)
        schema.add_field(field_name="cookbook", datatype=DataType.VARCHAR, max_length=8196*2) # 3000汉字：6000 字符
        schema.add_field(field_name="process", datatype=DataType.VARCHAR, max_length=8196*2)
        schema.add_field(field_name="sub_food", datatype=DataType.VARCHAR, max_length=8196*2)
        schema.add_field(field_name="author", datatype=DataType.VARCHAR, max_length=8196)

        index_params = MilvusClient.prepare_index_params()

        index_params.add_index(
            field_name="vector",
            metric_type="COSINE",
            index_type="IVF_FLAT",
            index_name="vector_index",
            params={"nlist": 128}
        )

        client.create_collection(collection_name="food", schema=schema, index_params=index_params)

        batch_size = 100
        for i in tqdm(range(0,len(self.document) ,batch_size) ):

            end = min(i+batch_size,len(self.document) )  # end: 0,210,100  0~100, 100~200, 200~min(210,300)

            cookbooks = self.document.all_cookbook[i:end]
            processs = self.document.all_process[i:end]
            sub_foods = self.document.all_sub_food[i:end]
            authors = self.document.all_author[i:end]

            embs = self.emb_model.to_emb(cookbooks)

            batch_data = []

            for j in range(len(cookbooks)):
                batch_data.append(
                    {"id": i+j, "vector": embs[j], "cookbook": cookbooks[j], "process": processs[j], "sub_food": sub_foods[j],"author":authors[j]}
                )

            client.insert(self.name,data=batch_data)

    def search(self,content,topN=3):
        emb = self.emb_model.to_emb([content])
        search_res = client.search(collection_name="food", data=emb, limit=topN,output_fields=["cookbook", "process", "sub_food","author"])

        id,distance,cookbook,process,sub_food,author = zip(*[ (d["id"],d["distance"],d["entity"]["cookbook"],d["entity"]["process"],d["entity"]["sub_food"],d["entity"]["author"])   for d in search_res[0]])

        return {
            "id":id,
            "distance":distance,
            "sub_food":sub_food,
            "cookbook":cookbook,
            "process":process,
            "author":author,
        }

if __name__ == "__main__":

    client = MilvusClient("http://127.0.0.1:19530")
    database = MyDatabase("/Users/azen/Desktop/llm/models/bge-base-zh-v1.5", "data/recipe_corpus_full.json")
    # print(client)

    app.run(host="0.0.0.0", port=28888)

    # while True:
    #     input_Text = input("请输入：")
    #     res = database.search(input_Text)
    #     print(res)