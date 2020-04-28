from flask import Flask, render_template, jsonify, request, session, redirect, url_for
app = Flask(__name__)

from bs4 import BeautifulSoup
import requests, csv, json

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.project

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'BF'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib

#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/')
def main():
   return render_template('contactform.html')

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/signup')
def signup():
   return render_template('signup.html')

@app.route('/setting')
def setting():
   return render_template('setting.html')

#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/signup', methods=['POST'])
def api_signup():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']
   nickname_receive = request.form['nickname_give']
   rain_receive = request.form['rain_give']
   mise_receive = request.form['mise_give']
   heat_receive = request.form['heat_give']
   cold_receive = request.form['cold_give']
   wind_receive = request.form['wind_give']
   email_receive = request.form['email_give']
   address_receive = request.form['address_give']

   id_result = db.user.find_one({'id': id_receive})
   if id_result is not None:
      return jsonify({'result': 'fail', 'msg': '이미 사용중인 아이디 입니다.'})

   nick_result = db.user.find_one({'nick': nickname_receive})
   if nick_result is not None:
      return jsonify({'result': 'fail', 'msg': '이미 사용중인 닉네임 입니다.'})

   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()


   db.user.insert_one({'id':id_receive,'pw':pw_hash,'nick':nickname_receive, 'rain': rain_receive, 'mise': mise_receive, 'heat': heat_receive, 'cold': cold_receive,
   'wind': wind_receive, 'email': email_receive, 'address': address_receive

   })



   return jsonify({'result': 'success'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])

def api_login():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']

   # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

   # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
   result = db.user.find_one({'id':id_receive,'pw':pw_hash})

   # 찾으면 JWT 토큰을 만들어 발급합니다.
   if result is not None:
      # JWT 토큰에는, payload와 시크릿키가 필요합니다.
      # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
      # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
      # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
      payload = {
         'id': id_receive,
         'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=86400)
      }
      token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

      # token을 줍니다.
      return jsonify({'result': 'success','token':token})

   # 찾지 못하면
   else:
      return jsonify({'result': 'fail', 'msg':'아이디/비밀번호가 일치하지 않습니다.'})

# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
   # 토큰을 주고 받을 때는, 주로 header에 저장해서 넘겨주는 경우가 많습니다.
   # header로 넘겨주는 경우, 아래와 같이 받을 수 있습니다.
   token_receive = request.headers['token_give']

   # try / catch 문?
   # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

   try:
      # token을 시크릿키로 디코딩합니다.
      # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
      payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
      print(payload)

      # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
      # 여기에선 그 예로 닉네임을 보내주겠습니다.
      userinfo = db.user.find_one({'id':payload['id']},{'_id':0})
      nick = userinfo['nick']
      rain_true = userinfo['rain']
      mise_true = userinfo['mise']
      heat_true = userinfo['heat']
      cold_true = userinfo['cold']
      wind_true = userinfo['wind']

      # API 연결하기
      # nick 으로 address 찾아서 해당 주소의 날씨 뽑아오기
      address = userinfo['address']


      address = address.split()
      date = datetime.datetime.now().strftime('%Y%m%d')
      time = datetime.datetime.now().strftime('%H%M')

      si = address[0][0:2]
      si2 = address[0]
      gu = address[1]
      dong = address[2]
      print('si' + si+'si2'+si2+'gu'+gu+'dong'+dong)

      # with open('C:\\Users\\suk93\\Desktop\\TodayWeather\\templates\\keys.json') as json_file:
      #    json_data = json.load(json_file)
      SERVICE_KEY = "EYQKHNA9sAcmcB2Ys%2B9IFgTf9cFZ0Z6bgZmMeYpTjR16rqGDXlpWahaJxWJ68zkJIUbUfhs7cTxL5PRfFjYT7w%3D%3D"

      URI = "http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getCtprvnMesureSidoLIst?serviceKey="
      items = "&numOfRows=31"
      PageNum = "&pageNo=1"
      # line5(시도 이름 (서울, 부산, 대구, 인천, 광주, 대전, 울산, 경기, 강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주, 세종))
      SidoName = "&sidoName=" + si
      searchCondition = "&searchCondition=HOUR"
      URI = URI + SERVICE_KEY + items + PageNum + SidoName + searchCondition

      response = requests.get(URI)  # REQUST로 데이터 요청하기
      soup = BeautifulSoup(response.text, 'html.parser')
      ItemList = soup.findAll('item')
      # 정의
      mise = 0
      POP_val = 0
      WSD_val = 0
      TMX_val = 0
      TMN_val = 0
      X = ""
      Y = ""

      for item in ItemList:
         if (gu == (item.find('cityname').text)):
            mise = item.find('pm10value').text

      with open('weather_api.csv', newline='', encoding='UTF-8') as csvfile:
         reader = csv.DictReader(csvfile)

         for row in reader:
            if si2 == row['1단계'] and gu == row['2단계'] and dong == row['3단계']:
               X = row['격자 X']
               Y = row['격자 Y']
      print('mise' + mise)
      DURI = "http://apis.data.go.kr/1360000/VilageFcstInfoService/getVilageFcst?serviceKey="
      Ditems = "&numOfRows=112"
      DdataType = "&dataType=XML"
      Dbase_date = "&base_date=" + date
      Dbase_time = "&base_time=0500"
      Dx = "&nx=" + X
      Dy = "&ny=" + Y

      DURI = DURI + SERVICE_KEY + PageNum + Ditems + DdataType + Dbase_date + Dbase_time + Dx + Dy

      Dresponse = requests.get(DURI)  # REQUST로 데이터 요청하기
      soup = BeautifulSoup(Dresponse.text, 'html.parser')
      DItemList = soup.findAll('item')

      for Ditems in DItemList:
         Ditem = list(Ditems)
         fcstTime = Ditem[4].text
         fcstValue = Ditem[5].text
         if (Ditem[2].text == "POP"):  # 강수량
            if (Ditem[3].text == date):
               if (int(0000) <= int(time) and int("0300") > int(time)):
                  if (Ditem[4].text == "0000"):
                     POP_val = fcstValue
                     print(Ditem[2].text, fcstTime, POP_val)  # category
               elif (int("0300") <= int(time) and int("0600") > int(time)):
                  if (Ditem[4].text == "0300"):
                     POP_val = fcstValue
                     print(Ditem[2].text, fcstTime, POP_val)  # category
               elif (int("0600") <= int(time) and int("0900") > int(time)):
                  if (Ditem[4].text == "0600"):
                     POP_val = fcstValue
                     print(Ditem[2].text, fcstTime, POP_val)  # category
               elif (int("0900") <= int(time) and int("1200") > int(time)):
                  if (Ditem[4].text == "0900"):
                     POP_val = fcstValue
                     print(Ditem[2].text, fcstTime, POP_val)  # category
               elif (int("1200") <= int(time) and int("1500") > int(time)):
                  if (Ditem[4].text == "1200"):
                     POP_val = fcstValue
                     print(Ditem[2].text, fcstTime, POP_val)  # category
               elif (int("1500") <= int(time) and int("1800") > int(time)):
                  if (Ditem[4].text == "1500"):
                     POP_val = fcstValue
                     print(Ditem[2].text, fcstTime, POP_val)  # category
               elif (int("1800") <= int(time) and int("2100") > int(time)):
                  if (Ditem[4].text == "1800"):
                     POP_val = fcstValue
                     print(Ditem[2].text, fcstTime, POP_val)  # category
               else:
                  if (Ditem[4].text == "2100"):
                     POP_val = fcstValue
                     print(Ditem[2].text, fcstTime, POP_val)  # category

         if (Ditem[2].text == "WSD"):  # 풍속
            if (Ditem[3].text == date):
               if (int(0000) <= int(time) and int("0300") > int(time)):
                  if (Ditem[4].text == "0000"):
                     WSD_val = fcstValue
                     print(Ditem[2].text, fcstTime, WSD_val)  # category
               elif (int("0300") <= int(time) and int("0600") > int(time)):
                  if (Ditem[4].text == "0300"):
                     WSD_val = fcstValue
                     print(Ditem[2].text, fcstTime, WSD_val)  # category
               elif (int("0600") <= int(time) and int("0900") > int(time)):
                  if (Ditem[4].text == "0600"):
                     WSD_val = fcstValue
                     print(Ditem[2].text, fcstTime, WSD_val)  # category
               elif (int("0900") <= int(time) and int("1200") > int(time)):
                  if (Ditem[4].text == "0900"):
                     WSD_val = fcstValue
                     print(Ditem[2].text, fcstTime, WSD_val)  # category
               elif (int("1200") <= int(time) and int("1500") > int(time)):
                  if (Ditem[4].text == "1200"):
                     WSD_val = fcstValue
                     print(Ditem[2].text, fcstTime, WSD_val)  # category
               elif (int("1500") <= int(time) and int("1800") > int(time)):
                  if (Ditem[4].text == "1500"):
                     WSD_val = fcstValue
                     print(Ditem[2].text, fcstTime, WSD_val)  # category
               elif (int("1800") <= int(time) and int("2100") > int(time)):
                  if (Ditem[4].text == "1800"):
                     WSD_val = fcstValue
                     print(Ditem[2].text, fcstTime, WSD_val)  # category
               else:
                  if (Ditem[4].text == "2100"):
                     WSD_val = fcstValue
                     print(Ditem[2].text, fcstTime, WSD_val)  # category

         if (Ditem[2].text == 'TMX'):  # 최고온도 1500
            if (Ditem[3].text == date):
               TMX_val = fcstValue
               print(Ditem[2].text, fcstTime, TMX_val)  # category

         if (Ditem[2].text == "TMN"):
            TMN_val = fcstValue
            print(Ditem[2].text, fcstTime, TMN_val)  # category
      # 정의
      mise_val = 0
      rain_val = 0
      wind_val = 0
      heat_val = 0
      cold_val = 0

      # if int(mise) >= int("80"):
      #    mise_val = mise
      # if int(POP_val) >= int("60"):
      #    rain_val = POP_val
      # if float(WSD_val) >= int("17"):
      #    wind_val = WSD_val
      # if float(TMX_val) >= int("34"):
      #    heat_val = TMX_val
      # if float(TMN_val) <= int("12"):
      #    cold_val = TMN_val

      return jsonify(
         {'result': 'success', 'nickname': nick, 'wind': int(WSD_val), 'rain': int(POP_val), 'cold': int(TMN_val), 'heat': int(TMX_val),
         'mise': int(mise), 'rain_true': rain_true, 'mise_true': mise_true,'heat_true': heat_true,'cold_true': cold_true,'wind_true': wind_true})

   except jwt.ExpiredSignatureError:
      # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
      return jsonify({'result': 'fail', 'msg':'로그인 시간이 만료되었습니다.'})


@app.route('/api/setting', methods=['POST'])
def api_setting():
   nick_receive = request.form['nick_give']
   rain_receive = request.form['rain_give']
   mise_receive = request.form['mise_give']
   heat_receive = request.form['heat_give']
   cold_receive = request.form['cold_give']
   wind_receive = request.form['wind_give']
   email_receive = request.form['email_give']
   address_receive = request.form['address_give']

   db.user.update_one({'nick': nick_receive}, {'$set': {'rain': rain_receive, 'mise': mise_receive,
                                                        'heat': heat_receive, 'cold': cold_receive,
                                                        'wind': wind_receive, 'email': email_receive,
                                                        'address': address_receive}})


   return jsonify({'result': 'success'})




if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)