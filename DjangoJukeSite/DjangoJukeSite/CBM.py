from DjangoJukeSite.CBMMusicManager import CBMMusicManager
import DjangoJukeSite.errors as errors
import netifaces as ni
from netifaces import AF_INET
import requests
from subprocess import check_output
import json
import os
import socket
import fcntl
import struct
import iface
import threading
from JukeSite.models import Track, Queue
from JukeSite.models import Room as DBRoom
"""
TODO:
    [X] Fix queue not getting synced correctly
    [X] When user adds a new song, elimate the delay.
        [X] Have the room object remember  which songs it downloaded
    [X] Add skip button of current cong for admin
    [] clean up the cache page
    [] add voting on songs in queue
    [X] when user searches song have previous search available with confirm message
        [] Have it automatically go to search when searching.
    [] Add icons on search songs results indicating if song is cached on master and if it is on the slave
    [] Play random songs from cache like pandora feature. (It would be cool if it grabbed popular songs)

"""

class Song():
    """
    This is an object that represents one song.
    We will be making restful API calls to our IBC's from
    """
    CBM_WEBSITE = "http://{}:5000"
    DOWNLOAD = CBM_WEBSITE + "/DownloadSong/{}/{}" # from [cbm] download [song_id]
    PLAY = CBM_WEBSITE + "/PlaySong/{}" # Play [song_id]
    STOP = CBM_WEBSITE + "/StopSong" # Stop song currently playing
    RESUME = CBM_WEBSITE + "/ResumeSong" # Resume current running song
    SET_VOLUME = CBM_WEBSITE + "/SetVolume/{}" # Set volume int([0-100])
    STATUS = CBM_WEBSITE + "/Status" # Status of current song and track id

    def __init__(self):
        self.id = None
        self.duration = None
        self.room = None

    def set_vars(self, gmusic_song):
        """
        All the information storing in the Song object being init.

        :param gmusic_song: [dictionary] gmusic_song search results
        """
        self.id = gmusic_song['track']['storeId']
        self.duration = int(gmusic_song['track']['durationMillis']) * .001

    def play(self):
        """
        Play song in room associated with this song

        :param song_id: [string] the storeID. Starts with a T
        :return:
        """
        self.is_set()
        res = requests.get(Song.PLAY.format(self.room.ip_address, self.id))
        return res.json()

    def download(self):
        """
        Download song to the IBC from the CBM

        :param cbm_url: [string] the url of the cbm (Master) to download song from
        :param song_id: [string] the song id to download
        :return:
        """
        self.is_set()
        # Check out to see if song is on the CBM
        if self.is_download() is False:
            # If it is not download the song with the music manager
            self.room.interface.music_manager.download_song(self.id)

        # Download the song to the IBC from the CBM
        res = requests.get(Song.DOWNLOAD.format(self.room.ip_address, self.room.interface.ip, self.id))
        return res.json()

    def stop(self):
        """
        Stop the current song on the IBC

        :return:
        """
        res = requests.get(Song.STOP.format(self.room.ip_address))
        return res.json()

    def resume(self):
        """
        Resume the current song on the IBC

        :return:
        """
        res = requests.get(Song.RESUME.format(self.room.ip_address))
        return res.json()

    def set_volume(self, volume_perc):
        """
        Set the volume of Rasbian on the IBC

        :param volume_perc: [int]
        :return:
        """
        res = requests.get(Song.SET_VOLUME.format(self.room.ip_address, volume_perc))
        return res.json()

    def status(self):
        """
        Get the status of the machine.
        Song duration and current track_id being played.

        :return:
        """

        res = requests.get(Song.STATUS.format(self.room.ip_address))
        return res.text

    def is_set(self):
        """
        The song has not been set
        :return:
        """
        if self.id is None:
            raise errors.SongNeedsToBeSetError("The song has not been set. Use the set_vars() method.", 8001)

    def is_download(self):
        """
        Will return True/False if the song is already downloaded on the CBM.

        :return: bool if song is downloaded
        """
        self.is_set()
        songs_dir = CBMMusicManager.SONG_DIR
        song_path = "{}/{}.mp3".format(songs_dir, self.id)
        if os.path.isfile(song_path):
            return True
        else:
            return False


class Room():
    """
    This represents one of hte IBCs/Slaves
    """
    def __init__(self):
        self.id = None
        self.mac_addr = None
        self.ip_address = None
        self.hostname = None
        self.queue = []
        self.current_song = None
        self.interface = None
        self.downloaded_songs = []

    def sync_queue(self):
        """
        Sync the DB queue to the room object queue

        :return:
        """
        self.queue = []
        songs = get_queue_songs(self.id)
        for song in songs:
            new_song = create_song_object(self, song)
            self.queue.append(new_song)


    def add_song(self, song):
        """
        Right now it downloads the song onto the CBM and then it downloads it to the IBC.

        :param song: Song() class
        :return:
        """

        # song.set_vars(song_info)

        if song not in self.queue:
            song.download()
            self.queue.append(song)

    def pop_song(self):
        """
        Take the next song in queue

        :return: the next song in queue
        """
        self.current_song = self.queue.get()
        return self.current_song


class CBMInterface():
    """
    This class will be the class that is loaded and is a global in the views.py
    It will have full functionality over the master and all of the slaves.
    This is pretty much the engine behind all of the other classes.
    """
    def __init__(self):
        self.id = None
        self.interface_name = "eth0"
        self.name = None
        self.ip = None
        self.master_ip = None
        self.music_manager = None
        self.rooms = []
        self.netmask = None
        self.set_current_ip()
        self.find_rooms()
        self.sync_rooms()
        self.sync_queues()
        # self.refresher()

    def refresher(self):
        """
        A thread running every 5 seconds to sync songs
        :return:
        """
        threading.Timer(5.0, self.refresher).start()
        # Check if queues are synced
        self.sync_song()
        self.sync_queues()

    def sync_rooms(self):
        """
        Sync the rooms from the db to the Room classes.
        :return:
        """
        db_rooms = DBRoom.objects.all()
        for db_r in db_rooms:
            print("Sycing: {}".format(db_r))
            r = Room()
            r.hostname = db_r.hostname
            r.ip_address = db_r.ip
            r.interface = self
            r.id = db_r.id
            self.rooms.append(r)

    def sync_queues(self):
        """
        Sync the queries for all of the rooms.
        This is run on application startup.

        :return:
        """
        for r in self.rooms:
            songs = get_queue_songs(r.id)
            for song in songs:
                song_obj = create_song_object(r, song)
                if self.music_manager is not None:
                    if not self.music_manager.is_downloaded(song_obj.id):
                        # Download song to master
                        res = self.music_manager.download_song(song_obj.id)
                        print("Downlaoded on master: {}".format(res))

                    if song_obj.id not in r.downloaded_songs:
                        # Download song to slave
                        res = song_obj.download()
                        message = res['message']
                        if "already cached" in message:
                            print("Song downloaded already")
                            r.downloaded_songs.append(song_obj.id)
                        else:
                            print("Download to the slave: {}".format(res))

    def sync_song(self):
        """
        Sync the song on the slave to the appropriate song in the queue.
        A api call is sent to the Slave and in the response the status of the song is returned.
        If the duartion of the song is '-1' then the song has stopped playing and start playing the next song
        """
        for r in self.rooms:
            r.sync_queue()
            if len(r.queue) != 0:
                if r.current_song is None:
                    first_song = r.queue[0]
                    first_song.play()
                    r.current_song = first_song
                elif len(r.queue) == 1:
                    res = r.current_song.status()
                    res = json.loads(res)
                    cur_dur = int(res['message']['duration'])
                    cur_song_id = res['message']['song_id']

                    if cur_dur == -1:
                        try:
                            current_song = r.queue[0]
                            if cur_song_id != current_song.id:
                                # Start playing the song but do not remove it from the queue
                                current_song.play()
                                r.current_song = current_song
                            else:
                                # Song is old and needs to be removed
                                Queue.objects.get(room_id=r.id).delete()
                        except IndexError:
                            print("ERRORRRRRRRRRRRRRRRR")

                else:
                    res = r.current_song.status()
                    res = json.loads(res)
                    print("Status of the current song: {}".format(res))
                    print("THe current song duration: {}".format(r.current_song.duration))
                    total_dur = int(r.current_song.duration)
                    
                    cur_dur = int(res['message']['duration'])

                    if cur_dur == -1:
                        # Switch to the next song because the song is over
                        self.next_song(r)

    def next_song(self, room):
        """
        Play the next song in the queue for this specific room.

        :param room: Room() object
        :return:
        """
        # Switch to the next song becausr the song is almost over
        print("Switching to the next song!!!!!! --->>>>>>>")
        db_songs = Queue.objects.filter(room_id=room.id)
        try:
            db_songs[0].delete()
            next_song = room.queue[1]
            print("This is the next song: {}".format(next_song.id))
            next_song.play()
            room.current_song = next_song
            del room.queue[0]
        except IndexError:
            print("There is no songs in the queue.")
        except UnboundLocalError:
            print("There is no next song to play.")

    def find_rooms(self, address="192.168.1.0", netmask="24"):
        """
        Will find the rooms using the address and netmask given.
        Will find the IBc devices (Rooms) by performing a nmap scan.
        It will then find any devices IP with the hostname starting with ibc
        Defaults to 192.168.1.0/24 network.

        After doing this the rooms will be added to the Django Database.

        :param address: The network the device is on
        :param netmask: The netmask of this network
        """
        command = "nmap -sn {}/{}".format(address, netmask).split(' ')
        res = check_output(command)
        lines = res.decode().split('\n')
        ibcs = [line.split('for ', 1)[1] for line in lines if 'ibc' in line]
        for ibc in ibcs:
            print("AN IBC WAS FOUND!")
            hostname, ip = ibc.split(' (',1)
            ip = ip.rstrip(')').strip()

            # Now we add the rooms to the database
            res = DBRoom.objects.filter(hostname=hostname)
            if len(res) == 0:
                print("Room is not in the database")
                # This room is not in the database yet.
                # Add the roome to the database
                db_room = DBRoom(hostname=hostname, ip=ip, name=hostname, queue_id=hostname)
                db_room.save()
                print("Room {} added to the database".format(hostname))
            else:
                print("Room is already in the database")

    def start_music_client(self):
        """
        Start the music client
        """
        self.music_manager = CBMMusicManager()
        self.music_manager.start()

    def get_current_ip(self):
        """
        Get the current ip from the interface

        :return: the current ip as a string || None if not possible
        """
        if self.interface_name is None:
            errors.SetInterfaceError("Set the 'interface_name' before performing this method.", 2004)

        return ni.ifaddresses(self.interface_name)[AF_INET][0]['addr']

    def set_current_ip(self):
        """
        This should work
        """
        self.ip = self.get_current_ip()

    def get_netmask(self):
        """
        Get netmask of device running methos.
        """
        s = socket.inet_ntoa(fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), 35099, struct.pack('256s', str.encode("en0")))[20:24])
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x891b, struct.pack('256s',iface))[20:24])

    def set_netmask(self):
        """
        Sets the netmask
        """
        self.netmask = self.get_netmask()

    def music_manager_logon(self, username, password):
        """
        Logon to the music mangaer
        """
        self.music_manager.logon(username, password)
        self.refresher()

    def find_room(self, room_id):
        print("Room ID: {}".format(room_id))
        for r in self.rooms:
            print("Aval room: {}".format(r.id))
            if str(r.id) == str(room_id):
                return r
        return None

def create_song_object(room, song):
    new_song = Song()
    new_song.room = room
    new_song.id = song.storeId
    new_song.duration = song.durationMillis
    return new_song

def get_queue_songs(room_id):
    """
    Find all of the songs in the queue associated with this room.

    :param room_id: [int] unique room id
    :return: list of songs from database
    """
    queue_songs = []
    songs = Queue.objects.filter(room_id=room_id)
    for s in songs:
        song_info = Track.objects.get(storeId=s.storeId)
        queue_songs.append(song_info)
    return queue_songs
