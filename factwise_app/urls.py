from django.urls import re_path as url

from .views.users import UsersView
from .views.teams import TeamsView
from .views.project_board import ProjectBoardView

""" Users """
urlpatterns = [
    url(r'^users/$', UsersView.as_view({'get': 'list', 'post': 'create'})),
    url(r'^users/(?P<id>.+)/teams/$', UsersView.as_view({'get': 'teams'})),
    url(r'^users/(?P<id>.+)/$', UsersView.as_view({'get': 'retrieve', 'put': 'partial_update'})),
]

""" Teams """
urlpatterns += [
    url(r'^teams/$', TeamsView.as_view({'get': 'list', 'post': 'create'})),
    url(r'^teams/(?P<id>.+)/users/$', TeamsView.as_view({'get': 'users'})),
    url(r'^teams/(?P<id>.+)/add-users/$', TeamsView.as_view({'post': 'add_users'})),
    url(r'^teams/(?P<id>.+)/remove-users/$', TeamsView.as_view({'post': 'remove_users'})),
    url(r'^teams/(?P<id>.+)/boards/$', ProjectBoardView.as_view({'get': 'list'})),
    url(r'^teams/(?P<id>.+)/$', TeamsView.as_view({'get': 'retrieve', 'put': 'partial_update'})),
]

""" Boards """
urlpatterns += [
    url(r'^boards/$', ProjectBoardView.as_view({'post': 'create'})),
    url(r'^boards/(?P<id>.+)/close/$', ProjectBoardView.as_view({'put': 'close'})),
    url(r'^boards/(?P<id>.+)/export/$', ProjectBoardView.as_view({'get': 'export'})),
]

""" Tasks """
urlpatterns += [
    url(r'^tasks/$', ProjectBoardView.as_view({'post': 'create_task'})),
    url(r'^tasks/(?P<id>.+)/$', ProjectBoardView.as_view({'put': 'update_task'})),
]
