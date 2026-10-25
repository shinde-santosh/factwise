from django.contrib import admin
from django.urls import path
from django.urls import re_path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(settings.APPNAME + '.urls')),
]

# from drf_yasg import openapi
# from drf_yasg.views import get_schema_view
# from rest_framework.permissions import AllowAny

# api_info = openapi.Info(title="Team Project Planner API", default_version='v1',
#                         description="APIs for managing users, teams, team boards and tasks within a board.")

# schema_view = get_schema_view( api_info, public=True, permission_classes=(AllowAny,),)

# """ swagger urls"""
# urlpatterns += [
    # re_path(r'^api/v1/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # re_path(r'^api/v1/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
# ]
