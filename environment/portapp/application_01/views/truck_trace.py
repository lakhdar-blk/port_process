from django.shortcuts import render, redirect
from django.views import View

import pyodbc
from django.conf import settings
from datetime import datetime


class TruckTrace(View):

    def get(self, request):
        
        if not request.user.is_authenticated:
            return redirect("LOGIN")
        if not request.session['shipid']:
            return redirect("SHIPS")
        if request.session["user_type"] not in ["COMEX", "SUPER_COMEX"]:
            return redirect("HOME")

        return render(request, 'truck_trace.html')


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

        loading_number = request.POST['loading_search']

        try:

            cursor = connector.cursor()
            query = """SELECT IS_FWEIGHT, IS_LOADING, IS_SWEIGHT, IS_FINISHED, 
            DT_TOS_SWEIGHT, DT_PORT_FWEIGHT , DT_LOADING, DT_PORT_SWEIGHT
            FROM TRUCKS WHERE LOADING_NUMBER = ? AND SHIP_ID = ? AND DELETED = 'N' """
            result = cursor.execute(query, (loading_number, shipid)).fetchall()
            cursor.close()


            if len(result) == 0:

                data = {
                    'show': True,
                    'message': 'This truck does not exist or belong to another ship'
                }
            
            else:

                is_fweight = result[0][0].replace(' ', '') if result[0][0] != None else None

                is_loading = result[0][1].replace(' ', '') if result[0][1] != None else None

                is_sweight = result[0][2].replace(' ', '') if result[0][2] != None else None

                is_finished = result[0][3].replace(' ', '') if result[0][3] != None else None
                    
        
                dt_tsweight = result[0][4].time() if result[0][4] != None else ''
                    
                dt_pfweight = result[0][5].time() if result[0][5] != None else ''

                dt_loading = result[0][6].time() if result[0][6] != None else ''

                dt_psweight = result[0][7].time() if result[0][7] != None else ''


                date_format_str = '%Y-%m-%d %H:%M:%S'
                

                if result[0][4] != None and result[0][5] != None:
                    d1 = datetime.strptime(str(result[0][5]), date_format_str)
                    d2 = datetime.strptime(str(result[0][4]), date_format_str)
                    time1 = d1-d2
                else:
                    time1 = ''

                if result[0][6] != None and result[0][5] != None:
                    d1 = datetime.strptime(str(result[0][6]), date_format_str)
                    d2 = datetime.strptime(str(result[0][5]), date_format_str)
                    time2 = d1-d2
                else:
                    time2 = ''

                if result[0][6] != None and result[0][7] != None:
                    d1 = datetime.strptime(str(result[0][7]), date_format_str)
                    d2 = datetime.strptime(str(result[0][6]), date_format_str)
                    time3 = d1-d2
                else:
                    time3 = ''

                data = {
                    
                    "is_fweight": is_fweight,
                    "is_loading": is_loading,
                    "is_sweight": is_sweight,
                    "is_finished": is_finished,
                    "dt_tsweight": dt_tsweight,
                    "dt_pfweight": dt_pfweight,
                    "dt_loading": dt_loading,
                    "dt_psweight": dt_psweight,
                    "time1": time1,
                    "time2": time2,
                    "time3": time3,
                    "loading": loading_number,
                }

            return render(request, 'truck_trace.html', data)

        except Exception as e:

            print(e)
            return render(request, 'truck_trace.html')

        