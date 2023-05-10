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
        query = "SELECT * FROM TRUCKS WHERE IS_FINISHED = 'X' AND SHIP_ID = ? AND DELETED = 'N' "
        result = cursor.execute(query, (shipid)).fetchall()
        cursor.close()

        print(len(result))

        return result

    except Exception as e:

        print(e)
        return False


def search_function(request, btn, step, time):

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
    data = {btn: True}

    from_date = request.POST['from_date'].strip()        
    to_date = request.POST['to_date'].strip() 
    loading_number = str(request.POST['loading_search'].strip())
    vessel_name = str(request.POST['vessel_search'].strip())    

    from_date = from_date.replace('T', ' ')
    to_date = to_date.replace('T', ' ')

    cursor = connector.cursor()
    query = "SELECT * FROM TRUCKS WHERE " + step + " = 'X' AND DELETED = 'N' AND SHIP_ID = '"+shipid+"'"


    if ("'" in loading_number or '"' in loading_number or "--" in loading_number or ";" in loading_number)\
        or ("'" in vessel_name or '"' in vessel_name or "--" in vessel_name or ";" in vessel_name):
        trucks = []

    elif from_date == "" and to_date == "" and  loading_number == "" \
        and vessel_name == "" and ('btnsearch' in request.POST):
        
        trucks = []

    elif from_date == "" and to_date == "" and  loading_number == ""\
        and vessel_name == "" and (btn in request.POST):

        trucks = cursor.execute(query).fetchall()
        cursor.close()
    
    else:

        execute = False

        if from_date != "" and to_date != "":
            
            query = query + " AND "+time+" BETWEEN '"+from_date+"' AND '"+to_date+"'"
            execute = True

        if loading_number != "":

            if time in query:
                query = query + " AND LOADING_NUMBER ='" + loading_number + "'" 
            else:
                query = query + " AND LOADING_NUMBER ='" + loading_number + "'" 
            execute = True

        if  vessel_name != "":
            
            if (time in query) or ("LOADING_NUMBER" in query): 
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
    return data


def check_rollback(request):

    cursor = connector.cursor()
    query = "SELECT [rollback] from application_01_users where username = ?"
    rollback = cursor.execute(query, (str(request.user), )).fetchall()
    cursor.close()

    return rollback[0][0]



class Finished(View):

    def get(self, request):

        if not request.user.is_authenticated:
            return redirect("LOGIN")
        if not request.session['ship']:
            return redirect("SHIPS")
        if request.session["user_type"] not in ["COMEX", "SUPER_COMEX"]:
            return redirect("HOME")
            
        shipid = request.session['shipid']

        data = {
            'pfwb': False,
            'loadb': False,
            'pswb': False,
            'finib': True
        }

        trucks = get_trucks(shipid)

        if trucks != False:

            data['trucks'] = trucks 
            data['rollback'] = check_rollback(request) 
            return render(request, 'finished.html', data)

        else:

            return render(request, 'finished.html', data)



    def post(self, request):

        shipid = request.session['shipid']

        if 'btnsearch' in request.POST:

            return render(request, 'finished.html', search_function(request, 'finib', 
            'IS_FINISHED', 'DT_PORT_SWEIGHT'))

        if 'pfwb' in request.POST:

            return render(request, 'finished.html', search_function(request, 'pfwb', 
            'IS_FWEIGHT', 'DT_TOS_SWEIGHT'))

        if 'loadb' in request.POST:

            return render(request, 'finished.html', search_function(request, 'loadb', 
            'IS_LOADING', 'DT_PORT_FWEIGHT'))

        if 'pswb' in request.POST:

            return render(request, 'finished.html', search_function(request, 'pswb', 
            'IS_SWEIGHT', 'DT_LOADING'))

        if 'finib' in request.POST:

            return render(request, 'finished.html', search_function(request, 'finib', 
            'IS_FINISHED', 'DT_PORT_SWEIGHT'))

        if 'confirmed' in request.POST:

            try:
                
                data = {
                    'pfwb': False,
                    'loadb': False,
                    'pswb': False,
                    'finib': True
                }

                loading_number = request.POST['rollback_loading']

                check_cursor = connector.cursor()
                query = """ SELECT IS_FINISHED FROM TRUCKS WHERE LOADING_NUMBER = ? """
                record = check_cursor.execute(query, (loading_number,)).fetchall()
                check_cursor.close()

                if record[0][0].replace(' ', '') == 'RB' :

                    data ['show'] = True
                    data['message'] = "The rollback operation on this truck was performed by another user"

                else:

                    cursor = connector.cursor()
                    query = """
                    UPDATE TRUCKS
                    SET
                    IS_FINISHED = ?,
                    IS_SWEIGHT = ?,
                    DT_PORT_SWEIGHT = ?,
                    USER_SWEIGHT = ?,
                    PORT_SWEIGHT = ?
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
                    return render(request, 'finished.html', data)

                else:

                    return render(request, 'finished.html', data)

            except Exception as e:

                print(e)

                data = {}                
                data ['show'] = True
                data['message'] = "An error has occured"

                return render(request, 'finished.html', data)

        return render(request, 'finished.html')