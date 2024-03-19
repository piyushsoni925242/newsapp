from flask import Flask,render_template,request,redirect,url_for,session
import pymysql as sql
from newsapi import NewsApiClient

app =  Flask(__name__)

app.secret_key='something went wrong'

def password_validation(password : str):
    if len(password) >= 8:
        lower = 0
        upper = 0
        number = 0
        special = 0
        for i in password:
            if i.islower():
                lower += 1
            elif i.isupper():
                upper += 1
            elif i.isnumeric():
                number += 1
            elif i in "~!@#$%^&*()+<>":
                special += 1
        if lower>=1 and upper>=1 and number>=1 and special>=1 :
            return True
        else:
            return False
    else:
        return False


newsapi = NewsApiClient(api_key='a56f582dd8b746908593ce592853b04e') 
  
def get_sources_and_domains(): 
    all_sources = newsapi.get_sources()['sources'] 
    sources = [] 
    domains = [] 
    for e in all_sources: 
        id = e['id'] 
        domain = e['url'].replace("http://", "") 
        domain = domain.replace("https://", "") 
        domain = domain.replace("www.", "") 
        slash = domain.find('/') 
        if slash != -1: 
            domain = domain[:slash] 
        sources.append(id) 
        domains.append(domain) 
    sources = ", ".join(sources) 
    domains = ", ".join(domains) 
    return sources, domains 

def db_connect():
    db = sql.connect(host='localhost', port=3306, user='root', database='newsapp')
    cursor = db.cursor() 
    return db, cursor

@app.route('/')
def home():
    if "email" in session:
        top_headlines = newsapi.get_top_headlines(country="in", language="en") 
        total_results = top_headlines['totalResults'] 
        if total_results > 100: 
                total_results = 100
        all_headlines = newsapi.get_top_headlines(country="in", 
                                                        language="en",  
                                                        page_size=total_results)['articles'] 
        return render_template("home.html", all_headlines = all_headlines) 
    else:
        return render_template("login.html") 

@app.route('/login')
def login():
    if 'email' in session:
        return redirect('/')
    else:
        return render_template('login.html')
    

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route("/aftersubmit/", methods=['GET', 'POST'])
def aftersignup():

    if request.method == 'GET':
        return redirect(url_for("signup"))
    
    else:
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        password = request.form.get("password")
        db, cursor = db_connect()

        cmd = f"select * from register where email = '{email}'"
        cursor.execute(cmd)
        data = cursor.fetchall()

        if data:
            msg = "email already exits..."
            return render_template("login.html", msg=msg)
        
        else:
            out = password_validation(password)
            if out:
                cmd = f"insert into register values('{name}', '{phone}', '{email}', '{password}');"
                cursor.execute(cmd)
                db.commit()
                db.close()
                msg = "Signup Successfully...."
                return render_template("login.html", msg=msg)
            else:
                msg = "password does not follow password condition"
                return render_template("signup.html")
    
@app.route("/afterlogin/", methods=['GET', 'POST'])
def afterlogin():
    if request.method == "GET":
        return render_template("login.html")
    
    else:
        email = request.form.get("email")
        password = request.form.get("password")

        db, cursor = db_connect()

        cmd = f"select * from register where email = '{email}'"
        cursor.execute(cmd)
        data = cursor.fetchall()
        db.close()
        if data:
            if data[0][3] == password:
                session['email'] = email
                session['password'] = password
                msg = 'login successfully. . . . '
                return render_template("afterlogin.html", msg=msg)
            else:
                msg = 'invalid password. . . . '
                return render_template("login.html", msg=msg)
        else:

            msg = 'invalid email.... '
            return render_template("login.html", msg=msg)

@app.route('/khabar',methods=['GET','POST'])
def khabar():
    if 'email' in session:
        if request.method == "POST": 
            sources, domains = get_sources_and_domains() 
            keyword = request.form["keyword"] 
            related_news = newsapi.get_everything(q=keyword, 
                                        sources=sources, 
                                        domains=domains, 
                                        language='en', 
                                        sort_by='relevancy') 
            no_of_articles = related_news['totalResults'] 
            if no_of_articles > 100: 
                no_of_articles = 100
            all_articles = newsapi.get_everything(q=keyword, 
                                        sources=sources, 
                                        domains=domains, 
                                        language='en', 
                                        sort_by='relevancy', 
                                        page_size = no_of_articles)['articles'] 
            return render_template("khabar.html", all_articles = all_articles,  
                                keyword=keyword) 
        else:
            return render_template("khabar.html")
    else:
        return render_template('login.html')
@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email')
        return redirect('login')
    else:
        return redirect('login')

if __name__ == "__main__":
    app.run(debug=True)