
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import index, SearchNameList, SearchPhoneList, SignupList, SpamList, ContactsList, LoginList

urlpatterns = [
    path('', index, name='index'),
    path('signup/', SignupList.as_view()),
    path('login/', LoginList.as_view()),
    path('contacts/', ContactsList.as_view()),
    path('spam/', SpamList.as_view()),
    path('search_name/', SearchNameList.as_view()),
    path('search_phone/', SearchPhoneList.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
