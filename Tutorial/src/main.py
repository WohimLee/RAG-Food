import gradio as gr
from zhipuai import ZhipuAI
from py2neo import Graph, Node, Relationship
import requests
import time
import random


def get_zhipu_response(prompt,model="glm-4-plus"):

    zhipu_client = ZhipuAI(api_key="0f56bcd3ce36d22b5b6564de4faeebfe.nvc4AlZb8rw1WhFG")

    response = zhipu_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的建议。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        top_p=0.7,
        temperature=0.95,
        max_tokens=1024,

    )
    res = response.choices[0].message.content
    return res


def get_intent(prompt):
    intent_prompt = f"""你需要从一段文本中，识别用户的意图属于以下哪种？如果都不属于，请输出：无。
意图1：询问菜谱的制作方式
意图2：询问菜谱所需要的食材
意图3：询问菜谱的厨师是谁？

样例如下：
```
输入：我想吃汉堡，请问该怎么做？
输出结果：意图1

输入：这个少油少糖版本的番茄炒蛋好好吃啊，是哪个厨师做的呢？
输出结果：意图3

输入：请问红烧茄子需要购买些什么，才能做出来？
输出结果：意图2

输入：李白是谁？
输出结果：无
```
输入：{prompt}
输出结果："""

    # response = get_answer(intent_prompt)
    # intent = ""
    #
    # for trunk in response:
    #     intent += trunk.choices[0].delta.content

    intent = get_zhipu_response(intent_prompt)
    if intent == "无":
        return 0

    try:
        intent = int(intent[-1])
    except:
        return 0

    return intent


def get_recipe_name(prompt):
    recipe_prompt = f"""请从输入的文本中，提取出连续、完整的一个菜名或菜谱，该菜名包含中餐、西餐，如果没有任何菜名或菜谱，输出：无。
参考样例如下：
```
输入：秋天了，西红柿浓汤炖肥牛，满满的番茄味儿，配上金针菇，暖暖的，可以配一大碗米饭，秋日的午后惬意十足。
输出：西红柿浓汤炖肥牛

输入：牛肉炖土豆该怎么做？
输出：牛肉炖土豆

输入：明天会下雨吗？
输出：无
```
输入：{prompt}
输出："""

    recipe_name = get_zhipu_response(recipe_prompt)

    return recipe_name

def stream_long_string(input_string):
    # 用一个生成器产生流式数据
    for char in input_string:
        time.sleep(random.random() / 20)  # 模拟延迟
        yield char

def query_neo4j(cmd):
    # 提取公共的 Neo4j 查询逻辑
    res = neo4j_client.run(cmd)
    return res.data()

def intent1_response(recipe_name):
    cmd = f"match (a:菜谱) where a.名称='{recipe_name}' return a"
    nodes = query_neo4j(cmd)
    if nodes:
        result = ""
        for node in nodes:
            result += node["a"]["制作方式"] + "\n*********************\n"
        # yield from stream_long_string(result)  # 逐字符生成结果

def intent2_response(recipe_name):
    cmd = f"match (a:菜谱) where a.名称='{recipe_name}' return a"
    nodes = query_neo4j(cmd)
    if nodes:
        for node in nodes:
            result = node["a"]["食材"] + "\n*********************\n"
            yield result  # 逐条生成结果

def intent3_response(recipe_name):
    cmd = f"match (a:菜谱 {{名称:'{recipe_name}'}})-[r:作者]->(b:厨师) return b"
    nodes = query_neo4j(cmd)
    if nodes:
        result = ""
        for node in nodes:
            result += node["b"]["姓名"] + "\n"
            result += node["b"]["编号"] + "\n"
            result += node["b"]["性别"] + "\n"
            result += "\n*********************\n"
        yield from stream_long_string(result)  # 逐字符生成结果

def answer(prompt):
    intent = get_intent(prompt)
    if intent == 0:
        return "无法回答"
    
    recipe_name = get_recipe_name(prompt)

    match intent:
        case 1:
            gen = intent1_response(recipe_name)
        case 2:
            gen = intent2_response(recipe_name)
        case 3:
            gen = intent3_response(recipe_name)
        case _:
            return "无法回答"

    # 从生成器中获取所有值并拼接成字符串
    return "".join(list(gen))


if __name__ =="__main__":
    # neo4j_client = Graph("[buding.onehot-tech.com]:7687", auth="neo4j", password="buding666")
    # neo4j_client = Graph("bolt://localhost:7687", auth=("neo4j", "your_password"))
    neo4j_client = Graph("bolt://localhost:7687")

    iface = gr.Interface(
        fn=answer,
        inputs=gr.Textbox(),
        outputs=gr.Markdown()
    )

    iface.launch(server_name="0.0.0.0")

    # print(answer("红烧鱼怎么做"))

