
import random
from py2neo import Node

from utils import load_config
from dataset import Recipe, read_data

class RecipeNodes:
    def __init__(self, all_data_df, config):
        self.all_data_df = all_data_df
        self.config = config

    def __len__(self):
        return len(self.all_data_df)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            # 处理切片操作
            return [self._get_node(i) for i in range(*idx.indices(len(self)))]
        else:
            # 处理单个索引操作
            return self._get_node(idx)

    def _get_node(self, idx):
        node = Node(
            "Recipe",
            Name=self.all_data_df.iloc[idx][self.config["tags"]["Name"]],
            Ingredient=self.all_data_df.iloc[idx][self.config["tags"]["Ingr"]],
            Instruction=self.all_data_df.iloc[idx][self.config["tags"]["Inst"]]
        )
        return node
    

class AuthorNodes:
    def __init__(self, all_data_df, config):
        self.all_data_df = all_data_df
        self.config  = config

    def __len__(self):
        return len(self.all_data_df)
    
    def __getitem__(self, idx):
        if isinstance(idx, slice):
            # 处理切片操作
            return [self._get_node(i) for i in range(*idx.indices(len(self)))]
        else:
            # 处理单个索引操作
            return self._get_node(idx)
    
    def _get_node(self, idx):
        node = Node(
            "Author",
            Name = self.generate_random_name(),
            Gender = random.choice(["男","女"]),
            Number = self.all_data_df.iloc[idx][self.config["tags"]["Auth"]]
        )
        return node
    
    def generate_random_name(self):

        # 随机选择一个姓氏
        surnames = [
            '赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈',
            '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许',
            '何', '吕', '施', '张', '孔', '曹', '严', '华', '金', '魏',
            '陶', '姜', '戚', '谢', '邹', '喻', '柏', '水', '窦', '章',
            '云', '苏', '潘', '葛', '奚', '范', '彭', '郎', '鲁', '韦',
            '昌', '马', '苗', '凤', '花', '方', '俞', '任', '袁', '柳',
            '酆', '鲍', '史', '唐', '费', '廉', '岑', '薛', '雷', '贺',
            '倪', '汤', '滕', '殷', '罗', '毕', '郝', '邬', '安', '常',
            '乐', '于', '时', '傅', '皮', '卞', '齐', '康', '伍', '余',
            '元', '卜', '顾', '孟', '平', '黄', '和', '穆', '萧', '尹'
        ]

        # 常见名字列表
        given_names = [
            '伟', '芳', '娜', '敏', '静', '强', '磊', '军', '洋', '勇',
            '艳', '杰', '娟', '涛', '明', '超', '秀', '丽', '霞', '平',
            '刚', '桂', '芬', '玲', '红', '莉', '波', '亮', '建', '梅',
            '俊', '花', '飞', '云', '慧', '颖', '琳', '婷', '紫', '青',
            '鹏', '娇', '阳', '兰', '燕', '松', '文', '利', '哲', '兴'
        ]
        surname = random.choice(surnames)
        # 随机选择名字的长度，可能是 1 个字或 2 个字
        name = random.choice(given_names)

        code = random.randint(0x4e00, 0x9fa5)

        return surname + name + chr(code)



if __name__ == "__main__":
    config_file = "/Users/azen/Desktop/llm/RAG-Tutorial/Meituan-RAG/4.Neo4j/src/config.json"
    
    config = load_config(config_file)
    all_data_df, fieldNames = read_data(config["data_path"], num=config["num_samples"])
    
    
