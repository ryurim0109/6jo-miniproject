import requests
from math import *
from bs4 import BeautifulSoup
from pymongo import MongoClient
import jwt
#from werkzeug.utils import secure_filename

import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb+srv://test:sparta@cluster0.7fswg.mongodb.net/?retryWrites=true&w=majority')
db = client.sign_up

##############메인페이지에 뮤지컬 정보 검색###############
@app.route('/index')
def home():
    token_receive = request.cookies.get('mytoken')
    search_title = request.args.get('search_title')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        name = db.users.find_one({'username': payload['id']})  # 데이터베이스에서 email과 일치하는 name을 찾아서 name에 저장한다.
        user = name["profile_name"]

        if search_title is None:
            # DB에서 뮤지컬 정보 모두 가져오기
            all_musicals = list(db.musicals.find({}, {'_id': False}))

            # 닉네임 & 뮤지컬 목록 반환하기
            return render_template("index.html", all_musicals=all_musicals, name=user)
        else:
            search_musicals = list(db.musicals.find({"title": {"$regex": search_title}}, {'_id': False}))
            return jsonify({'result':'success','search_musicals':search_musicals})
            # return render_template("search_main.html", search_musicals=search_musicals, name=user)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


##############로그인 하기###############
@app.route('/')
def login():
    return render_template('login.html')

###################로그인 토큰 생성 및 발급############
@app.route('/sign_in', methods=['POST'])
def sign_in():

    useremail_receive = request.form['useremail_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': useremail_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': useremail_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

##############회원가입###############
@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    useremail_receive = request.form['useremail_give']
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": useremail_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    useremail_receive = request.form['useremail_give']
    exists = bool(db.users.find_one({"useremail": useremail_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_up/check_dup2', methods=['POST'])
def check_dup2():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

#########################################################
#예령님 더보기 버튼 ..

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('http://ticket.interpark.com/TPGoodsList.asp?Ca=Mus', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

musicals = soup.select('table > tbody > tr')

@app.route("/list", methods=["GET"])
def musical_list():
    page = request.args.get("page", 1, type=int)
    musical_list = list(db.musicals.find({}, {'_id': False}).skip((page-1) * 12).limit(12))
    musicals_count = len(list(db.musicals.find({}, {'_id': False})))
    last_page = ceil(musicals_count / 12)
    return jsonify({'musicals': musical_list, 'last_page': last_page})


##########################디테일 페이지로 이동###############################

@app.route('/detail', methods=['GET'])
def detail_go():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        name = db.users.find_one({'username': payload['id']})
        user = name["profile_name"]
        return render_template('detail.html', name=user)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

## 디테일 페이지 댓글 저장하기 (쿠키 id값도 빼와서 해당 유저 정보에 데이터 db저장)
@app.route('/detailc', methods=["POST"])
def detail_comment():
    token_receive = request.cookies.get('mytoken')

    comment_receive = request.form['comment_give']
    star_receive = request.form['star_give']
    title_receive = request.form['title_give']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        name = db.users.find_one({'username': payload['id']})
        user = name["profile_name"]
        comment_list = list(db.commentSave.find({}, {'_id': False}))
        count = len(comment_list) + 1

        doc = {
             'name': user,
             'comment': comment_receive,
             'star': star_receive,
             'title': title_receive,
             'num': count
        }
        db.commentSave.insert_one(doc)
        return jsonify({'msg': '입력완료!'})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
         return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

##디테일 페이지 댓글 불러오기
@app.route('/detail_comment', methods=["POST"])
def show_comment():
    title_receive = request.form['title_give']
    comment_list = list(db.commentSave.find({'title':title_receive},{'_id': False}))
    return jsonify({'comment': comment_list})

##디테일 페이지 댓글 삭제하기
@app.route('/detail_delete', methods=["POST"])
def del_comment():
    token_receive = request.cookies.get('mytoken')
    num_receive = request.form['num_give']
    names = list(db.commentSave.find({'num': int(num_receive)}, {'_id': False}))
    nam = names[0]
    print(nam)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        name = db.users.find_one({'username': payload['id']},{'_id':False})
        print(name)
        if nam['name'] == name['profile_name']:
            db.commentSave.delete_one({'num':int(num_receive)})
            return jsonify({'msg': '삭제완료!'})
        else:
            return jsonify({'msg': '다른사람이 작성한 글입니다. 삭제할 수 없습니다.'})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

#############디테일 페이지 뮤지컬 정보 불러오기
@app.route('/detail1', methods=["POST"])
def detail():
    title_receive = request.form['title_give']
    music = db.musicals.find_one({'title': title_receive},{'_id': False})
    return jsonify({'music': music})

##크롤링
# ms = soup.select('table > tbody > tr')
# for mm in ms:
#     image = mm.select_one('td.RKthumb > a > img')['src']
#     title = mm.select_one('td.RKthumb > a > img')['alt']
#     place = mm.select_one('td:nth-child(3) > a').text
#     date = mm.select_one('td:nth-child(4)').text.replace('\n','').replace('\t','')
#
#     doc = {
#     'image': image,
#     'title': title,
#     'place':place,
#     'date':date
#      }
#
#
#     db.musicals.insert_one(doc)



#########################################################
# 실행 코드 (맨 아래)
#########################################################

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)