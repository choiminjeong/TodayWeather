import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.project

address = db.user.find_one({'nick':'test'})
address = address['address'].split()
si = address[0][0:2]
gu = address[1]


#line1
URI="http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getCtprvnMesureSidoLIst?serviceKey="
#line2
SERVICE_KEY="EYQKHNA9sAcmcB2Ys%2B9IFgTf9cFZ0Z6bgZmMeYpTjR16rqGDXlpWahaJxWJ68zkJIUbUfhs7cTxL5PRfFjYT7w%3D%3D"
#line3
items="&numOfRows=31"
#line4
PageNum="&pageNo=1"

#line5(시도 이름 (서울, 부산, 대구, 인천, 광주, 대전, 울산, 경기, 강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주, 세종))
SidoName = "&sidoName=" + si
#line6
searchCondition="&searchCondition=HOUR"
#line7
URI=URI+SERVICE_KEY+items+PageNum+SidoName+searchCondition
# print(URI)
#

response=requests.get(URI) #REQUST로 데이터 요청하기
# print(response.text)
#
soup = BeautifulSoup(response.text, 'html.parser')
ItemList=soup.findAll('item')

# for item in ItemList:
    # print(item)
    # print(item.find('datatime').text)
    # if (gu == (item.find('cityname').text)):
    #     print(item.find('cityname').text)
    # print(item.find('so2value').text)
    # print(item.find('covalue').text)
    #     print(item.find('pm10value').text)   #미세먼지
    #     print(item.find('pm25value').text)   #초미세먼지
        # print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")



#line1
DURI="http://apis.data.go.kr/1360000/VilageFcstInfoService/getVilageFcst?serviceKey="
#line2
DSERVICE_KEY="EYQKHNA9sAcmcB2Ys%2B9IFgTf9cFZ0Z6bgZmMeYpTjR16rqGDXlpWahaJxWJ68zkJIUbUfhs7cTxL5PRfFjYT7w%3D%3D"
#line4
DPageNum="&pageNo=1"
#line3
Ditems="&numOfRows=112"
#line5(시도 이름 (서울, 부산, 대구, 인천, 광주, 대전, 울산, 경기, 강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주, 세종))
DdataType = "&dataType=XML"
#line6
Dbase_date = "&base_date=20200421"
Dbase_time = "&base_time=0500"
Dx = "&nx=1"
Dy = "&ny=1"
#line7
DURI=DURI+DSERVICE_KEY+DPageNum+Ditems+DdataType+Dbase_date+Dbase_time+Dx+Dy
print(DURI)

Dresponse=requests.get(DURI) #REQUST로 데이터 요청하기

soup = BeautifulSoup(Dresponse.text, 'html.parser')
DItemList=soup.findAll('item')

print(DItemList)
for Ditems in DItemList:
    for Ditem in Ditems:
        print(Ditem)
        # print(Ditem.find('baseTime').text)
        # print(Ditem.find('category').text)
        # print(Ditem.find('fcstDate').text)
        # print(Ditem.find('fcstTime').text)
        # print(Ditem.find('fcstValue').text)
    # print(Ditem)
    # print(Ditem.find('category').text) #강수확률 POP
    # print(Ditem.find('TMN').text)  # 최저온도 TMN
    # print(Ditem.find('TMX').text)  # 최고온도 TMX
    # print(Ditem.find('WSD').text)  # 풍속 WSD

    # if ((Ditem.find('category').text) =='POP'):
    # print(Ditem.find('fcstValue'))

    #fcstTime 예보시각 0000 -- 2100