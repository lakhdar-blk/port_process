from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
import json
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
        query = "SELECT * FROM TRUCKS WHERE IS_LOADING = 'X' AND SHIP_ID = ? AND DELETED = 'N' "
        result = cursor.execute(query, (shipid)).fetchall()
        cursor.close()

        return result

    except Exception as e:

        print(e)
        return False


def check_rollback(request):

    cursor = connector.cursor()
    query = "SELECT [rollback] from application_01_users where username = ?"
    rollback = cursor.execute(query, (str(request.user), )).fetchall()
    cursor.close()

    return rollback[0][0]


class Loading(View):

    def get(self, request):

        if not request.user.is_authenticated:
            return redirect("LOGIN")
        if not request.session['ship']:
            return redirect("SHIPS")
        if request.session["user_type"] not in ["COMEX", "SUPER_COMEX", "LACHING", "QUALITY"]:
            return redirect("HOME")
        
        shipid = request.session['shipid']

        data = {}
        trucks = get_trucks(shipid)
 

        if trucks != False:

            data = { 'trucks': trucks, 'rollback': check_rollback(request) }
            return render(request, 'loading.html', data)

        else:

            return render(request, 'loading.html', data)


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
            query = "SELECT * FROM TRUCKS WHERE IS_LOADING = 'X' AND DELETED = 'N' AND SHIP_ID = '"+shipid+"'"

            if ("'" in loading_number or '"' in loading_number or "--" in loading_number or ";" in loading_number)\
                or ("'" in vessel_name or '"' in vessel_name or "--" in vessel_name or ";" in vessel_name):
                trucks = []

            elif from_date == "" and to_date == "" and  loading_number == "" \
                and vessel_name == "":
                trucks = []

            else:

                execute = False

                if from_date != "" and to_date != "":
                    
                    query = query + " AND DT_PORT_FWEIGHT BETWEEN '"+from_date+"' AND '"+to_date+"'"
                    execute = True

                if loading_number != "":

                    if "DT_PORT_FWEIGHT" in query:
                        query = query + " AND LOADING_NUMBER ='" + loading_number + "'" 
                    else:
                        query = query + " AND LOADING_NUMBER ='" + loading_number + "'" 
                    execute = True

                if vessel_name != "":
                    
                    if ("DT_PORT_FWEIGHT" in query) or ("LOADING_NUMBER" in query): 
                        query = query + " AND VESSEL_NAME =' " + vessel_name + "'" 
                    else:
                        query = query + " AND VESSEL_NAME =' " + vessel_name + "'" 
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
                data['rollback'] = check_rollback(request) 


            return render(request, 'loading.html', data)

        if 'btnsave' in request.POST:

            user = str(request.user)

            try:

                loading_number = request.POST['loading_number']

                check_cursor = connector.cursor()
                query = """ SELECT IS_LOADING FROM TRUCKS WHERE LOADING_NUMBER = ? """
                record = check_cursor.execute(query, (loading_number,)).fetchall()
                check_cursor.close()


                if record[0][0].replace(' ', '') == 'X' :
                    
                    saving_date = datetime.now().strftime("%Y-%m-%d %H:%M")

                    cursor = connector.cursor()
                    query = """UPDATE TRUCKS SET 

                    DT_LOADING = ?,
                    IS_LOADING = ?,
                    IS_SWEIGHT = ?,
                    USER_LOADING = ?

                    WHERE LOADING_NUMBER = ?"""

                    cursor.execute(query, (saving_date, 'C', 'X', user, loading_number))
                    cursor.commit()
                    cursor.close()


                    data = {
                        'show': True,
                        'message': 'Saved successfully'
                    }
                    
                else:

                    if record[0][0].replace(' ', '') == 'C':

                        data = {
                        'show': True,
                        'message': 'This truck was validated by another user'
                        }


                    elif record[0][0].replace(' ', '') == 'RB':

                        data = {
                        'show': True,
                        'message': 'This truck was moved to the first weight step by another user'
                        }
                    

                trucks = get_trucks(shipid)

                if trucks != False:
                    data['trucks'] = trucks
                    data['rollback'] = check_rollback(request) 


                return render(request, 'loading.html', data)
            
            except Exception as e:

                print(e)

                data = {
                    'show': True,
                    'message': 'An error has been occured !'
                }

                return render(request, 'loading.html', data)

        
        if 'confirmed' in request.POST:

            try:

                data = {}

                loading_number = request.POST['rollback_loading']

                check_cursor = connector.cursor()
                query = """ SELECT IS_LOADING FROM TRUCKS WHERE LOADING_NUMBER = ? """
                record = check_cursor.execute(query, (loading_number,)).fetchall()
                check_cursor.close()

                if record[0][0].replace(' ', '') == 'RB':

                    data ['show'] = True
                    data['message'] = "This truck was moved to the port first weight step by another user"

                elif record[0][0].replace(' ', '') == 'C':

                    data ['show'] = True
                    data['message'] = "Cannot rollback this truck, it was moved to the second weight step by another user"

                else:

                    cursor = connector.cursor()
                    query = """
                    UPDATE TRUCKS
                    SET
                    IS_LOADING = ?,
                    IS_FWEIGHT = ?,
                    DT_PORT_FWEIGHT = ?,
                    PORT_FWEIGHT = ?,
                    USER_FWEIGHT = ?
                    WHERE LOADING_NUMBER = ?
                    """
                    
                    cursor.execute(query, ('RB', 'X', None, None, None, loading_number))
                    cursor.commit()
                    cursor.close()

                    data ['show'] = True
                    data['message'] = "Rollback operation terminated successfully"

                trucks = get_trucks(shipid)

                if trucks != False:

                    data['trucks'] = trucks 
                    data['rollback'] = check_rollback(request) 
                    return render(request, 'loading.html', data)

                else:

                    return render(request, 'loading.html', data)


            except Exception as e:

                print(e)

                data = {}                
                data ['show'] = True
                data['message'] = "An error has occured"

                return render(request, 'loading.html', data)