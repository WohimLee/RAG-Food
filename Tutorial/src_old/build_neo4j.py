      
from py2neo import Graph,Node,Relationship
import json
from tqdm import  tqdm
import random

def read_data(path,num=None):
    with open(path,encoding="utf-8") as f:
        all_data = f.readlines()

    new_cookbook,new_process,new_sub_food,new_author = [],[],[],[]

    for data in all_data:
        data = json.loads(data)
        try:
            cookbook,process,sub_food,author = data["name"],"；".join(data["recipeInstructions"]),"；".join(data["recipeIngredient"]),data["author"]
        except:
            continue

        new_cookbook.append(cookbook)
        new_process.append(process)
        new_sub_food.append(sub_food)
        new_author.append(author)
    if num is not  None:
        return new_cookbook[:num],new_process[:num],new_sub_food[:num],new_author[:num]
    return new_cookbook,new_process,new_sub_food,new_author

def build_cookbook(all_cookbook,all_process,all_sub_food):
    all_nodes = []
    for i in range(len(all_cookbook)):
        node = Node("菜谱",名称=all_cookbook[i],食材=all_sub_food[i],制作方式=all_process[i])
        # client.create(node)
        all_nodes.append(node)

    batch_size = 99 # 10

    for i in tqdm(range(0,len(all_nodes),batch_size),desc="创建食谱节点中"):
        batch_nodes = all_nodes[i:i+batch_size] # list1 = [1,2,3]   list1[0:100]
        client.create(eval("|".join([f"batch_nodes[{j}]" for j in range(len(batch_nodes))])))


    return all_nodes

def random_chinese_char():
    # 随机生成一个在汉字Unicode编码范围内的编码值
    code = random.randint(0x4e00, 0x9fa5)
    # 将编码值转换为对应的中文字符
    return chr(code)

def generate_random_name():
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

    return surname + name + random_chinese_char()

def build_author(all_author):
    all_nodes = []
    author_id = list(set(all_author))
    author_map = {}

    new_all_author = []

    for aut in author_id:
        r_n = generate_random_name()
        sex = random.choice(["男","女"])
        author_map[aut] = (r_n,sex)

    for aut in all_author:
        new_all_author.append((aut,*author_map[aut]))

    for aut in new_all_author:
        node = Node("厨师", 姓名=aut[1], 性别=aut[2], 编号=aut[0])
        # client.create(node)
        all_nodes.append(node)

    batch_size = 99

    for i in tqdm(range(0,len(all_nodes),batch_size),desc="创建厨师节点中"):
        batch_nodes = all_nodes[i:i+batch_size] # list1 = [1,2,3]   list1[0:100]
        client.create(eval("|".join([f"batch_nodes[{j}]" for j in range(len(batch_nodes))])))

    return all_nodes

def build_relationship(cookbook_nodes,author_nodes):

    global client

    all_rel = []

    for node1,node2 in zip(cookbook_nodes,author_nodes):
        rel = Relationship(node1, "作者", node2)
        # client.create(rel)
        all_rel.append(rel)

    batch_size = 99
    for i in tqdm(range(0,len(all_rel),batch_size),desc="创建关系中"):
        batch_rel = all_rel[i:i+batch_size] # list1 = [1,2,3]   list1[0:100]
        client.create(eval("|".join([f"batch_rel[{j}]" for j in range(len(batch_rel))])))

if __name__ == "__main__":
    client = Graph("[buding.onehot-tech.com]:7687")

    cmd = "match (n) detach  delete n"
    client.run(cmd)

    all_cookbook,all_process,all_sub_food,all_author = read_data("data/recipe_corpus_full.json",1000)

    cookbook_nodes = build_cookbook(all_cookbook,all_process,all_sub_food)

    author_nodes = build_author(all_author)

    build_relationship(cookbook_nodes,author_nodes)



    