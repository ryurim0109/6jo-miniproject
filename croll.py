import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.tfnms.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.sign_up

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('http://ticket.interpark.com/TPGoodsList.asp?Ca=Mus', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

musicals = soup.select('table > tbody > tr')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('http://ticket.interpark.com/TPGoodsList.asp?Ca=Mus', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

musicals = soup.select('table > tbody > tr')
for musical in musicals:
    image = musical.select_one('td.RKthumb > a > img')['src']
    title = musical.select_one('td.RKthumb > a > img')['alt']
    place = musical.select_one('td:nth-child(3) > a').text
    date = musical.select_one('td:nth-child(4)').text.replace('\n','').replace('\t','')

    doc = {
    'image': image,
    'title': title,
    'place':place,
    'date':date
     }

    db.musicals.insert_one(doc)