from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import loader
from JukeSite.models import Track, Room, Queue
from DjangoJukeSite.CBM import CBMInterface

Interface = CBMInterface()
Interface.interface_name = 'etho0'
Interface.set_current_ip()
Interface.start_music_client()
Interface.music_manager.start()
Interface.music_manager.logon('andcope1995@gmail.com', 'Basketball12@1995')

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
    current_room = None
    queue_songs = []
    tracks = Track.objects.all()
    rooms = Room.objects.all()
    queues = Queue.objects.all()

    # Find the current room
    for r in rooms:
        if str(r.id) == str(room_id):
            current_room = r

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
    current_room = None
    queue_songs = []
    rooms = Room.objects.all()
    template = loader.get_template('dashboard.html')
    song_query = None
    song_results = None

    # Get the search query string
    if request.method == 'GET':
        song_query = request.GET.get('search_box', None)

    current_room = get_current_room(room_id)
    queue_songs = get_queue_songs(room_id)
    song_results = get_song_query_results(song_query)

    print(queue_songs)
    context = {
       'rooms': rooms,
       'current_room': current_room,
       'song_results': song_results,
       'queue': queue_songs
    }
    return HttpResponse(template.render(context, request))

def add_song(request, room_id, song_id):

    current_room = None
    add_results = None
    queue_songs = []
    tracks = Track.objects.all()
    rooms = Room.objects.all()
    queues = Queue.objects.all()
    template = loader.get_template('dashboard.html')


    current_room = get_current_room(room_id)
    queue_songs = get_queue_songs(room_id)
    song_in_queue = is_song_in_queue(song_id, queue_songs)

    if song_in_queue:
        add_results = "ERROR: Song already in the Queue"
    else:
        q = Queue(storeId=song_id, room_id=room_id, position=1)
        q.save()
        add_results = "Song added to the queue."
        queue_songs = get_queue_songs(room_id)

    context = {
       'tracks': tracks,
       'rooms': rooms,
       'current_room': current_room,
       'add_results': add_results,
       'queue': queue_songs
    }
    return HttpResponse(template.render(context, request))


def get_queue_songs(room_id):
    # Find all the current songs in the  appropriate Queue
    queue_songs = []
    songs = Queue.objects.filter(room_id=room_id)
    for s in songs:
        song_info = Track.objects.get(storeId=s.storeId)
        queue_songs.append(song_info)
    return queue_songs


def get_current_room(room_id):
    room = Room.objects.get(id=room_id)
    return room


def is_song_in_queue(song_id, queue_songs):
    for song in queue_songs:
        if song_id == song.storeId:
            return True
    return False


def get_song_query_results(song_query):
    # Find the search results
    song_results = None
    if song_query is not None:
        song_results = Interface.music_manager.search_song(str(song_query))
        # Add the results to our database
        for song in song_results:
            song = song['track']
            t = Track(storeId=song['storeId'], title=song['title'], album=song['album'], artist=song['artist'])
            t.save()

    return song_results

def logoff():
    Interface.music_manager.logout()
    Interface.music_manager.stop()
