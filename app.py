from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps
from data import Songs
import random
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'addyoursecretkeyhere'	#this method for adding session secret key in pythonanywhere

songs_data = Songs()

def is_registered(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'registered' in session:
			return f(*args, **kwargs)
		else:
			return redirect(url_for('register'))
	return wrap


@app.route('/')
def index():
	return render_template('home.html')

@app.route('/about/')
def about():
	return render_template('about.html')

@app.route('/highscore/')
def highscore():
	return render_template('highscore.html')



##################Core game logic and random number generation
@app.route('/random_security/')
@is_registered
def random_security():
	if True:
		#session['rand_num'] = random.randint(0, len(songs_data)-1)
		session['rand_num'] = random.choice(session['unvisited'])
		session['unvisited'].remove(session['rand_num'])
		if len(session['unvisited']) < 1:
			session['gamecomplete'] = True
			return redirect(url_for('gamecomplete'))
		return redirect(url_for('game'))
	return render_template('security.html')


class SongForm(Form):
	name = StringField('Identify the song<br>(NOTE: select from the drop-down as you type)', [validators.DataRequired()])

@app.route('/game/', methods = ['GET', 'POST'])
@is_registered
def game():
	#rand_num = random.randint(0, 4)
	form = SongForm(request.form)
	if request.method == 'POST' and form.validate():
		session['name_candidate'] = form.name.data
		return redirect(url_for('score'))
	return render_template('game.html', i = session['rand_num'], songs = songs_data, form = form, score = session['score'])

################# giving clues
@app.route('/gameclue', methods = ['GET', 'POST'])
@is_registered
def clue():
	session['clue'] = True
	form = SongForm(request.form)
	if request.method == 'POST' and form.validate():
		session['name_candidate'] = form.name.data
		return redirect(url_for('score'))
	return render_template('gameclue.html', i = session['rand_num'], songs = songs_data, form = form, score = session['score'])

################# music scoring engine

#this function is useed as udayip spell checker, not at all efficient
def LongestCommonSubsequence(X, Y):
    # find the length of the strings 
    m = len(X) 
    n = len(Y) 
  
    # declaring the array for storing the dp values 
    L = [[None]*(n+1) for i in xrange(m+1)] 
  
    """Following steps build L[m+1][n+1] in bottom up fashion 
    Note: L[i][j] contains length of LCS of X[0..i-1] 
    and Y[0..j-1]"""
    for i in range(m+1): 
        for j in range(n+1): 
            if i == 0 or j == 0 : 
                L[i][j] = 0
            elif X[i-1] == Y[j-1]: 
                L[i][j] = L[i-1][j-1]+1
            else: 
                L[i][j] = max(L[i-1][j] , L[i][j-1]) 
  
    # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1] 
    return L[m][n]


@app.route('/muscorengine')
@is_registered
def score():
	song_answer = songs_data[session['rand_num']]

	closeness = LongestCommonSubsequence(session['name_candidate'].lower(), song_answer['name'].lower())
	closenesspercent = (closeness*100.0)/len(song_answer['name'])
	print "\n\n\n\n\n\n\n\n closeness percent -->", closenesspercent

	if closenesspercent >= 50.0:
	#if session['name_candidate'].lower() == song_answer['name'].lower():
		if session['clue'] == True:
			session['clue'] = False
			flash('You don\'t get any points since you used clues', 'danger')
			return redirect(url_for('random_security'))
		else:
			session['score'] = session['score'] + 1
			return redirect(url_for('random_security'))
	else:
		return redirect(url_for('gameover'))
	return ('Checking answer...')

################# registration and authorisation
class RegisterForm(Form):
	name = StringField('Your name', [validators.Length(min = 3, max = 50), validators.DataRequired()])

@app.route('/register/', methods = ['GET', 'POST'])
def register():
	session.clear()
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		session['registered'] = True
		session['score'] = 0
		session['clue'] = False
		session['gamecomplete'] = False

		session['unvisited'] = []
		for i in range(0, len(songs_data)):
			print "/n/n/n/n/n",i
			session['unvisited'].append(i)

		session['username'] = name 							#succesfully entered the name, now you can play
		flash("Let's start, {}".format(session['username']), 'success')
		return redirect(url_for('random_security'))
	return render_template('register.html', form = form)

@app.route('/thaan_oru_potanaa')
@is_registered
def redhand():
	return('Njan oru pottan annenu karithiyo ?')

def palindrome(n):
	temp=n
	rev=0
	while(n>0):
	    dig=n%10
	    rev=rev*10+dig
	    n=n//10
	if(temp==rev):
	    return 1
	else:
	    return 0

################# quiting the game or Getting game-over-ed
@app.route('/gameover')
@is_registered
def gameover():
	final_score = session['score']
	final_rand_num = session['rand_num']
	song_name = songs_data[session['rand_num']]['name']
	film_name = songs_data[session['rand_num']]['film']
	release_year = songs_data[session['rand_num']]['year']
	yturl = songs_data[session['rand_num']]['yturl']
	flag = 0
	flag = palindrome(final_score)
	
	if flag == 1:
		category = 'palindrome'
		reaction = 1

	if (final_score)*(100)/(len(songs_data)) <= 10 and flag == 1:
		category = 2
		reaction = random.randint(1, 13)
	if (final_score)*(100)/(len(songs_data)) > 10 and final_score <= 20 and flag == 0:
		category = 4
		reaction = random.randint(1, 9)
	if (final_score)*(100)/(len(songs_data)) > 20 and final_score <= 30 and flag == 0:
		category = 8
		reaction = random.randint(1, 14)
	if (final_score)*(100)/(len(songs_data)) > 30 and final_score <= 40 and flag == 0:
		category = 16
		reaction = random.randint(1, 10)
	if (final_score)*(100)/(len(songs_data)) > 40 and final_score <= 50 and flag == 0:
		category = 32
		reaction = random.randint(1, 5)
	if (final_score)*(100)/(len(songs_data)) > 50 and final_score <= 60 and flag == 0:
		category = 64
		reaction = random.randint(1, 8)
	if (final_score)*(100)/(len(songs_data)) > 60 and final_score < 70 and flag == 0:
		category = 128
		reaction = random.randint(1, 6)
	if (final_score)*(100)/(len(songs_data)) >= 70 and flag == 0:
		category = 256
		reaction = random.randint(1, 7)
	session.clear()
	return render_template('gameover.html', song_name = song_name, film_name = film_name, release_year = release_year, yturl = yturl, final_score = final_score, category = category, reaction = reaction)

################# When the user is lit af and completes the effing game. Shit
@app.route('/gamecomplete')
@is_registered
def gamecomplete():
	if session['gamecomplete'] == True:
		session.clear()
		return render_template('gamecomplete.html')
	else:
		return redirect(url_for('redhand'))

if __name__ == "__main__":
	#app.secret_key = "addyoursecretkeyhere"     #how to add secret key in python anywhere
	app.run(debug = True)