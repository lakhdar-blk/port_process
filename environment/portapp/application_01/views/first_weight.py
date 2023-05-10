
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


def get_trucks(shipid):

    try:
            
        cursor = connector.cursor()
        query = "SELECT * FROM TRUCKS WHERE IS_FWEIGHT = 'X' AND SHIP_ID = ? AND DELETED = 'N' "
        result = cursor.execute(query, (shipid)).fetchall()
        cursor.close()

        print(len(result))
        return result

    except Exception as e:

        print(e)
        return False


class First_weight(View):

    def get(self, request):

        if not request.user.is_authenticated :
            return redirect("LOGIN")
        if not request.session['ship']:
            return redirect("SHIPS")
        if request.session["user_type"] not in ["COMEX", "SUPER_COMEX", "LACHING", "QUALITY", "TRANSITOR"]:
            return redirect("HOME")
        
        shipid = request.session['shipid']

        data = {}
        trucks = get_trucks(shipid)

   
        if trucks != False:

            data = { 'trucks': trucks }
            return render(request, 'first_weight.html', data)

        else:

            return render(request, 'first_weight.html', data)


    def post(self, request):

        connector = pyodbc.connect(
                "Driver={" + settings.DATABASES['default']['OPTIONS']['driver'] + "};"
                "Server=" + settings.DATABASES['default']['HOST'] + ";"
                "Database=" + settings.DATABASES['default']['NAME'] + ";"
                "UID=" + settings.DATABASES['default']['USER'] + ";"
                "PWD=" + settings.DATABASES['default']['PASSWORD'] + ";"
                "Trusted_Connection=no;"
                "MARS_Connection=Yes;"
        )


        shipid = request.session['shipid']

        data = {}

        if 'btnsearch' in request.POST:

            from_date = request.POST['from_date'].strip()        
            to_date = request.POST['to_date'].strip() 
            loading_number = str(request.POST['loading_search'].strip())
            vessel_name = str(request.POST['vessel_search'].strip())

            from_date = from_date.replace('T', ' ')
            to_date = to_date.replace('T', ' ')

            cursor = connector.cursor()
            query = "SELECT * FROM TRUCKS WHERE IS_FWEIGHT = 'X' AND DELETED = 'N' AND SHIP_ID = '"+shipid+"'"

            if ("'" in loading_number or '"' in loading_number or "--" in loading_number or ";" in loading_number)\
                or ("'" in vessel_name or '"' in vessel_name or "--" in vessel_name or ";" in vessel_name):
                trucks = []

            elif from_date == "" and to_date == "" and  loading_number == "" \
                and vessel_name == "":
                trucks = []

            else:

                execute = False

                if from_date != "" and to_date != "":
                    
                    query = query + " AND DT_TOS_SWEIGHT BETWEEN '"+from_date+"' AND '"+to_date+"'"
                    execute = True

                if loading_number != "":

                    if "DT_TOS_SWEIGHT" in query:
                        query = query + " AND LOADING_NUMBER ='" + loading_number + "'" 
                    else:
                        query = query + " AND LOADING_NUMBER ='" + loading_number + "'" 
                    execute = True

                if vessel_name != "":
                    
                    if ("DT_TOS_SWEIGHT" in query) or ("LOADING_NUMBER" in query): 
                        query = query + " AND VESSEL_NAME =' " + vessel_name + "'" 
                    else:
                        query = query + " AND VESSEL_NAME =' " + vessel_name + "'" 

                        print(query)
                    execute = True

                if execute:
                    trucks = cursor.execute(query ).fetchall()
                    cursor.close()

                else:
                    trucks = []


            if len(trucks) == 0:
                data ['show'] = True
                data['message'] = "No results found"

            else:
                data['trucks'] = trucks

            return render(request, 'first_weight.html', data)

        if 'btnsave' in request.POST:
            
            user = str(request.user)

            try:

                port_first_weight = request.POST['pfweight']
                loading_number = request.POST['loading_number']

                check_cursor = connector.cursor()
                query = """ SELECT IS_FWEIGHT FROM TRUCKS WHERE LOADING_NUMBER = ? """
                record = check_cursor.execute(query, (loading_number,)).fetchall()
                check_cursor.close()

                if record[0][0].replace(' ', '') == 'C':

                    data = {
                    'show': True,
                    'message': 'The port first weight already added by another user'
                    }

                else:

                    saving_date = datetime.now().strftime("%Y-%m-%d %H:%M")

                    cursor = connector.cursor()
                    query = """UPDATE TRUCKS SET 

                    PORT_FWEIGHT = ?,
                    DT_PORT_FWEIGHT = ?,
                    IS_FWEIGHT = ?,
                    IS_LOADING = ?,
                    USER_FWEIGHT = ?

                    WHERE LOADING_NUMBER = ?"""

                    cursor.execute(query, (port_first_weight, saving_date, 'C', 'X', 
                    user, loading_number))
                    cursor.commit()
                    cursor.close()


                    data = {
                        'show': True,
                        'message': 'Port first weight added successfully'
                    }

                trucks = get_trucks(shipid)

                if trucks != False:
                    data['trucks'] = trucks

                return render(request, 'first_weight.html', data)
            
            except Exception as e:

                print(e)

                data = {
                    'show': True,
                    'message': 'An error has been occured !'
                }

                return render(request, 'first_weight.html', data)