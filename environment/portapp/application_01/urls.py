from django.urls import path
from .views import login_page, Home, Logout, Second_weight, Finished, Loading, First_weight, TruckTrace, Boats
urlpatterns = [
    path('', login_page.as_view(), name="LOGIN"),
    path('home/', Home.as_view(), name="HOME"),
    path('logout/', Logout.as_view(), name="LOGOUT"),
    path('SECOND_WEIGHT/', Second_weight.as_view(), name="SWEIGHT"),
    path('LOADING/', Loading.as_view(), name="LOADING"),
    path('FIRST_WEIGHT/', First_weight.as_view(), name="FWEIGHT"),
    path('FINISHED/', Finished.as_view(), name="FINISHED"),
    path('TRUCKTRACE/', TruckTrace.as_view(), name="TUCKTRACE"),
    path('BOAT_SELECTION/', Boats.as_view(), name="SHIPS"),
    #path('newform/', newForm, name="NEWRE"),
]