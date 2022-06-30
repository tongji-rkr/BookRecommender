from utils import load_config
from logger import setup_log
from flask import Flask, request, render_template, session, redirect, url_for
from utils import mysql
import math
import numpy as np
from test import test
from train import train
from data_loader import load_kg,dataset_split

config = load_config()
logger = setup_log(__name__)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'nlp'
mysql = mysql(config['mysql'])
item_num=0
operation_num=10

@app.route("/")
def root():
    """
    主页
    :return: home.html
    """
    login, userid = False, ''
    if 'userid' in session:
        login, userid = True, session['userid']
    # 热门书籍
    hot_books = []
    sql = "SELECT ISBN, title, Author, Year, Publisher, ImageL FROM Books where ISBN = '" + \
          "' or ISBN = '".join(config['bookid']) + "'"
    print(sql)

    try:
        hot_books = mysql.fetchall_db(sql)
        hot_books = [[v for k, v in row.items()] for row in hot_books]

    except Exception as e:
        logger.exception("select hot books error: {}".format(e))

    return render_template('Index.html',
                           login=login,
                           books=hot_books,
                           useid=userid,
                           name = "index")


@app.route("/guess")
def guess():
    """
    猜你喜欢
    :return: Index.html
    """
    login, userid, error = False, '', False
    if 'userid' in session:
        login, userid = True, session['userid']
    # 推荐书籍
    guess_books = []
    if login:
        sql = """select e.ISBN,e.Title,e.Author,e.Year,e.Publisher,e.ImageL from Books e
                inner join (select  c.ItemId,sum(c.Rating) as score  
                            from Bookrating c 
                            group by c.ItemId
                            order by score desc 
                            limit 16) f
                on e.Id = f.ItemId""".format(session['userid'])
        print(sql)

        try:
            guess_books = mysql.fetchall_db(sql)
            print(guess_books)
            guess_books = [[v for k, v in row.items()] for row in guess_books]

        except Exception as e:
            logger.exception("select guess books error: {}".format(e))
    return render_template('Index.html',
                           login=login,
                           books=guess_books,
                           useid=userid,
                           name = "guess")

def load_data(data):
    n_user = len(set(data[:, 0]))
    n_item = len(set(data[:, 1]))
    for i in range(len(data)):
        if data[i][2]>0.5:
            data[i][2]=1
        else:
            data[i][2]=0
    print(n_user)
    print(n_item)
    train_data, test_data = dataset_split(data)
    n_entity, n_relation, kg = load_kg()
    print("data loaded.")
    return n_user, n_item, n_entity, n_relation, train_data, test_data, kg


@app.route("/recommend")
def recommend():
    """
    推荐页面
    :return: Index.html
    """
    global item_num
    global operation_num
    login, userid, error = False, '', False
    if 'userid' in session:
        login, userid = True, session['userid']
    # 推荐书籍
    recommend_books=[]
    data=[]
    if login:
        if operation_num>=10:
            sql = "SELECT * FROM Bookrating" 
            data = mysql.fetchall_db(sql)
            data = np.array([[v for k, v in row.items()] for row in data])
            mkr_data=load_data(data)
            item_num=mkr_data[1]
            train(config['model'],mkr_data)
            operation_num=0
        model_path='../model/book.pth'
        recommend_books=test(model_path,userid,item_num)
        #print(recommend_books)
        sql = "select ISBN, title, Author, Year, Publisher, ImageL from Books where ISBN = '" + \
          "' or ISBN = '".join(recommend_books) + "'"
        sql = sql+' limit 16'
        #print(sql)
        try:
            recommend_books = mysql.fetchall_db(sql)
            recommend_books = [[v for k, v in row.items()] for row in recommend_books]

        except Exception as e:
            logger.exception("select recommend books error: {}".format(e))
    return render_template('Index.html',
                           login=login,
                           books=recommend_books,
                           useid=userid,
                           name = "recommend")

@app.route("/loginForm")
def loginForm():
    """
    跳转登录页
    :return: Login.html
    """
    if 'userid' in session:
        return redirect(url_for('root'))
    else:
        return render_template('Login.html', error='')


@app.route("/registerationForm")
def registrationForm():
    """
    跳转注册页
    :return: Register.html
    """
    return render_template("Register.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    注册
    :return: Register.html
    """
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            location = 'china'
            age = request.form['age']

            try:
                sql = "insert into User (Id,UserPassword,Location,Age) values ('{}','{}','{}','{}')".format(username, password, location, age)
                mysql.exe(sql)
                logger.info("username:{},password:{},age:{} register success".format(username, password, age))
            except Exception as e:
                mysql.rollback()
                logger.exception("username:{},password:{},age:{} register filed".format(username, password, age))
            return render_template('Login.html')
    except Exception as e:
        logger.exception("register function error: {}".format(e))
        return render_template('Register.html', error='注册出错')


def is_valid(username, password):
    """
    登录验证
    :param username: 用户名
    :param password: 密码
    :return: True/False
    """
    try:
        sql = "select Id as Username,UserPassword as Password from User where Id='{0}' && UserPassword='{1}'".format(username,password)
        result = mysql.fetchone_db(sql)
        
        if result:
            logger.info('username:{},password:{}: has login success'.format(username, password))
            return True
        else:
            logger.info('username:{},password:{}: has login filed'.format(username, password))
            return False
    except Exception as e:
        logger.exception('username:{},password:{}: has login error'.format(username, password))
        return False


@app.route("/login", methods=['POST', 'GET'])
def login():
    """
    登录页提交
    :return: Login.html
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and username == password:
            session['userid'] = username
            return render_template('Admin.html',userid= 'admin')
        if is_valid(username, password):
            session['userid'] = username
            return redirect(url_for('root'))
        else:
            error = '账号密码输入错误'
            return render_template('Login.html', error=error)


@app.route("/logout")
def logout():
    """
    退出登录，注销
    :return: root
    """
    session.pop('userid', None)
    return redirect(url_for('root'))


def update_recommend_book(UserId, ItemId):
    """
    更新推荐数据
    """
    global operation_num
    sql = "select Rating from Bookrating where UserId='{0}' and ItemId='{1}'".format(UserId, ItemId)
    rating = mysql.fetchone_db(sql)
    print(rating)
    if rating:
        rating = float(rating['Rating'])
    
        if rating + 0.1 > 2: score =2
        else: rating += 0.1
        sql = "update Bookrating set Rating='{2}' where UserId='{0}' and ItemId='{1}'".format(UserId, ItemId,rating)
        logger.info("update_recommend_book, sql:{}".format(sql))
        mysql.exe(sql)
    else:
        rating = 0.1
        sql = "insert into Bookrating (UserId,ItemId,Rating) values ('{0}','{1}','{2}')".format(UserId, ItemId,rating)
        logger.info("update_recommend_book, sql:{}".format(sql))
        mysql.exe(sql)
    operation_num+=1


@app.route("/bookinfo", methods=['POST', 'GET'])
def bookinfo():
    """
    书籍详情
    :return: BookInfo.html
    """
    global operation_num
    # 获取用户IP
    score = 0
    if 'userid' not in session:
        userid = None
        login = False
    else:
        userid = session['userid']
        login = True
    print(operation_num)
    try:
        if request.method == 'GET':
            bookid = request.args.get('bookid')
            sql = "select ISBN, Title, Author, Year, Publisher, ImageL, Id from Books where ISBN='{}'".format(bookid)
            book_info = mysql.fetchall_db(sql)
            book_info = [v for k, v in book_info[0].items()]
            #print(book_info)
            user_id=int(userid)
            item_id=int(book_info[6])
            print([user_id,item_id])
            update_recommend_book(user_id,item_id)
        if userid:
            sql = '''select a.Rating as Rating from Bookrating a join Books b on a.ItemId=b.Id where a.UserId="{0}" and b.ISBN="{1}" '''.format(userid,bookid)
            rating = mysql.fetchone_db(sql)
            if rating:
                score = int(5*rating['Rating'])
                if score>5:
                    score=5
            print(score)

    except Exception as e:
        logger.exception("select book info error: {}".format(e))
    return render_template('BookInfo.html',
                           book_info=book_info,
                           login=login,
                           useid=userid,
                           score=score)


@app.route("/user", methods=['POST', 'GET'])
def user():
    """
    个人信息
    :return: UserInfo.html
    """
    login, userid = False, None
    if 'userid' not in session:
        return redirect(url_for('loginForm'))
    else:
        login, userid = True, session['userid']
    userinfo = []
    try:
        sql = "select Id,UserPassword,Location,Age from User where Id='{}'".format(userid)
        userinfo = mysql.fetchone_db(sql)
        userinfo = [v for k, v in userinfo.items()]
    except Exception as e:
        logger.exception("select UserInfo error: {}".format(e))
    return render_template("UserInfo.html",
                           login=login,
                           useid=userid,
                           userinfo=userinfo)


@app.route("/search", methods=['POST', 'GET'])
def search():
    """
    书籍检索
    :return: Search.html
    """
    login, userid = False, None
    if 'userid' in session:
        login, userid = True, session['userid']
    keyword, search_books = "", []
    try:
        if request.method == 'GET':
            keyword = request.values.get('keyword')
            keyword = keyword.strip()
            sql = """select ISBN, Title, Author, Year, Publisher, ImageL from Books 
            where ISBN='{0}' 
            or Title like '%{0}%'
            or Author like '%{0}%'
            or Year = '{0}' limit 16""".format(keyword)
            print(sql)
            search_books = mysql.fetchall_db(sql)
            search_books = [[v for k, v in row.items()] for row in search_books]
    except Exception as e:
        logger.exception("select search books error: {}".format(e))
    return render_template("Search.html",
                           key=keyword,
                           books=search_books,
                           login=login,
                           useid=userid)


@app.route("/rating", methods=['POST', 'GET'])
def rating():
    """
    书籍评分
    :return: update
    """
    userid = session['userid']
    try:
        if request.method == 'POST':
            rank = request.values.get('rank')
            bookid = request.values.get('bookid')
            print(rank)
            sql = '''select a.Rating as Rating,b.Id as Id from Bookrating a join Books b on a.ItemId=b.Id where a.UserId="{0}" and b.ISBN="{1}" '''.format(userid,bookid)
            print(sql)
            rating = mysql.fetchone_db(sql)
            print(rating)
            if rating['Rating']:
                sql = '''update Bookrating set Rating='{2}' where UserId="{0}" and ItemId="{1}"  '''.format(userid,
                                                                                                rating['Id'], int(rank)/5)
            else:
                sql = '''insert into Bookrating (UserId,ItemId,Rating) values ('{0}','{1}','{2}') '''.format(userid,
                                                                                                 rating['Id'], int(rank)/5)
            print(sql)
            mysql.exe(sql)
            logger.info("update book rating success,sql:{}".format(sql))
    except Exception as e:
        logger.exception("rating books error: {}".format(e))
    return redirect(url_for('root'))


@app.route("/historical", methods=['POST', 'GET'])
def historical():
    """
    历史评分
    :return: Historicalscore.html"
    """
    login, userid = False, None
    if 'userid' not in session:
        return redirect(url_for('loginForm'))
    else:
        login, userid = True, session['userid']
    historicals = []
    try:
        sql = '''select ISBN,Title,Author,Year,Rating,ImageM from (SELECT * from Bookrating ) a  
                        LEFT  JOIN  Books as b on a.ItemId = b.Id where a.UserId = '{}'
                        '''.format(userid)
        historicals = mysql.fetchall_db(sql)
        for i in range(len(historicals)):
            if float(historicals[i]['Rating'])>1:
                historicals[i]['Rating']=5
            else:
                historicals[i]['Rating']=int(5*historicals[i]['Rating'])
        historicals = [[v for k, v in row.items()] for row in historicals]
    except Exception as e:
        logger.exception("historical rating books error: {}".format(e))
    return render_template("Historicalscore.html",
                           books=historicals,
                           login=login,
                           useid=userid)


@app.route("/editinfo", methods=["GET", "POST"])
def editinfo():
    """
    修改个人信息
    :return: Userinfo.html
    """
    userid = session['userid']
    try:
        if request.method == 'POST':
            location = request.form['location']
            age = request.form['age']
            try:
                sql = "update User set Location='{}',Age= '{}' WHERE Id='{}'".format(location, age, userid)
                mysql.exe(sql)
                logger.info("update userinfo --> username:{},location:{},age:{} ".format(userid, location, age))
            except Exception as e:
                mysql.rollback()
                logger.exception("username:{},location:{},age:{} update filed".format(username, location, age))
            return redirect(url_for('user'))
    except Exception as e:
        logger.exception("add user info  error: {}".format(e))
        return redirect(url_for('user'))


@app.route("/editpassword", methods=["GET", "POST"])
def editpassword():
    """
    修改账号密码
    :return: Userinfo.html
    """
    userid = session['userid']
    try:
        if request.method == 'POST':
            password1 = request.form['password1']
            password2 = request.form['password2']
            if password1==password2:
                try:
                    sql = "update User set UserPassword='{}' where Id='{}'".format(password1, userid)
                    mysql.exe(sql)
                    logger.info("UPDATE password --> username:{},password:{} ".format(userid, password1))
                except Exception as e:
                    mysql.rollback()
                    logger.exception("username:{},password:{} update password filed".format(username, password1))
                return redirect(url_for('user'))
            else:
                return redirect(url_for('user'))
    except Exception as e:
        logger.exception("add user info  error: {}".format(e))
        return redirect(url_for('user'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)
