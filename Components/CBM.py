from CBMMusicManager import CBMMusicManager
import errors
import netifaces as ni
import queue
from netifaces import AF_INET, AF_INET6, AF_LINK
import requests
from subprocess import check_output
import json
import os

class Song():
    """
    This is an object that represents one song.
    We will be making restful API calls to our IBC's from
    """
    CBM_WEBSITE="http://{}:5000"
    DOWNLOAD = CBM_WEBSITE + "/DownloadSong/{}/{}" # from [cbm] download [song_id]
    PLAY = CBM_WEBSITE + "/PlaySong/{}" # Play [song_id]
    STOP = CBM_WEBSITE + "/StopSong" # Stop song currently playing
    RESUME = CBM_WEBSITE + "/ResumeSong" # Resume current running song
    SET_VOLUME = CBM_WEBSITE + "/SetVolume/{}" # Set volume int([0-100])
    STATUS = CBM_WEBSITE + "/Status" # Status of current song and track id

    def __init__(self):
        self.id = None
        self.artist = None
        self.album = None
        self.title = None
        self.duration = None
        self.image = None
        self.room = None

    def set_vars(self, gmusic_song):
        """
        All the information storing in the Song object being init.

        :param gmusic_song: [dictionary] gmusic_song search results
        """
        self.id = gmusic_song['track']['storeId']
        self.artist = gmusic_song['track']['artist']
        self.album = gmusic_song['track']['album']
        self.title = gmusic_song['track']['title']
        self.duration = gmusic_song['track']['durationMillis']
        self.image = gmusic_song['track']['albumArtRef'][0]['url']

    def play(self):
        """
        Play song in room associated with this song

        :param song_id: [string] the storeID. Starts with a T
        :return:
        """
        self.is_set()
        res = requests.get(Song.PLAY.format(self.room.ip_address, self.id))
        return json.load(res.json())

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
            self.room.interface.music_manager.download_song_id(self.id)

        # Download the song to the IBC from the CBM
        res = requests.get(Song.DOWNLOAD.format(self.room.ip_address, self.room.interface.ip, self.id))
        return json.load(res.json())

    def stop(self):
        """
        Stop the current song on the IBC

        :return:
        """
        res = requests.get(Song.STOP.format(self.room.ip_address))
        return json.load(res.json())

    def resume(self):
        """
        Resume the current song on the IBC

        :return:
        """
        res = requests.get(Song.RESUME.format(self.room.ip_address))
        return json.load(res.json())

    def set_volume(self, volume_perc):
        """
        Set the volume of Rasbian on the IBC

        :param volume_perc: [int]
        :return:
        """
        res = requests.get(Song.SET_VOLUME.format(self.room.ip_address, volume_perc))
        return json.load(res.json())

    def status(self):
        """
        Get the status of the machine.
        Song duration and current track_id being played.

        :return:
        """

        res = requests.get(Song.STATUS.format(self.room.ip_address))
        return json.load(res.json())

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
        self.mac_addr = None
        self.ip_address = None
        self.hostname = None
        self.queue = queue.Queue()
        self.current_song = None
        self.interface = None

    def add_song(self, song_info):
        song = Song()
        song.room = self
        song.set_vars(song_info)
        self.queue.put(song)

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

    def find_rooms(self):
        command = "nmap -sn 192.168.1.0/24".split(' ')
        res = check_output(command)
        res = res.decode()
        lines = res.split('\n')

        ibcs = [line.split('for ', 1)[1] for line in lines if 'ibc' in line]
        for ibc in ibcs:
            hostname, ip = ibc.split(' (',1)
            ip = ip.rstrip(')').strip()

            r = Room()
            r.hostname = hostname
            r.ip_address = ip
            r.interface = self

            self.rooms.append(r)

    def start_music_client(self):
        self.music_manager = CBMMusicManager()
        self.music_manager.start()

    def get_current_ip(self):
        """
        Get the current ip from the interface

        :return: the current ip as a string || None if not possible
        """
        if self.interface_name is None:
            errors.SetInterfaceError('Set the interface name before performing this method.', 2004)

        return ni.ifaddresses(self.interface_name)[AF_INET][0]['addr']

    def set_current_ip(self):
        """
        This should work
        """
        self.ip = self.get_current_ip()
