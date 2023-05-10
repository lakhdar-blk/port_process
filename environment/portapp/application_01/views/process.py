from urllib import request
from django.shortcuts import render, redirect
from django.views import View

from ..models import Users, User

from django.contrib.auth import authenticate, login, logout

import pyodbc
from django.conf import settings
#from django.contrib.sessions.models import Session

connector = pyodbc.connect(
        "Driver={" + settings.DATABASES['default']['OPTIONS']['driver'] + "};"
        "Server=" + settings.DATABASES['default']['HOST'] + ";"
        "Database=" + settings.DATABASES['default']['NAME'] + ";"
        "UID=" + settings.DATABASES['default']['USER'] + ";"
        "PWD=" + settings.DATABASES['default']['PASSWORD'] + ";"
        "Trusted_Connection=no;"
        "MARS_Connection=Yes;"
)

def get_user_type(username):

    cursor = connector.cursor()
    query = "SELECT * FROM application_01_users WHERE username = ?"
    result = cursor.execute(query, (username)).fetchall()
    cursor.close()

    print(result[0][5])
    
    return result[0][5]

class login_page(View):

    def get(self, request):

        if request.user.is_authenticated:
            return redirect("HOME")

        return render(request, 'login_page.html')    
    

    def post(self, request):

        username = request.POST['username']
        password = request.POST['password']


        try:

            user = authenticate(
                request=request, 
                username=username, 
                password=password)

            if user != None:

                request.session["user_type"] = get_user_type(username)

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.session['ship'] = ''
                return redirect('SHIPS')

            else:

                return render(request, 'login_page.html', {'message': 'The Username or password is incorrect', 'show': True})

        except Exception as e:
            
            print(e)
            return render(request, 'login_page.html', {'message': 'An error occured in the login process', 'show': True})


class Logout(View):

    def get(self, request):

        logout(request)
        return redirect('LOGIN')


class Home(View):

    def get(self, request):

        if not request.user.is_authenticated :
            return redirect("LOGIN")
        if not request.session['ship']:
            return redirect("SHIPS")
        
        status = ["IS_FWEIGHT", "IS_LOADING", "IS_SWEIGHT", "IS_FINISHED"]
        tnumbers = []

        for i in range(4):
            statu = status[i]
            
            cursor = connector.cursor()
            query = "SELECT * FROM TRUCKS WHERE "+ statu +" = ? AND SHIP_ID = ?"
            result = cursor.execute(query, ('X', request.session['shipid'])).fetchall()
            tnumbers.append(len(result))
            cursor.close()

        print(tnumbers)
        return render(request, 'home.html')    
    

    def post(self, request):

        return render(request, 'login_page.html')

