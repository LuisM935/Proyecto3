from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("artwork/<int:artwork_id>", views.artwork, name="artwork"),
    path("artworks/search", views.search_artworks, name="search_artworks"),
    path("artworks/random", views.random_artworks, name="random_artworks"),
    path('artwork/artist/<int:artist_id>', views.artist_detail, name='artist_detail'),
    path('artwork/<int:artwork_id>/add-to-collection/', views.add_to_collection, name='add_to_collection'),
    path("collections/", views.collections, name="collections"),
    path("collection_list/", views.collection_list, name="collection_list"),
    path("collection/add", views.collection_add, name="collection_add"),
    path('collection/view/<int:collection_id>/', views.view_collection, name='view_collection'),
    path('collection/<int:collection_id>/edit/', views.collection_edit, name='collection_edit'),
    path('collection/<int:collection_id>/remove/', views.remove_collection, name='remove_collection'),   
    path("accounts/profile/", views.index, name="index"),
    path("accounts/register/", views.register, name="register")
]