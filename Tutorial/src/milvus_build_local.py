import torch
from tqdm import tqdm
from pymilvus import MilvusClient, DataType
from sentence_transformers import SentenceTransformer
from dataset import Recipe, DataLoader


class MilvusDatabase:
    def __init__(self, emb_model_path, dataset: Recipe, collection_name="food"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.emb_model = SentenceTransformer(emb_model_path).to(self.device)
        self.dataset = dataset
        self.collection_name = collection_name
        self.client = MilvusClient("http://127.0.0.1:19530")


        # 检查是否存在 collection
        if not self.client.has_collection(self.collection_name):
            print(f"Collection '{self.collection_name}' 不存在，正在创建...")
            self.create_collection()
        else:
            # 检查 collection 中是否有数据
            self.client.load_collection("food")
            stats = self.client.get_collection_stats(self.collection_name)
            row_count = stats["row_count"]
            if row_count == 0:
                print(f"Collection '{self.collection_name}' 存在，但数据为空，准备插入数据...")
            else:
                print(f"Collection '{self.collection_name}' 已存在，共有 {row_count} 条数据。无需重复创建。")

    def create_collection(self):
        """创建 Milvus 集合 (仅在 collection 不存在时调用)"""
        schema = MilvusClient.create_schema(auto_id=False)
        schema.add_field(field_name=self.dataset.fieldName_id, datatype=DataType.INT64, is_primary=True)
        schema.add_field(field_name=self.dataset.fieldName_vector, datatype=DataType.FLOAT_VECTOR, dim=768)
        schema.add_field(field_name=self.dataset.fieldName_name, datatype=DataType.VARCHAR, max_length=16392)
        schema.add_field(field_name=self.dataset.fieldName_recipeInstructions, datatype=DataType.VARCHAR, max_length=16392)
        schema.add_field(field_name=self.dataset.fieldName_recipeIngredient, datatype=DataType.VARCHAR, max_length=16392)
        schema.add_field(field_name=self.dataset.fieldName_author, datatype=DataType.VARCHAR, max_length=8196)

        index_params = MilvusClient.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            metric_type="COSINE",
            index_type="IVF_FLAT",
            index_name="vector_index",
            params={"nlist": 128}
        )

        self.client.create_collection(collection_name=self.collection_name, schema=schema, index_params=index_params)
        print(f"Collection '{self.collection_name}' 创建成功！")

    def insert_data(self, dataloader):
        """插入数据 (仅在 collection 数据为空时调用)"""
        for batch_data_df in tqdm(dataloader, total=len(dataloader), desc="Building Database"):
            batch_ids = batch_data_df[self.dataset.fieldName_id].tolist()
            batch_names = batch_data_df[self.dataset.fieldName_name].tolist()
            batch_instructions = batch_data_df[self.dataset.fieldName_recipeInstructions].tolist()
            batch_ingredients = batch_data_df[self.dataset.fieldName_recipeIngredient].tolist()
            batch_authors = batch_data_df[self.dataset.fieldName_author].tolist()

            # 编码名称为向量
            embs = self.emb_model.encode(batch_names)

            # 准备插入的数据
            entities = [
                {
                    self.dataset.fieldName_id: int(batch_ids[i]),
                    self.dataset.fieldName_vector: embs[i],
                    self.dataset.fieldName_name: batch_names[i],
                    self.dataset.fieldName_recipeInstructions: batch_instructions[i],
                    self.dataset.fieldName_recipeIngredient: batch_ingredients[i],
                    self.dataset.fieldName_author: batch_authors[i],
                }
                for i in range(len(batch_ids))
            ]

            # 批量插入数据
            self.client.insert(self.collection_name, entities)
            
        self.client.flush(collection_name=self.collection_name)
        print(f"数据插入完成！")

    def search(self, content, topN=3):
        emb = self.emb_model.encode([content])
        res = self.client.search(
            collection_name=self.collection_name,
            data=emb,
            limit=topN,
            output_fields=[
                self.dataset.fieldName_name,
                self.dataset.fieldName_recipeInstructions,
                self.dataset.fieldName_recipeIngredient,
                self.dataset.fieldName_author
            ]
        )

        results = []
        for item in res[0]:
            results.append({
                "id": item["id"],
                "distance": item["distance"],
                "recipeIngredient": item["entity"][self.dataset.fieldName_recipeIngredient],
                "name": item["entity"][self.dataset.fieldName_name],
                "recipeInstruction": item["entity"][self.dataset.fieldName_recipeInstructions],
                "author": item["entity"][self.dataset.fieldName_author]
            })

        return results
    
    def clear(self):
        # # 删除操作
        if self.client.has_collection(self.collection_name):
            self.client.drop_collection(self.collection_name)

if __name__ == "__main__":
    model_path = "/Users/azen/Desktop/llm/models/bge-base-zh-v1.5"
    data_path = "/Users/azen/Desktop/llm/RAG-Tutorial/data/recipe_corpus_full.json"
    batch_size = 10
    
    dataset = Recipe(data_path, num=1000)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    # 初始化数据库
    database = MilvusDatabase(model_path, dataset)

    # 仅在 collection 数据为空时插入
    stats = database.client.get_collection_stats(database.collection_name)
    if stats["row_count"] == 0:
        database.insert_data(dataloader)
        print("Milvus 数据库构建完成！")
    else:
        print("Milvus 数据库已存在，跳过数据插入。")
    

    # while True:
    #     input_Text = input("请输入：")
    #     res = database.search(input_Text)
    #     print(res)

    database.client.close()