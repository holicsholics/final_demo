# 필요 라이브러리 
import streamlit as st
from streamlit_folium import st_folium
import folium
from streamlit_folium import folium_static
from folium import plugins
import json
import time
import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
# from glob import glob
import koreanize_matplotlib
import plotly.express as px
import requests

st.set_page_config(
    page_title="지켜줄게..너의 안전..",
    page_icon="❤️",
    layout="wide"
)

@st.cache
def load_data(file_name,en):
    data = pd.read_csv(file_name, encoding=en)
    return data

df_출발지 = pd.DataFrame({'출발지':['서울특별시 용산구 한강대로 405','서울특별시 서초구 신반포로 194']})
df_도착지 = pd.DataFrame({'도착지':['서울특별시 종로구 종로3길 17']})
# sidebar 지정-------------------------------------

with st.sidebar:
    st.markdown("## 💌 여러분의 안전을 지켜줄겁니다. 💌")
    st.markdown("**************")
    st.header("🔎검색")
    # 검색 요소 받기
    출발지 = st.selectbox("출발지",df_출발지["출발지"])
    도착지 =  st.selectbox("도착지",df_도착지["도착지"])
    st.markdown("**************")
    
def get_location(address):
  url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + address
  headers = {"Authorization": "KakaoAK c88bcccff9c5bef1a68843ff7083841b"}
  api_json = json.loads(str(requests.get(url,headers=headers).text))
  address = api_json['documents'][0]['address']
  crd = {"lat": str(address['y']), "lng": str(address['x'])}
  address_name = address['address_name']

  return crd

start = get_location(출발지)
end = get_location(도착지)

def tmap_api(start,end):
    url = "https://apis.openapi.sk.com/tmap/routes?version=1&callback=function"

    payload = {
        "tollgateFareOption": 16,
        "roadType": 32,
        "directionOption": 1,
        "endX": end['lng'],
        "endY": end['lat'],
        "endRpFlag": "G",
        "reqCoordType": "WGS84GEO",
        "startX": start['lng'],
        "startY": start['lat'],
        "gpsTime": "20191125153000",
        "speed": 100,
        "uncetaintyP": 1,
        "uncetaintyA": 1,
        "uncetaintyAP": 1,
        "carType": 0,
        "startName": "%EC%9D%84%EC%A7%80%EB%A1%9C%20%EC%9E%85%EA%B5%AC%EC%97%AD",
        "endName": "%ED%97%A4%EC%9D%B4%EB%A6%AC",
        "gpsInfoList": "126.939376564495,37.470947057194365,120430,20,50,5,2,12,1_126.939376564495,37.470947057194365,120430,20,50,5,2,12,1",
        "detailPosFlag": "2",
        "resCoordType": "WGS84GEO",
        "sort": "index"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "appKey": "l7xx543bd2b77e19411d84d2f757bf2396cd"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.text

df_res = tmap_api(start,end)
json_df = json.loads(df_res)

alpha = []
for i in range(len(json_df['features'])):
    if type(json_df['features'][i]['geometry']['coordinates'][0]) == float:
        alpha.append(json_df['features'][i]['geometry']['coordinates'])

경도 = []
위도 = []
for i in range(len(alpha)):
    경도.append(alpha[i][0])
    위도.append(alpha[i][1])

df_좌표 = pd.DataFrame({'경도' : 경도, '위도' : 위도})

location_data = []
for i in range(0,len(df_좌표)):
    location_data.append([위도[i], 경도[i]])

center = location_data[round(len(df_좌표)/2)]
m = folium.Map(location=[center[0], center[1]], zoom_start=13)
# 시작
location_data = df_좌표[["위도","경도"]].values[:len(df_좌표)].tolist()
for i in df_좌표.index:
    popup = "Liberty Bell"
    tt = "Liberty Bell"
    location = [df_좌표.loc[i, "위도"], df_좌표.loc[i, "경도"]]
    folium.Marker(
        location = location, 
        popup="Liberty Bell", 
        tooltip=tt
    ).add_to(m)
        
# plugins.MarkerCluster(location_data).add_to(m)

#지도 띄우기
folium_static(m)
