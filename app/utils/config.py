import json

def load_config(config_file):
    # 读取 JSON 文件
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config



if __name__ == "__main__":
    config_file = "/Users/azen/Desktop/llm/RAG-Food/app/config.json"
    config = load_config(config_file)