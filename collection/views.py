from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
import random
from collection.models import Artwork, Collection, Artist
from django.contrib.postgres import search
from django.core.paginator import Paginator
from .forms import CollectionForm

def register(request):
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            username = f.cleaned_data.get('username')
            raw_password = f.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return HttpResponseRedirect('/')

    else:
        f = UserCreationForm()

    return render(request, 'registration/registration_form.html', {'form': f})


def artwork(request, artwork_id):
    artwork = Artwork.objects.get(pk=artwork_id)
    collections = Collection.objects.filter(owner=request.user)
    return render(request, 'collection/artwork.html', {'artwork': artwork, 'collections': collections})

def collections(request):
    collections = Collection.objects.filter(owner=request.user)
    return render(request, 'collection/collections.html',
                  {'collections': collections})


def collection_list(request):
    collections = Collection.objects.filter(owner=request.user)
    return render(request, 'collection/collection_list.html',
                  {'collections': collections})

def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    return render(request, 'collection/artist.html', {'artist': artist})
    
def view_collection(request, collection_id):
    collection = Collection.objects.get(pk=collection_id)
    artworks = collection.artworks.all()
    return render(request, 'collection/view_collection.html', {'collection': collection, 'artworks': artworks})

def add_to_collection(request, artwork_id):
    if request.method == 'POST':
        artwork = get_object_or_404(Artwork, pk=artwork_id)
        collection_id = request.POST.get('collection_id')
        collection = get_object_or_404(Collection, pk=collection_id, owner=request.user)

        collection.artworks.add(artwork)

        return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})

    return HttpResponse(status=400)

def collection_edit(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    if request.method == 'POST':
        
        collection.name = request.POST.get('name')
        collection.description = request.POST.get('description')
        collection.save()
        return  redirect('collections') 
    return render(request, 'collection/collection_edit.html', {'collection': collection})

def remove_collection(request, collection_id):
    if request.method == 'POST':
        collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
        collection.delete()
        return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})
    return HttpResponse(status=400)

def collection_add(request):
    form = None
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            collection = Collection(
                    name=name,
                    description=description,
                    owner=request.user)
            collection.save()
            return HttpResponse(status=204,
                                headers={'HX-Trigger': 'listChanged'})

    return render(request,
                  'collection/collection_form.html',
                  {'form': form})


def index(request):
    artworks = list(Artwork.objects.all())
    random_works = []
    if artworks:
        random_works = random.sample(artworks, 4)
    return render(request, 'collection/index.html', {'artworks': random_works})


def random_artworks(request):
    artworks = list(Artwork.objects.all())
    random_works = []
    if artworks:
        random_works = random.sample(artworks, 4)
    return render(request, 'collection/artworks_random.html',
                  {'artworks': random_works})


def search_artworks(request):
    if request.method == 'GET':
        value = request.GET['search']
        artworks = ft_artworks(value)

        paginator = Paginator(artworks, 4)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, 'collection/artwork_search.html',
                      {'artworks': artworks, 'search_value': value,
                       "page_obj": page_obj})
    else:
        return render(request, 'collection/index.html',
                      {'artworks': [], 'search_value': None})


def ft_artworks(value):
    vector = (
        search.SearchVector("title", weight="A")
        + search.SearchVector("author__name", weight="B")
        + search.SearchVector("style__name", weight="C")
        + search.SearchVector("genre__name", weight="C")
    )
    query = search.SearchQuery(value, search_type="websearch")
    return (
        Artwork.objects.annotate(
            search=vector,
            rank=search.SearchRank(vector, query),
        )
        .filter(search=query)
        .order_by("-rank")
    )