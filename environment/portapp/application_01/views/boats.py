from django.shortcuts import render, redirect
from django.views import View

import pyodbc
from django.conf import settings

from datetime import datetime


connector = pyodbc.connect(
        "Driver={" + settings.DATABASES['default']['OPTIONS']['driver'] + "};"
        "Server=" + settings.DATABASES['default']['HOST'] + ";"
        "Database=" + settings.DATABASES['default']['NAME'] + ";"
        "UID=" + settings.DATABASES['default']['USER'] + ";"
        "PWD=" + settings.DATABASES['default']['PASSWORD'] + ";"
        "Trusted_Connection=no;"
        "MARS_Connection=Yes;"
)


class Boats(View):

    def get(self, request):

        if not request.user.is_authenticated:
            return redirect("LOGIN")

        request.session['ship']=''
        
        cursor = connector.cursor()
        query = "SELECT * FROM SHIPS WHERE COMPLETED = 'NO' "
        ships = cursor.execute(query).fetchall()
        cursor.close()

        data= {
            'ships': ships
        }

        return render(request, 'selectboats.html', data)


    def post(self, request):

        try:
        
            cursor = connector.cursor()
            query = "SELECT name FROM SHIPS where shipid = ?"
            res = cursor.execute(query, (str(request.POST['ship']))).fetchall()
            name = res[0][0]
            request.session['ship'] = name
            request.session['shipid'] = request.POST['ship']
            
            status = ["IS_FWEIGHT", "IS_LOADING", "IS_SWEIGHT", "IS_FINISHED"]
            tnumbers = []

            for i in range(4):
                statu = status[i]
                
                cursor = connector.cursor()
                query = "SELECT * FROM TRUCKS WHERE "+ statu +" = ? AND SHIP_ID = ? AND DELETED = 'N'"
                result = cursor.execute(query, ('X', request.session['shipid'])).fetchall()
                tnumbers.append(len(result))
                cursor.close()

            data = {
                "pwf": tnumbers[0],
                "ld": tnumbers[1],
                "psw": tnumbers[2],
                "comp": tnumbers[3]
            }

            return render(request, 'home.html', data)
    
        except Exception as e:

            print(e)
            request.session['ship']=''

            cursor = connector.cursor()
            query = "SELECT * FROM SHIPS WHERE COMPLETED = 'NO'"
            ships = cursor.execute(query).fetchall()
            cursor.close()

            data= {
                'ships': ships
            }

            
            return render(request, 'selectboats.html', data)
