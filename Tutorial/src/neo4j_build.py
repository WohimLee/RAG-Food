

import random
from tqdm import tqdm

from py2neo import Graph, Node, Relationship

from nodes import RecipeNodes, AuthorNodes
from utils import load_config
from dataset import read_data



class Neo4fDatabase:
    def __init__(self, address, recipeNodes, authorNodes, config):
        self.client = Graph(address)
        self.recipeNodes = recipeNodes
        self.authorNodes = authorNodes
        self.batch = config["data_batch"]
        self.create_database()

    def create_database(self):
        self.clear()
        self.create_recipe_nodes()
        self.create_author_nodes()
        self.build_relationship()
        
        return


    def create_recipe_nodes(self):
        for i in tqdm(
            range(0, len(self.recipeNodes)-1, self.batch), 
            desc="Creating Recipe Nodes"
        ):
            batch_nodes = self.recipeNodes[i:i+self.batch]
            exp = "|".join([f"batch_nodes[{idx}]" for idx in range(len(batch_nodes))])
            self.client.create(eval(exp))
        

    def create_author_nodes(self):
        for i in tqdm(
            range(0, len(self.recipeNodes)-1, self.batch), 
            desc="Creating Author Nodes"
        ):
            batch_nodes = self.authorNodes[i:i+self.batch]
            exp = "|".join([f"batch_nodes[{idx}]" for idx in range(len(batch_nodes))])
            self.client.create(eval(exp))
    
    def build_relationship(self):
        all_relationships = []
        for i in range(len(self.recipeNodes)):
            node1 = self.recipeNodes[i]
            node2 = self.authorNodes[i]
            relationship = Relationship(node1, "Author", node2)
            all_relationships.append(relationship)
        
        for i in tqdm(
            range(0, len(all_relationships)-1, self.batch), 
            desc="Buiding Relationship"
        ):
            batch_relationships = all_relationships[i:i+self.batch]
            exp = "|".join([f"batch_relationships[{idx}]" for idx in range(len(batch_relationships))])
            self.client.create(eval(exp))

    def clear(self):
        cmd = "match (n) detach delete (n)" # 删除 Neo4j 数据库中的所有节点和关系
        self.client.run(cmd) 




if __name__ == "__main__":
    address = "bolt://localhost:7687"

    data_path = "data/recipe_corpus_full.json"
    config_file = "/Users/azen/Desktop/llm/RAG-Tutorial/Meituan-RAG/4.Neo4j/src/config.json"
    config = load_config(config_file)

    all_data_df, fieldNames = read_data(config["data_path"], num=config["num_samples"])
    
    recipeNodes = RecipeNodes(all_data_df, config)
    authorNodes = AuthorNodes(all_data_df, config)
    
    neo4jDatabase = Neo4fDatabase(address, recipeNodes, authorNodes, config)


    pass