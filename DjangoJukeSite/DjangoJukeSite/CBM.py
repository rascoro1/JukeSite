from DjangoJukeSite.CBMMusicManager import CBMMusicManager
import DjangoJukeSite.errors as errors
import netifaces as ni
import queue
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
        if self.id is None:
            raise errors.SongNeedsToBeSetError("The song has not been set. Use the set_vars() method.", 8001)

    def is_download(self):
        """
        Will return True/False if the song is already downloaded on the CBM.

        :return: bool if song is downloaded
        """
        self.is_set()
        songs_dir = self.room.interface.music_manager.SONG_DIR
        song_path = "{}/{}.mp3".format(songs_dir, self.id)
        if os.path.isfile(song_path):
            return True
        else:
            return False


class Room():
    def __init__(self):
        self.id = None
        self.mac_addr = None
        self.ip_address = None
        self.hostname = None
        self.queue = []
        self.current_song = None
        self.interface = None

    def add_song(self, song):
        """
        Right now it downloads the song onto the CBM and then it downloads it to the IBC.

        :param song_info:
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
    def __init__(self):
        self.id = None
        self.interface_name = None
        self.name = None
        self.ip = None
        self.master_ip = None
        self.music_manager = None
        self.rooms = []
        self.netmask = None
        self.sync_rooms()
        # self.refresher()

    def refresher(self):
        threading.Timer(5.0, self.refresher).start()
        # Check if queues are synced
        self.sync_queues()
        self.sync_song()

    def sync_rooms(self):
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
        for r in self.rooms:
            songs = get_queue_songs(r.id)

            for song in songs:
                new_song = Song()
                new_song.room = r
                new_song.id = song.storeId
                new_song.duration = song.durationMillis

                if new_song in r.queue:
                    print("Room already contains this song")
                else:
                    print("Room does not contain this song yet. Download the song on the IBC.")
                    r.add_song(new_song)

    def sync_song(self):
        for r in self.rooms:
            if len(r.queue) != 0:
                if r.current_song is not None:
                    first_song = r.queue[0]
                    first_song.play()
                else:
                    print("Status of the current song: {}".format(r.current_song.status()))

    def find_rooms(self, address="192.168.1.0", netmask="24"):
        """
        Will find the rooms using the address and netmask given.
        Will find the IBc devices (Rooms) by performing a nmap scan.
        It will then find any devices IP with the hostname starting with ibc
        Defaults to 192.168.1.0/24 network.
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
                db_room = DBRoom(hostname=r.hostname, ip=r.ip_address, name=r.hostname, queue_id=r.hostname)
                db_room.save()
                print("Room {} added to the database".format(r.hostname))
            else:
                print("Room is already in the database")


    def start_music_client(self):
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
        s = socket.inet_ntoa(fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), 35099, struct.pack('256s', str.encode("en0")))[20:24])
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x891b, struct.pack('256s',iface))[20:24])

    def set_netmask(self):
        self.netmask = self.get_netmask()

    def music_manager_logon(self, username, password):
        self.music_manager.logon(username, password)
        self.refresher()

def get_queue_songs(room_id):
    # Find all the current songs in the  appropriate Queue
    queue_songs = []
    songs = Queue.objects.filter(room_id=room_id)
    for s in songs:
        song_info = Track.objects.get(storeId=s.storeId)
        queue_songs.append(song_info)
    return queue_songs
