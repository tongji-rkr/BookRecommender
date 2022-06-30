import argparse
import numpy as np
from sklearn.metrics import det_curve

def read_item_index_to_entity_id_file():
    file = '../data/book/item_index2entity_id.txt'
    print('reading item index to entity id file: ' + file + ' ...')
    isbn_list=[]
    for line in open(file, encoding='utf-8').readlines():
        item_index = line.strip().split('\t')[0]
        isbn_list.append(item_index)
    return isbn_list


def convert_books(isbn_list):
    file = '../data/book/BX-Books.csv'

    print('reading books details ...')
    isbn_detail=dict()
    for line in open(file, encoding='utf-8').readlines()[1:]:
        array = line.strip().split(';')
        for i in range(len(array)):
            array[i]=array[i][1:-1]
        if len(array)==8:
            isbn_detail[array[0]]=array
    print('converting books details ...')
    writer = open('../data/book/book_mysql.sql', 'w', encoding='utf-8')
    id=0
    for isbn in isbn_list:
        if isbn_detail.get(isbn)!=None:
            detail=isbn_detail[isbn]
            writer.write("insert into Books (Id,ISBN,Title,Author,Year,Publisher,ImageS,ImageM,ImageL) values (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\");\n".format(id,detail[0],detail[1],detail[2],detail[3],detail[4],detail[5],detail[6],detail[7]))
            id+=1
    writer.close()
    print('number of items: %d' % len(isbn_list))

def convert_ratings():
    file = '../data/book/ratings_final.txt'

    print('reading ratings details ...')
    writer = open('../data/book/ratings_mysql.sql', 'w', encoding='utf-8')
    for line in open(file, encoding='utf-8').readlines()[1:]:
        array = line.strip().split(' ')
        if len(array)==3:
            writer.write("insert into Bookrating (UserId,ItemId,Rating) values ('{}','{}','{}');\n"
            .format(array[0],array[1],array[2]))
    writer.close()

def convert_users():
    file = '../data/book/BX-Users.csv'

    print('reading users details ...')
    writer = open('../data/book/user_mysql.sql', 'w', encoding='utf-8')
    user_id=0
    for line in open(file, encoding='utf-8').readlines()[1:]:
        array = line.strip().split(';')
        for i in range(len(array)):
            array[i]=array[i][1:-1]
        if user_id<=17859 and len(array)==3:
            if array[2][0]<='1' or array[2][0]>'9':
                array[2]='18'
            writer.write("insert into User (Id,Location,Age) values ('{}','{}','{}');\n"
            .format(user_id,array[1],int(array[2])))
            user_id+=1
    writer.close()


if __name__ == '__main__':
    isbn_list=read_item_index_to_entity_id_file()
    convert_books(isbn_list)
    convert_users()
    convert_ratings()
    print('done')
