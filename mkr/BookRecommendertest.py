from test import test

model_path='../model/book.pth'
user_id=1
n_item=10000
test_list=test(model_path,user_id,n_item)
print("推荐图书的ISBN")
print(test_list[0:10])


