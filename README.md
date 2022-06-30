## BookRecommender

基于知识图谱的图书推荐系统

### MKR模型
由于推荐系统(RS)中的物品和知识图谱(KG)中的实体存在重合，MKR模型中使用多任务学习的框架，将推荐系统和知识图谱视为两个分离但是相关的任务，进行交替学习。
推荐部分的输入是用户和物品的特征表示，用户点击对应物品的估值概率作为输出。
知识图谱特征学习部分的输入是三元组(h,r,t)中的头节点h和关系r，预测的尾节点t作为输出。
推荐系统和知识图谱这两部分通过“交叉特征共享单元”(cross-feature-sharing unit)进行特征的交叉推测，该单元的目的是让两个模块交换信息，让两者获取更多的信息，弥补自身信息稀疏性。
推荐系统的训练目的是预测用户点击率，实际上是一个二分类问题。

### flask后端+前端模块
在这个项目中，我在后端使用flask+mysql，前端使用html+css+js进行网站的设计

### mysql模块
#### TABLE User
> 用户ID，密码，所在地区，年龄

```
User
{
    "Id":       	"用户ID"
    "UserPassword": "密码"
    "Location":     "所在地区"
    "Age":        	"年龄"
}
```

#### TABLE Books
> 书ID、ISBN编号、书名、作者、出版时间、出版社、图片URL1(模糊)、图片URL2(中等)、图片URL3(清晰)

```
Books
{
    "Id":       	"书ID"
    "ISBN":    		"ISBN编号"
    "Title":        "书名"
    "Author":       "作者"
    "Year":        	"出版时间"
    "Publisher":    "出版社"
    "ImageS":       "图片URL1(模糊)"
    "ImageM":       "图片URL2(中等)"
    "ImageL":       "图片URL3(清晰)"
}
```

#### TABLE Bookrating
> 用户ID、书ID、评分

```
Bookrating
{
    "UserId":     	"用户ID"
    "ItemId": 		"书ID"
    "Rating":		"评分"
}
```
### 文件夹介绍
data:存储训练需要的文件
mkr:MKR模型及训练、测试的代码文件
model:训练得到的模型文件
pic:模型、算法图片及matlab根据数据得到的曲线图
server:flask后端代码、yaml配置文件和前端文件	

### 测试用例
```txt
cd ./mkr
python BookRecommendertest.py
```

### 如何配置环境及数据库
1.配置mysql环境，分别运行./data/book/sql文件夹中的createtable.sql、book_mysql.sql、user_mysql.sql和ratings.sql进行表的建立以及初始数据的导入
2.配置flaks环境，修改config.yaml中的配置信息
3.在mkr文件夹中加入.flaskenv文件并安装相关python库
4.之后在/BookRecommender文件夹下
```txt
cd ./mkr
python -m flask run
```

### 参考文献
[Multi-Task Feature Learning for Knowledge Graph Enhanced Recommendation](https://arxiv.org/abs/1901.08907)
