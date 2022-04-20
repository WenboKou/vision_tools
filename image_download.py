import os
import pandas as pd
import requests

csv_path = 'IMDb-Face.csv'
data = pd.read_csv(csv_path)
urls = data['url']
for i in range(1000):
    img_data = requests.get(data['url'][i]).content
    with open(f'/home/wenbokou/下载/IMDB-Face/{i}.jpg', 'wb') as handler:
        handler.write(img_data)