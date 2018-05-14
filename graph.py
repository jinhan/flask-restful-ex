import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

from decimal import *

import boto3
import os, io, operator
import uuid

from PIL import Image

plt.xkcd()

font_path = "./res/NanumBarunGothic.otf" or "./res/HYGTRE.TTF" or "/usr/share/fonts/truetype/nanum/NanumGothic_Coding.ttf"
font_name = font_manager.FontProperties(fname = font_path).get_name()
rc('font', family = font_name)


s3 = boto3.resource('s3', region_name = 'ap-northeast-2',
                    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY'])
bucket = 'electiongraphs'

r2r = {
    '광주': '광주시',
    '울산': '울산시',
    '전북': '전라북도',
    '전남': '전라남도',
    '서울': '서울시',
    '경남': '경상남도',
    '대전': '대전시',
    '대구': '대구시',
    '경기': '경기도',
    '부산': '부산시',
    '경북': '경상북도',
    '인천': '인천시',
    '충북': '충청북도',
    '강원': '강원도',
    '충남.세종': '충청남도',
    '제주': '제주시',
}
def convertRegionName(r):
    return r2r[r]

# json from https://github.com/southkorea/southkorea-maps
def generateMap(region, data):
    # print(data)
    if region == '서울':
        map = gpd.read_file("./geo/seoul_municipalities_geo.json")
        figsize = (14,10)
        crop_area = (150,220,1180,880)
        votes = {}
        for d in data:
            key = d[1] + '구'
            votes[key] = int(d[0])

    elif region == '전국':
        map = gpd.read_file("./geo/skorea_provinces_geo.json")
        figsize = (20,20)
        crop_area = (160,50,830,830)
        votes = {}
        for d in data:
            try:
                key = convertRegionName(d[1])
                votes[key] = int(d[0])
            except:
                pass
   
    else:
        map = None


    if map is not None:
        votes_df = pd.DataFrame(list(votes.items()), columns=['name', 'percent'])
        data_result = pd.merge(map, votes_df, on='name')
        data_result['sum'] = data_result['name'].map(str) +' : '+ data_result['percent'].map(str) +'%'
        # print(data_result)

        final_pic = data_result.plot(figsize=figsize, linewidth=0.25, edgecolor='black',column='percent', cmap='Blues')
        # print(data_result.head())
        for index, row in data_result.iterrows():
            # print(row['name'])
            xy = row['geometry'].centroid.coords[:][0]
            xytext = row['geometry'].centroid.coords[:][0]
            # 전국
            # if row['name'] == '경기도':
            #     xytext2 = tuple(map(operator.add, xytext, (0, -0.3)))
            # elif row['name'] == '인천시':
            #     xytext2 = tuple(map(operator.add, xytext, (0.1, 0.1)))
            # elif row['name'] == '충청남도':
            #     xytext = tuple(map(operator.add, xytext, (-0.2, 0.2)))

            plt.annotate(row['sum'], xy=xy, xytext=xytext,  horizontalalignment='center',verticalalignment='center')
            plt.axis('off')
        plt.figure(frameon=False)

        # upload to s3
        img_data = io.BytesIO()
        crop_data = io.BytesIO()

        fig = final_pic.get_figure()
        fig.savefig(img_data, format='png', transparent=True, bbox_inches='tight') # bbox_inches='tight'
        img_data.seek(0)

        im = Image.open(img_data)
        cropImage = im.crop(crop_area)
        cropImage.save(crop_data, format='png', transparent=True)

        image_name = str(uuid.uuid4().hex) + ".png"
        # s3.Bucket(bucket).put_object(Key=image_name, Body=crop_data, ContentType="image/png")

        cropImage.save(image_name)

        img_data.close()
        crop_data.close()

        return "http://electiongraphs.s3.amazonaws.com/" + image_name

    else:
        return None

def generateGraph(q):
    return "https://s3.amazonaws.com/"
