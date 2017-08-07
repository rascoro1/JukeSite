from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import loader
from JukeSite.models import Track, Room, Queue
from DjangoJukeSite.CBM import CBMInterface, Song
import threading
import os

Interface = CBMInterface()
Interface.interface_name = ""
Interface.start_music_client()
Interface.music_manager_logon('andcope1995@gmail.com', 'Basketball12@1995')

def index(request):
    """
    passes all track database objects to index.html
    :param request:
    :return:
    """
    # # latest_question_list = Track.objects.order_by('-pub_date')[:5]
    current_queue = None
    tracks = Track.objects.all()
    rooms = Room.objects.all()
    queues = Queue.objects.all()

    first_room = rooms[0]

    for q in queues:
        if q.id == first_room.queue_id:
            current_queue = q

    template = loader.get_template('dashboard.html')
    context = {
        'rooms': rooms,
        'queue': current_queue,
        'add_results': "Select a room to view/add songs to the queue."
    }
    return HttpResponse(template.render(context, request))
    # return render_to_response('trackQueue/index.html', {'tracks': Track.objects.all()})


def room(request, room_id):
    """
    Represents a user being in a specific room.

    :param request:
    :param room_id: [int] The unique room ID. This will help identify the Queue.

    :return:
    """
    current_room = None
    queue_songs = []
    tracks = Track.objects.all()
    rooms = Room.objects.all()
    queues = Queue.objects.all()

    current_room = get_current_room(room_id)
    # Find all the current songs in the  appropriate Queue
    songs = Queue.objects.filter(room_id=room_id)
    for s in songs:
        song_info = Track.objects.filter(storeId=s.storeId)
        queue_songs.append(song_info)

    template = loader.get_template('dashboard.html')
    context = {
        'tracks': tracks,
        'rooms': rooms,
        'current_room': current_room,
        'queue': queue_songs
    }



    return HttpResponse(template.render(context, request))


def search_song(request, room_id):
    """
    Represents a user being in a room and having the ability to search

    :param request: Mandatory request
    :param room_id: The room the user is currently in
    :return:
    """
    print("THIS IS THE REQUEST DIR: {}".format(dir(request)))
    current_room = None
    queue_songs = []
    rooms = Room.objects.all()
    template = loader.get_template('dashboard.html')
    song_query = None
    song_results = None
    new_room_name = None

    # Get the search query string
    if request.method == 'GET':
        song_query = request.GET.get('search_box', None)

    if request.method == 'GET':
        new_room_name = request.GET.get('name_box', None)



    current_room = get_current_room(room_id)
    queue_songs = get_queue_songs(room_id)
    song_results = get_song_query_results(song_query)

    if new_room_name is not None:
        print("NEW ROOM IS NOT NONE: {}".format(new_room_name))
        current_room.name = new_room_name
        current_room.save()

    print(queue_songs)
    context = {
       'rooms': rooms,
       'current_room': current_room,
       'song_results': song_results,
       'queue': queue_songs
    }
    return HttpResponse(template.render(context, request))

def display_cache(request):
    template = loader.get_template('display_cache.html')
    songs = os.listdir(Interface.music_manager.SONG_DIR)
    cached_songs = []
    for song in songs:
        print("Looking for song {}".format(song))
        song_id = song.rstrip('.mp3')
        res = Track.objects.filter(storeId=song_id)
        if len(res) != 0:
            cached_songs.append(res[0])
            print("Found a track!")
        else:
            print("Information on this song '{}' could not be found in the database.".format(song))

    cached_songs = sorted(cached_songs, key=lambda x: x.artist, reverse=True)

    context = {
        'songs': cached_songs,
    }

    return HttpResponse(template.render(context, request))


def add_song(request, room_id, song_id):
    """
    Repersents the view that is presented when the user submits a song to the queue.

    :param request: Mandatory request parameter
    :param room_id: The room the current user is in
    :param song_id: The song that is being added to the room
    :return:
    """

    current_room = None
    add_results = None
    queue_songs = []
    tracks = Track.objects.all()
    rooms = Room.objects.all()
    queues = Queue.objects.all()
    template = loader.get_template('dashboard.html')

    # Get the search query string
    if request.method == 'GET':
        song_query = request.GET.get('search_box', None)

    if request.method == 'GET':
        new_room_name = request.GET.get('name_box', None)


    # Get information
    current_room = get_current_room(room_id)
    queue_songs = get_queue_songs(room_id)
    song_in_queue = is_song_in_queue(song_id, queue_songs)
    song_results = get_song_query_results(song_query)


    if song_in_queue:
        add_results = "ERROR: Song already in the Queue"
    else:
        print("THIs is the queuers username: {}".format(request.user.username))
        q = Queue(storeId=song_id, room_id=room_id, user=request.user.username, position=1)
        q.save()
        add_results = "Song added to the queue."
        queue_songs = get_queue_songs(room_id)


    context = {
       'tracks': tracks,
       'rooms': rooms,
       'current_room': current_room,
        'song_results': song_results,
        'add_results': add_results,
       'queue': queue_songs
    }
    return HttpResponse(template.render(context, request))


def skip_song(request, room_id):
    """
    Repersents the view that is presented when the user submits a song to the queue.

    :param request: Mandatory request parameter
    :param room_id: The room the current user is in
    :param song_id: The song that is being added to the room
    :return:
    """

    current_room = None
    add_results = None
    queue_songs = []
    rooms = Room.objects.all()
    template = loader.get_template('dashboard.html')

    # Get the search query string
    if request.method == 'GET':
        song_query = request.GET.get('search_box', None)

    if request.method == 'GET':
        new_room_name = request.GET.get('name_box', None)


    # Get information
    current_room = get_current_room(room_id)
    queue_songs = get_queue_songs(room_id)
    song_results = get_song_query_results(song_query)

    cur_room_id = current_room.id
    cur_room_obj = Interface.find_room(cur_room_id)

    if cur_room_obj is not None:
        Interface.next_song(cur_room_obj)
        add_results = "Skipped song successfully."

    context = {
       'rooms': rooms,
       'current_room': current_room,
        'song_results': song_results,
        'add_results': add_results,
       'queue': queue_songs
    }
    return HttpResponse(template.render(context, request))


def get_queue_songs(room_id):
    """
    Get all of the songs in the current room/queue
    :param room_id: The room that the current user is in

    :return:A list of Django tracks model objects
    """
    # Find all the current songs in the  appropriate Queue
    queue_songs = []
    songs = Queue.objects.filter(room_id=room_id)
    for s in songs:
        print("A Song ID: {}".format(s.storeId))
        song_info = Track.objects.get(storeId=s.storeId)
        song_dict = {'song': song_info, 'user': s.user}
        queue_songs.append(song_dict)
    return queue_songs


def get_current_room(room_id):
    """
    Get the current room in the database

    :param room_id:
    :return:
    """
    return Room.objects.get(id=room_id)


def is_song_in_queue(song_id, queue_songs):
    """
    Is the song already in the Queue?
    :param song_id: Is this song in the queue
    :param queue_songs: A list of songs to compare the song_id
    :return:
    """
    for song in queue_songs:
        if song_id == song['song'].storeId:
            return True
    return False


def get_song_query_results(song_query):
    """
    Get the song query results entered by the user

    :param song_query: The search key word to search google
    :return: A list of songs from the music manager.
    """
    song_results = None
    if song_query is not None:
        song_results = Interface.music_manager.search_song(str(song_query))
        # Add the results to our database
        for song in song_results:
            song = song['track']
            t = Track(storeId=song['storeId'], title=song['title'], album=song['album'], artist=song['artist'], durationMillis=song['durationMillis'])
            t.save()

    return song_results


def logoff():
    """
    Log off the music manager
    """
    Interface.music_manager.logout()
    Interface.music_manager.stop()