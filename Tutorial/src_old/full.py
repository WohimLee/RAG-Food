import gradio as gr
from zhipuai import ZhipuAI
from py2neo import Graph, Node, Relationship
import requests
import time
import random

def get_answer(prompt,model="glm-4-plus"):

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
        stream=True
    )
    # result = ""
    for trunk in response:
        yield trunk.choices[0].delta.content
    # return result
    # return response

def get_cookbook(prompt):
    cookbook_prompt = f"""请从输入的文本中，提取出连续、完整的一个菜名或菜谱，该菜名包含中餐、西餐，如果没有任何菜名或菜谱，输出：无。
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

    cookbook = "".join(get_answer(cookbook_prompt))

    return cookbook

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

    intent = "".join(get_answer(intent_prompt))
    if intent == "无":
        return 0

    try:
        intent = int(intent[-1])
    except:
        return 0

    return intent


def stream_long_string(input_string):
    # 用一个生成器产生流式数据
    for char in input_string:
        time.sleep(random.random()/20)  # 模拟延迟
        yield char

def answer(prompt):

    rate = 0.8

    intent = get_intent(prompt)
    if intent == 0:
        return "无法回答"

    cookbook = get_cookbook(prompt)

    result = ""

    if intent == 1: # 查询菜谱的制作方式
        cmd = f"match (a:菜谱) where a.名称='{cookbook}'  return a"
        res = neo4j_client.run(cmd)
        nodes = res.data()

        if len(nodes) != 0:
            for node in nodes:
                result += node["a"]["制作方式"]
                result += "\n*********************\n"
                # yield result
            gen = stream_long_string(result)
            output_str = ""
            for char in gen:
                output_str += char
                yield output_str

    elif intent == 2: # 查询菜谱的食材
        cmd = f"match (a:菜谱) where a.名称='{cookbook}'  return a"
        res = neo4j_client.run(cmd)
        nodes = res.data()

        if len(nodes) != 0:
            for node in nodes:
                result += node["a"]["食材"]
                result += "\n*********************\n"
                yield result
            gen = stream_long_string(result)
            output_str = ""
            for char in gen:
                output_str += char
                yield output_str

    else: # 查询菜谱的作者信息
        cmd = f"match (a:菜谱 {{名称:'{cookbook}'}})-[r:作者]->(b:厨师)  return b"
        res = neo4j_client.run(cmd)
        nodes = res.data()

        if len(nodes) != 0:
            for node in nodes:
                result += node["b"]["姓名"] + "\n"
                result += node["b"]["编号"] + "\n"
                result += node["b"]["性别"]+"\n"
                result += "\n*********************\n"
                # yield result
            gen = stream_long_string(result)
            output_str = ""
            for char in gen:
                output_str += char
                yield output_str

    if len(result) == 0:

        data = {"input_text":cookbook,"topk":1}

        milvus_res = requests.post("http://127.0.0.1:28888/milvus",json=data,headers={"Content-Type":"application/json"})

        if milvus_res.status_code == 200:
            milvus_res = milvus_res.json()
            sim_score = milvus_res["distance"][0]

            if sim_score > rate:
                if intent==1 or intent==2:
                    cmd = f" match (a:菜谱 {{名称: '{milvus_res['cookbook'][0]}' }} )  return a"
                else:
                    cmd = f" match (a:厨师 {{编号: '{milvus_res['author'][0]}' }} )  return a"

                res = neo4j_client.run(cmd)
                athor_nodes = res.data()

                if len(athor_nodes)!=0:
                    node = athor_nodes[0]

                    if intent == 1:
                        result += node["a"]["制作方式"] + "\n"

                        modify_prompt = f"""假设你是一个资深的美食博主，用户的`输入`和`输出`存在不匹配的问题，你需要根据用户的`输入`，对`输出`进行适当的修改，要求如下：
1. 尽量较少的修改`输出`内容
2. `输入`和`输出`必须是复合逻辑与事实
3. 修改后的`输出`必须能用于解答`输入`的问题
样例如下：
```
`输入`：咖喱羊肉饭怎么做？
`输出`：1.胡萝卜洗净切小块，土豆洗净切小块，洋葱洗净切小块;2.鸡胸肉去骨切丁，1勺料酒，少许盐，糖，生姜，食用油腌制一会儿；起锅热油，把鸡肉倒下去，小火翻炒；成品 ，非常美味可口。
修改后的输出：1.胡萝卜洗净切小块，土豆洗净切小块，洋葱洗净切小块;2.羊肉洗净切成小丁，1勺料酒，少许盐，糖，生姜，食用油腌制一会儿；起锅热油，把羊肉倒下去，小火翻炒；成品 ，非常美味可口。

`输入`：可可芒果曲奇需要什么配料
`输出`：100g黄油；65g糖粉；100g常温淡奶油25℃左右(冬天需温热到45℃）；120g低筋面粉；16g可可粉；4g速溶咖啡粉；50g玉米淀粉；10g杏仁粉；若干巧克力豆
修改后的输出：100g黄油；65g糖粉；100g常温淡奶油25℃左右(冬天需温热到45℃）；120g低筋面粉；16g可可粉；适量的芒果肉；50g玉米淀粉；10g杏仁粉；若干巧克力豆
```
`输入`：{prompt}
`输出`：{result}
修改后的输出："""

                        result = ""
                        for text in get_answer(modify_prompt):
                            result += text
                            yield result

                    elif intent == 2:
                        result += node["a"]["食材"] + "\n"

                        modify_prompt = f"""假设你是一个资深的美食博主，用户的`输入`和`输出`存在不匹配的问题，你需要根据用户的`输入`，对`输出`进行适当的修改，要求如下：
1. 尽量较少的修改`输出`内容
2. `输入`和`输出`必须是复合逻辑与事实
3. 修改后的`输出`必须能用于解答`输入`的问题
样例如下：
```
`输入`：咖喱羊肉饭怎么做？
`输出`：1.胡萝卜洗净切小块，土豆洗净切小块，洋葱洗净切小块;2.鸡胸肉去骨切丁，1勺料酒，少许盐，糖，生姜，食用油腌制一会儿；起锅热油，把鸡肉倒下去，小火翻炒；成品 ，非常美味可口。
修改后的输出：1.胡萝卜洗净切小块，土豆洗净切小块，洋葱洗净切小块;2.羊肉洗净切成小丁，1勺料酒，少许盐，糖，生姜，食用油腌制一会儿；起锅热油，把羊肉倒下去，小火翻炒；成品 ，非常美味可口。

`输入`：可可芒果曲奇需要什么配料
`输出`：100g黄油；65g糖粉；100g常温淡奶油25℃左右(冬天需温热到45℃）；120g低筋面粉；16g可可粉；4g速溶咖啡粉；50g玉米淀粉；10g杏仁粉；若干巧克力豆
修改后的输出：100g黄油；65g糖粉；100g常温淡奶油25℃左右(冬天需温热到45℃）；120g低筋面粉；16g可可粉；适量的芒果肉；50g玉米淀粉；10g杏仁粉；若干巧克力豆
```
`输入`：{prompt}
`输出`：{result}
修改后的输出："""

                        result = ""
                        for text in get_answer(modify_prompt):
                            result += text
                            yield result

                    else:
                        result += node["a"]["姓名"] + "\n"
                        result += node["a"]["编号"] + "\n"
                        result += node["a"]["性别"] + "\n"
                    yield result

    if len(result) == 0:
        for text in get_answer(prompt):
            result += text
            yield result



if __name__ =="__main__":
    neo4j_client = Graph("[buding.onehot-tech.com]:7687", auth="neo4j", password="buding666")
    iface = gr.Interface(
        fn=answer,
        inputs=gr.Textbox(),
        outputs=gr.Markdown()
    )

    iface.launch(server_name="0.0.0.0")