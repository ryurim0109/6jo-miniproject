import requests
from math import *
from bs4 import BeautifulSoup
from pymongo import MongoClient

import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb+srv://test:sparta@cluster0.7fswg.mongodb.net/?retryWrites=true&w=majority')
db = client.sign_up


##############메인페이지에 뮤지컬 정보 붙여넣기###############
@app.route('/')
def home():
    musicals = list(db.musicals.find({}, {'id':False}))
    return render_template('index.html', musicals=musicals)

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
#예령님 더보기 버튼 구현이 안됨..

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

@app.route('/detail')
def detail_go():
    return render_template('detail.html')

#############디테일 페이지 뮤지컬 정보 불러오기
@app.route('/detail1', methods=["POST"])
def detail():
    title_receive = request.form['title_give']
    music = db.musicals.find_one({'title': title_receive},{'_id': False})
    return jsonify({'music': music})

@app.route('/search', methods=["GET"])
def search():
    # find_title를 포함한 제목 찾아서 db에 저장된 image, title 보여주기
    search_title = request.form['search_title']
    if search_title is None:
        all_musicals = list(db.musicals.find({}, {'_id': False}))
        return render_template('index.html', musicals=all_musicals)
    else:
        search_musicals = list(db.musicals.find({'musical_title':{"$regex":search_title}},{'id':False}))
        return render_template('search_main.html', musicals=search_musicals)

#########################################################
# 실행 코드 (맨 아래)
#########################################################

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)