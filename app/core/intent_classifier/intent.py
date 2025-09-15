import random

import torch
from transformers import AutoTokenizer,AutoModel
from torch.utils.data import DataLoader,Dataset
from tqdm import tqdm
def read_data(path,test_rate=0.1):
    with open(path,encoding="utf-8") as f:
        all_data = f.read().split("\n")
        random.shuffle(all_data)

    all_text = []
    all_label = []

    for data in all_data:
        data_s = data.split(" ")
        try:
            text,label = data_s
            label = int(label)
        except:
            continue
        all_text.append(text)
        all_label.append(label)

    test_len = int(len(all_data) * test_rate)

    test_text = all_text[:test_len]
    test_label = all_label[:test_len]

    train_text = all_text[test_len:]
    train_label = all_label[test_len:]

    return train_text,train_label,test_text,test_label

class MyDataset(Dataset):
    def __init__(self,all_text,all_label):
        self.all_text = all_text
        self.all_label = all_label

    def __len__(self):
        return len(self.all_text)

    def __getitem__(self, index):
        # text = "你需要对以下内容做文本分类，文本为：" + text + "\n最后的类别为："

        text = self.all_text[index]
        label = self.all_label[index]

        tokens = tokenizer.encode(text)

        return tokens,label,len(tokens)

def collect_function(batch_data):

    batch_token,batch_label,batch_len = zip(*batch_data)
    max_len = max(batch_len)

    batch_new_token = []

    for i in range(len(batch_token)):
        new_token = batch_token[i] + (max_len-batch_len[i]) * [tokenizer.pad_token_id]
        batch_new_token.append(new_token)
    return torch.tensor(batch_new_token),torch.tensor(batch_label)

class MyMode(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.base_model = AutoModel.from_pretrained("../model/DeepSeek-R1-Distill-Qwen-1.5B")  # 3.3 * (20~30)

        self.cls = torch.nn.Linear(1536,4)

        for name,param in self.base_model.named_parameters():
            # if "embed_tokens" in name:
            #     param.requires_grad = True
            # else:
                param.requires_grad = False

        self.loss_fun = torch.nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)


    def forward(self,x,label=None):


        output,_ = self.base_model.forward(x,attention_mask=(x!=151643),return_dict=False)
        output = torch.mean(output,dim=1)
        predict = self.cls(output)

        if label is not None:
            loss = self.loss_fun(predict,label)

            return loss
        return torch.argmax(predict,dim=-1)


if __name__ == "__main__":

    random.seed(314)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    train_text,train_label,test_text,test_label = read_data("all_data.txt")

    tokenizer = AutoTokenizer.from_pretrained("../model/DeepSeek-R1-Distill-Qwen-1.5B")

    batch_size = 8
    epoch = 1
    lr = 0.001

    train_dataset = MyDataset(train_text,train_label)
    train_dataloader = DataLoader(train_dataset,batch_size,shuffle=False,collate_fn=collect_function)

    test_dataset = MyDataset(test_text,test_label)
    test_dataloader = DataLoader(test_dataset,batch_size,shuffle=False,collate_fn=collect_function)

    model = MyMode().to(device)
    opt = torch.optim.AdamW(model.parameters(),lr=lr)

    for e in range(epoch):
        for batch_token,batch_label in tqdm(train_dataloader):
            batch_token, batch_label = batch_token.to(device),batch_label.to(device)

            loss = model(batch_token,batch_label)

            loss.backward()
            opt.step()
            opt.zero_grad()
            # break

        right_num = 0

        for batch_token, batch_label in test_dataloader:
            batch_token, batch_label = batch_token.to(device),batch_label.to(device)

            predict = model.forward(batch_token)

            right_num += int(torch.sum(predict == batch_label))

        acc = right_num/len(test_dataset)
        print(f"acc:{acc}")

        # # torch.save(model.state_dict(), 'model_state_dict.pth')
        torch.save(model, 'model.pth')

        # # 将模型的参数和状态转换为 FP16，然后保存它
        # for param in model.parameters():
        #     param.data = param.data.half()
        #     if param.grad is not None:
        #         param.grad.data = param.grad.data.half()
        #
        # torch.save(model.state_dict(), 'model_state_dict_fp16.pth')
