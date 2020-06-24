## converts our nice json into pandas-readable shit
import pandas as pd
jsondata = pd.read_json('templates/data/posts.json')

titles = []
descriptions = []
dates = []
media = []

for post in jsondata['posts']:
    titles.append(post['title'])
    descriptions.append(post['description'])
    dates.append(post['date'])
    media.append(post['media'])

df_data = pd.DataFrame(list(zip(titles, descriptions, dates, media)), columns =['title', 'description','date','media']) 
print(df_data)

df_data.to_csv("templates/data/pandas_readable_data.csv")