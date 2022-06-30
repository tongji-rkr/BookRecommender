import numpy as np
import torch

def read_item_index_to_entity_id_file():
    file = '../data/book/item_index2entity_id.txt'
    isbn_list=dict()
    item_cnt=0
    for line in open(file, encoding='utf-8').readlines():
        item_index = line.strip().split('\t')[0]
        isbn_list[item_cnt]=item_index
        item_cnt+=1
    return isbn_list

def test(model_path,user_id,n_item):
    users=(int(user_id)*np.ones(n_item)).astype(np.int16)
    items=np.arange(0,n_item,1).astype(np.int16)
    heads=items
    feed=np.array((users, items, heads))
    feed= torch.Tensor(feed).long()
    mkr=torch.load(model_path)
    with torch.set_grad_enabled(False):
        y_scores = mkr.forward("rs", feed)
    y_scores=np.array(y_scores)
    item_dict=dict(zip(items,y_scores))
    res_list=sorted(item_dict.items(),key=lambda kv:kv[1],reverse=True)
    res_list=res_list[0:20]
    print("book_id,score")
    print(res_list[0:10])
    isbn_list=read_item_index_to_entity_id_file()
    ans_list=[]
    for tp in res_list:
        item_id=int(tp[0])
        isbn=isbn_list[item_id]
        ans_list.append(isbn)
    return ans_list



