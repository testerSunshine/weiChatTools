from django.conf.urls import url

from weiChatToken import views

urlpatterns = [
    url(r'token/', views.wechat, name="wechat"),

]