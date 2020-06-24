from flask import Flask, render_template, url_for, flash, request, redirect
from werkzeug.utils import secure_filename
import pandas as pd 
import math

import os
from os.path import join, dirname, realpath


app = Flask(__name__)

PWD = pd.read_csv('templates/data/pass.txt').columns[0]
# print(PWD)
UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/img/uploads/')

ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOADS_PATH

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





# for logging in jinja
def debug(text):
  print(text)
  return ''
def hash_post(text):
  return str(abs(hash(text)))

def joinstrwithslash(listOfstrings):
  return '/'.join(listOfstrings)


posts = pd.read_csv('templates/data/pandas_readable_data2.csv',index_col=0)
posts['date']=pd.to_datetime(posts['date'])
# make a copy so we can add more columns for easy data processing. The copy makes it so we don't have to re-save this 
# new df and overwrite old data with these new columns. Specifically, I need a year column for filtering
# postsCopy = posts
# postsCopy['year'] = pd.DatetimeIndex(posts['date']).year
# print(posts)
# use 'nothing' as placeholder



@app.route('/success')
def success():
  #on success, save and reload the posts dataframe
  #create dir to store backup dataframes
  newdir = app.config['UPLOAD_FOLDER']+str(pd.datetime.now().year)+"_"+str(pd.datetime.now().month)+'/'
  try:
    os.makedirs(newdir)
  except FileExistsError as e:
    print(e,"directory already exists")
  global posts
  #overwrite master df in below path, but also save it to the monthly dir as a backup in case master gets corrupted
  posts.to_csv('templates/data/pandas_readable_data2.csv',columns=['title','description','date','images','youtube'])
  posts.to_csv(newdir+'pandas_readable_data2.csv',columns=['title','description','date','images','youtube'])
  
  posts = pd.read_csv('templates/data/pandas_readable_data2.csv',index_col=0)
  posts['date']=pd.to_datetime(posts['date'])
  return render_template('html/success.html.jinja')



@app.route('/')
def home():
  # log info
  logs = pd.read_csv('templates/data/hits.csv',index_col=0)
  ip_addr = ''
  if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
    ip_addr = request.environ['REMOTE_ADDR']
  else:
    ip_addr = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
  new_log = {'date': pd.datetime.now(), 'IP_ADDR': ip_addr}
  logs=logs.append(new_log, ignore_index=True)
  logs.to_csv('templates/data/hits.csv')
  global posts
  mastheadText = ["Joe's Journal",'Documenting what I do in my free time... sometimes']
  return render_template('html/index.html.jinja',postData=posts[::-1][:4], mastheadImage='home-bg.jpg', debug=debug,mastText = mastheadText,hashtext=hash_post,str=str)

#plus sign separates list elements
# http://localhost:5000/all/05-13-1996/05-13-2096/all/
@app.route('/all/<string:startYear>/<string:endYear>/')
def all(startYear,endYear):
  # create mask for posts to be displayed
  posts['year'] = pd.DatetimeIndex(posts['date']).year
  posts['year']= posts['year'].astype(str) # convert to string. if recognized as int, then pd.to_datetime(2015) = 1970.00....2015
  posts['year'] = pd.to_datetime(posts['year']) # now convert from year as type string to year as type datetime
  mask = (posts['year'] >= pd.to_datetime(startYear)) & (posts['year'] <= pd.to_datetime(endYear)) # generate True, False mask
  df = posts.loc[mask] # generate df to pass to all posts for display

  mastheadText = ['All Posts','Filter by below criteria']
  filterInfo = [startYear,endYear]
  years_low_to_high = pd.DatetimeIndex(posts['date']).year.sort_values().drop_duplicates()
  return render_template('html/all.html.jinja', years=years_low_to_high,postData=df.iloc[::-1], mastheadImage='lab.jpg', debug=debug,mastText = mastheadText,filterInfo=filterInfo,hashtext=hash_post,str=str)



@app.route('/about')
def about():
  mastheadText = ['About Me','']
  return render_template('html/about.html.jinja', mastheadImage='banjuh.jpg', debug=debug,mastText = mastheadText)


@app.route('/post/<string:hashOfPost>')
def post(hashOfPost):
  global posts
  for idx, row in posts.iterrows():
    # print(hash_post(row['description']))
    # print(str(hashOfPost))
    if hash_post(str(row['title'])+str(row['description'])+str(row['date'])) == str(hashOfPost):
      # print(row)
      return render_template('html/post.html.jinja',post_=posts.iloc[idx],mastText = ['',''],mastheadImage='banjuh.jpg')
  mastheadText = ['Uh Oh','Post not found']
  return render_template('html/notFound.html',mastText = mastheadText,image_ = '404.png')


@app.route('/newpost', methods=['GET', 'POST'])
def upload_file():
  global posts
  if request.method == 'POST':
    if request.form['password'] != PWD:
      return redirect(url_for('bad_pwd'))

    #create dir to store images
    year_month = str(pd.datetime.now().year)+"_"+str(pd.datetime.now().month)
    newdir = app.config['UPLOAD_FOLDER']+year_month+'/'
    try:
      os.makedirs(newdir)
    except FileExistsError as e:
      print(e,"directory already exists")
    #define lists to make into a post entry later on
    post_title=request.form['title']
    post_desc=request.form['description']
    post_files=[]
    post_date = pd.datetime.now() if request.form['userDate']=='' else request.form['userDate']
    post_yt = 'nothing' if request.form['yt']=='' else request.form['yt']
    # print('\n\n\n\n')
    # print(request.form)
    # print(request.form['password'])
    # print('\n\n\n\n')
    # check if the post request has the file part
    for file_ in ["file1", "file2","file3"]:
        if file_ not in request.files:
            print('Line 37 in App.py')
            print(request.files)
            return redirect(request.url)#reloads page if there was a problem. Later, route to an error page instead.
    
    for file_ in ["file1", "file2","file3"]:
        file = request.files[file_]
        if file.filename != '':#don't upload blank files!
            # print(file.filename)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(newdir, filename))
                post_files.append('/static/img/uploads/'+year_month+'/'+file.filename)
    
    # print(posts)
    postfilestr = ''
    if post_files!=[]:
      for p in post_files:
        postfilestr = postfilestr+','+p
      postfilestr = postfilestr[1:]
      post_files = postfilestr
    if post_files==[]:
      post_files='nothing'
    new_post = {'title':post_title,
                'description':post_desc,
                'date':post_date, 
                'images':post_files,
                'youtube':post_yt}
    posts=posts.append(new_post, ignore_index=True)
    # print(posts['date'])
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #   print(posts)
    return redirect(url_for('success'))
  mastheadText = ["Create New Post",'Title and description are required']
  return render_template('html/newpost.html.jinja', mastheadImage='newpost.jpeg', debug=debug,mastText = mastheadText)




@app.route('/contact')
def contact():
  mastheadText = ["Contact Me",'My email is joe@joemulhern.net']
  return render_template('html/contact.html.jinja', mastheadImage='post-bg.jpg', debug=debug,mastText = mastheadText)


@app.errorhandler(404)
def page_not_found(e):
  mastheadText = ['Uh Oh',"The page you're looking for does not exist."]
  return render_template('html/notFound.html',mastText = mastheadText,image_ = '404.png'), 404

@app.route('/invalid_password')
def bad_pwd():
  mastheadText = ['Nice Try!',"Wrong password."]
  return render_template('html/notFound.html',mastText = mastheadText,image_ = 'nice.jpg')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)