

import json
import numpy as np
import pandas as pd
from tqdm import tqdm


from ..utils.config import load_config


def read_data(file, num=None):
    # df = pd.read_json(file, lines=True, nrows=num)

    with open(file, "r", encoding="utf-8") as f:
        all_data = f.readlines()[:num]

    fieldNames = list(eval(all_data[0]).keys())
    df = pd.DataFrame(columns=['id'] + fieldNames)

    # 按条插入数据
    for i, item in tqdm(enumerate(all_data), total=len(all_data), desc="Reading Data"):
        data = json.loads(item)
        item_with_id = {'id': i, **data}
        df = pd.concat([df, pd.DataFrame([item_with_id])], ignore_index=True)

    df = df.dropna()
    df[fieldNames[3]] = df[fieldNames[3]].apply(lambda x: "；".join(x))
    df[fieldNames[4]] = df[fieldNames[4]].apply(lambda x: "；".join(x))

    df = df[df['name'].str.len() <= 20]
    df = df.astype('string').fillna('unknown')
    return df, fieldNames


class Recipe:
    def __init__(self, all_data_df: pd.DataFrame):
        self.all_data_df = all_data_df

        # for item in self.fieldNames:
        #     setattr(self, f"fieldName_{item}", item)

    def __len__(self):
        return len(self.all_data_df)

    def __getitem__(self, idx):
        return self.all_data_df.iloc[idx]
    

class DataLoader:
    def __init__(self, dataset: Recipe, batch_size, shuffle=False):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.indice = np.arange(len(dataset))

    def __len__(self):
        return int(np.ceil(len(self.dataset) / self.batch_size))

    def __iter__(self):
        self.cursor = 0
        if self.shuffle:
            np.random.shuffle(self.indice)
        return self
    
    def __next__(self):
        if self.cursor >= len(self.dataset):
            raise StopIteration
        
        batch_indice = self.indice[self.cursor: self.cursor+self.batch_size]
        batch_data_df = self.dataset.all_data_df.iloc[batch_indice]
        self.cursor += self.batch_size
        return batch_data_df

