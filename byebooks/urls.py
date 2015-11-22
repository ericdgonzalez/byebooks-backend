"""byebooks URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    #API STARTS HERE
    #FOR DEBUGGING ONLY url(r'^user$', 'byebooks.endpoints.get_user', name='get_user'),
    url(r'^create_user$', 'byebooks.endpoints.create_user', name='create_user'),
    url(r'^launch$',  'byebooks.interfaces.launchpad'),
    url(r'^get_wishlist$', 'byebooks.endpoints.get_wishlist'),
    url(r'^get_storefront$', 'byebooks.endpoints.get_storefront'),
    url(r'^append_wishlist$', 'byebooks.endpoints.append_wishlist'),
    url(r'^append_storefront$', 'byebooks.endpoints.append_storefront'),
    url(r'^remove_wishlist$', 'byebooks.endpoints.remove_wishlist'),
    url(r'^remove_storefront$', 'byebooks.endpoints.remove_storefront'),
    url(r'^send_message$', 'byebooks.endpoints.send_message'),
    url(r'^get_conversations$', 'byebooks.endpoints.get_conversations'),
    url(r'^get_conversation$', 'byebooks.endpoints.endpoint_get_conversation'),
    url(r'^remove_conversation$', 'byebooks.endpoints.endpoint_remove_conversation'),
    url(r'^search$', 'byebooks.endpoints.endpoint_search'),
    url(r'^authenticate$', 'byebooks.endpoints.authenticate'),
    url(r'^resolve$', 'byebooks.endpoints.resolve_id'),

]
