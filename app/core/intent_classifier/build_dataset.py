import py2neo
import json
import jieba.posseg as psg
from zhipuai import ZhipuAI
from tqdm import tqdm

def get_zhipuai(prompt):

    client = ZhipuAI(api_key="0f56bcd3ce36d22b5b6564de4faeebfe.nvc4AlZb8rw1WhFG")

    response = client.chat.completions.create(
        model="glm-4-plus",
        messages=[
            {
                "role": "system",
                "content": "你是一个美食专家，你的任务是为用户提供专业、准确、有见地的建议。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        top_p=1.0,
        temperature=1.0,
        max_tokens=1024,
        stream=True
    )
    result = ""
    for trunk in response:
        result += trunk.choices[0].delta.content
    return result

if __name__ == "__main__":

    for i in tqdm(range(20)):
#         answer = get_zhipuai("""假设你需要向美食专家询问一道菜的做法，请模仿并适当修改以下句式，发出至少20个其他食谱或菜品的制作方式提问，并具有一定的吸引力，无需输出其他内容。
# 家里人想吃牛肉炖土豆了，告诉我怎么做吧
# 我想吃汉堡，给我推荐的做法
# 输出格式：["xxx","xxx","xxx",...]""")

#         answer = get_zhipuai("""假设你需要根据食材，向美食专家询问可以做什么菜，请模仿以下句式，根据食材或者配料发出至少20个其他食谱或菜品的制作方式提问，并具有一定的吸引力，适当的更换句式，无需输出其他内容。
# 鱼块和生姜可以做啥
# 番茄与茄子能做啥下饭菜
# 家里冰箱只剩点羊肉了，厨房只有盐和一点酱油，能做什么？
# 输出格式：["xxx","xxx","xxx",...]""")

#         answer = get_zhipuai("""假设你需要向美食专家询问一道菜所需要的配料，请模仿并适当更改以下句式，根据其他菜谱或者菜名发出至少20个提问，并具有一定的吸引力，适当的更换句式，无需输出其他内容。
# 糖醋鲤鱼需要什么配料
# 我要准备材料才能做出宫保鸡丁？
# 做一个好吃的扬州炒饭，要啥食材？
# 输出格式：["xxx","xxx","xxx",...]""")

        answer = get_zhipuai("""假设你需要某一道菜的厨师是谁？，请模仿以下句式，发出至少20个提问，并具有一定的吸引力，适当的更换句式，无需输出其他内容。
样例如下：```
店里的扬州炒饭是哪个厨师的做的？
西街口的东坡肉是谁的杰作？
听说吃步行街的羊肉炸串很好吃，不知道是谁做的？```
输出格式：["xxx","xxx","xxx",...]""")

        try :
            answer = eval(answer)
        except:
            continue

        with open("data/all_data.txt", "a+", encoding="utf-8") as f:
            for text in answer:
                f.write(f"{text} 3\n")



