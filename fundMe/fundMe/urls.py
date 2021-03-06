"""fundMe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from userProfile import views
from django.conf import settings  # new
from django.conf.urls.static import static  # new

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('special/', views.special, name='special'),
    path('userProfile/', include('userProfile.urls')),
    path('logout/', views.user_logout, name='logout'),
    path('projects/', views.show_projects, name="projects"),
    path('project/<int:id>', views.show_a_project, name="show_project"),
    path('<str:username>/projects/', views.get_projects, name='user_projects'),
    path('category/<int:id>', views.get_category_projects, name="get_category_projects"),
    path('search/<str:data>', views.search, name="search_projects"),
    path('ratings/', include('star_ratings.urls', namespace='ratings'))

]

if settings.DEBUG:  # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
