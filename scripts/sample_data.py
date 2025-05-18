
import os

from app.utils.config import load_config
from app.data_loader.dataset import read_data

def sample_data(file, num=None):
    # df = pd.read_json(file, lines=True, nrows=num)

    with open(file, "r", encoding="utf-8") as f:
        samples = f.readlines()[:num]

    return samples

if __name__ == "__main__":
    config_file = "/Users/azen/Desktop/llm/RAG-Food/app/config.json"
    config = load_config(config_file)

    num = 2000
    samples = sample_data(config["raw_data"], num=num)

    save_name = os.path.join(config["workspace"], "data")
    with open(f"{save_name}/samples_{num}.json", "w") as f:
        f.write("".join(samples))


    pass