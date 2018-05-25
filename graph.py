import geopandas as gpd
import pandas as pd

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

from decimal import *
import boto3
import os, io, operator
import uuid
from PIL import Image
import numpy as np

from timeit import default_timer as timer

plt.xkcd()

# TODO: font not found
font_path = "./res/H2GTRE.TTF"
font_name = matplotlib.font_manager.FontProperties(fname=font_path).get_name()
matplotlib.rc('font', family=font_name)


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

# geoJson = {
#     '서울': gpd.read_file("./geo/seoul_municipalities_geo.json"),
#     '전국': gpd.read_file("./geo/skorea_provinces_geo.json"),
# }
seoul = gpd.read_file("./geo/seoul_municipalities_geo.json")
korea = gpd.read_file("./geo/skorea_provinces_geo_simple.json")

# json from https://github.com/southkorea/southkorea-maps
def generateMap(region, data):
    # print(data)
    if region == '서울':
        # map = gpd.read_file("./geo/seoul_municipalities_geo.json")
        # map = geoJson[region]
        map = seoul
        figsize = (18,15)
        crop_area = (150,220,1180,880)
        votes = {}
        for d in data:
            key = d[1] + '구'
            votes[key] = int(d[0])

    elif region == '전국':
        # map = gpd.read_file("./geo/skorea_provinces_geo.json")
        # map = geoJson[region]
        map = korea
        figsize = (11,11)
        crop_area = (100,25,660,685)
        votes = {}
        for d in data:
            try:
                key = convertRegionName(d[1])
                votes[key] = int(d[0])
            except:
                # print(d[1])
                pass
    else:
        map = None

    # print(votes)
    if map is not None:
        votes_df = pd.DataFrame(list(votes.items()), columns=['name', 'percent'])
        data_result = pd.merge(map, votes_df, on='name')
        data_result['sum'] = data_result['name'].map(str) +' : '+ data_result['percent'].map(str) +'%'
        # print(data_result)

        final_pic = data_result.plot(figsize=figsize, linewidth=0.25, edgecolor='black',column='percent', cmap='Blues')
        # print(data_result.head())
        start = timer()
        for index, row in data_result.iterrows():
            # print(row['name'])
            xy = row['geometry'].centroid.coords[:][0]
            xytext = row['geometry'].centroid.coords[:][0]
            # if row['name'] == '경기도':
            #     xytext2 = tuple(map(operator.add, xytext, (0, -0.3)))
            # elif row['name'] == '인천시':
            #     xytext2 = tuple(map(operator.add, xytext, (0.1, 0.1)))
            # elif row['name'] == '충청남도':
            #     xytext = tuple(map(operator.add, xytext, (-0.2, 0.2)))

            plt.annotate(row['sum'], xy=xy, xytext=xytext,  horizontalalignment='center',verticalalignment='center')
            plt.axis('off')
        plt.figure(frameon=False)
        end = timer()
        print(end-start)

        start = timer()
        # upload to s3
        img_data = io.BytesIO()
        crop_data = io.BytesIO()

        fig = final_pic.get_figure()
        fig.savefig(img_data, format='png', transparent=True, bbox_inches='tight') # bbox_inches='tight'
        img_data.seek(0)

        # im = Image.open(img_data)
        # cropImage = im.crop(crop_area)
        # cropImage.save(crop_data, format='png', transparent=True)
        # crop_data.seek(0)
        image_name = str(uuid.uuid4().hex) + ".png"
        # s3.Bucket(bucket).put_object(Key=image_name, Body=crop_data, ContentType="image/png")

        # cropImage.save(image_name)

        img_data.close()
        crop_data.close()
        end = timer()
        print(end-start)
      
        return "http://electiongraphs.s3.amazonaws.com/" + image_name

    else:
        return None
 


parties_color={'더불어민주당': '#2475FF',
       '자유한국당': '#CC0000',
       '바른미래당': '#00B4B4',  
       '민주평화당': '#FFA500',
       '정의당': '#FFCC00',
       '무소속': '#ffffff',
       'default': '#000000' } 

def generateGraph(data):
    print(data)

    sorted_parties_rates=[]
    sorted_parties_color=[]
    real_yticks = []

    sorted_item = sorted(data, reverse=True)

    for i, (rate, name) in enumerate(sorted_item):
        try:
            n1, n2 = name.split(' ')
            n = n1 + ' \n(' + n2 + ')'
            real_yticks.append(n)
            try:
                sorted_parties_color.append(parties_color[n1])
            except KeyError:
                sorted_parties_color.append(parties_color['default'])
            sorted_parties_rates.append(int(rate))
        except:
            real_yticks.append(name)
            try:
                sorted_parties_color.append(parties_color[name])
            except KeyError:
                sorted_parties_color.append(parties_color['default'])
            sorted_parties_rates.append(int(rate))

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    ax.invert_yaxis()

    ypos = np.arange(len(real_yticks))
    rects = plt.barh(ypos, sorted_parties_rates, align='center', height=0.6,color=sorted_parties_color,edgecolor='black')
    #edgecolor 는 무소속 bar graph를 흰색으로 칠할 때 배경과 더 명확히 구별하기 위해서 넣었습니다.
    plt.yticks(ypos, real_yticks, fontsize=14)

    for i, rect in enumerate(rects):
        if rect.get_width() < 4:
            ax.text(1.46 * rect.get_width(), rect.get_y() + rect.get_height() / 2.0, str(sorted_parties_rates[i]) + '%',fontsize=14, ha='right', va='center')
        else:
            ax.text(0.95 * rect.get_width(), rect.get_y() + rect.get_height() / 2.0, str(sorted_parties_rates[i]) + '%',fontsize=14, ha='right', va='center')

    plt.xlabel('현재 득표율', fontsize=15)

    # upload to s3
    start = timer()
    img_data = io.BytesIO()
    fig.savefig(img_data, format='png', transparent=True, bbox_inches='tight') # bbox_inches='tight'
    img_data.seek(0)
    image_name = str(uuid.uuid4().hex) + ".png"
    # s3.Bucket(bucket).put_object(Key=image_name, Body=img_data, ContentType="image/png")
    im = Image.open(img_data) #
    im.save(image_name) #
    img_data.close()
    end = timer()
    print("graph fileio:  ", end-start)

    return "http://electiongraphs.s3.amazonaws.com/" + image_name
