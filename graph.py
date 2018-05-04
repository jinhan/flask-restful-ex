import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

from decimal import *

import boto3
import os, io
import uuid

plt.xkcd()

# font_path = "/usr/share/fonts/truetype/nanum/NanumGothic_Coding.ttf"
font_path = "./res/NanumBarunGothic.otf"
font_name = font_manager.FontProperties(fname = font_path).get_name()
rc('font', family = font_name)


s3 = boto3.resource('s3', region_name = 'ap-northeast-2',
                    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY'])
bucket = 'electiongraphs'


def generateMap(region, data):

    if region == '서울':
        map = gpd.read_file("./geo/seoul_municipalities_geo.json")
    else:
        map = None

    # if map != None:
    votes = {}
    for d in data:
        key = d[1] + '구'
        votes[key] = int(d[0])
    # print(votes)
    
    votes_df = pd.DataFrame(list(votes.items()), columns=['SIG_KOR_NM', 'percent'])
    data_result = pd.merge(map, votes_df, on='SIG_KOR_NM')

    final_pic = data_result.plot(figsize=(14,10), linewidth=0.25, edgecolor='black',
                                column='percent', cmap='Blues', scheme='quantiles', legend=True)

    for index, row in map.iterrows():
        xy = row['geometry'].centroid.coords[:]
        xytext = row['geometry'].centroid.coords[:]
        plt.annotate(row['SIG_KOR_NM'], xy = xy[0], xytext = xytext[0],
                    horizontalalignment = 'center', verticalalignment = 'center')
        plt.axis('off')
    plt.figure(frameon=False)

    img_data = io.BytesIO()
    fig = final_pic.get_figure()
    fig.savefig(img_data, format='png', transparent=True)
    img_data.seek(0)

    image_name = str(uuid.uuid4().hex)
    s3.Bucket(bucket).put_object(Key=image_name, Body=img_data, ContentType="image/png")

    return "http://electiongraphs.s3.amazonaws.com/" + image_name

    # else:
    #     return None

def generateGraph(q):
    return "https://s3.amazonaws.com/"
