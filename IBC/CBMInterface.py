from CBMMusicManager import CBMMusicManager
import errors
import netifaces as ni
import queue
from netifaces import AF_INET, AF_INET6, AF_LINK
import requests
from subprocess import check_output

class Song():
    """
    This is an object that repersents one song.
    """
    def __init__(self):
        self.id = None
        self.artist = None
        self.album = None
        self.title = None
        self.duration = None
        self.image = None

    def set_vars(self, gmusic_song):
        self.id = gmusic_song['track']['storeId']
        self.artist = gmusic_song['track']['artist']
        self.album = gmusic_song['track']['album']
        self.title = gmusic_song['track']['title']
        self.duration = gmusic_song['track']['durationMillis']
        self.image = gmusic_song['track']['albumArtRef'][0]['url']



class Rooms():
    def __init__(self):
        self.mac_addr = None
        self.ip_address = None
        self.hostname = None
        self.queue = queue.Queue()
        # get put

    def add_song(self, song_info):
        song = Song()
        song.set_vars(song_info)
        self.queue.put(song)

    def pop_song(self):
        return self.queue.get()


class CBMInterface():
    CONFIG_FPATH = "/home/pi/Desktop/JukeSite/ibcconfig"

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

            r = Rooms()
            r.hostname = hostname
            r.ip_address = ip

            self.rooms.append(r)

    def set_id_and_interface(self):
        """
        INSTEAD: I think we should give hostnames staerting with ibc indicating that they are IBC.

        Each IBC will have its own ID starting from 1 and going up.
        The interface name connected in to the wifi needs to be on the line below the id.
        """
        try:
            f = open(CBMInterface.CONFIG_FPATH, 'r')
        except:
            raise errors.CouldNotOpenIBCConfigFile('Could not open {}'.format(CBMInterface.CONFIG_FPATH), 2002)
        lines = f.readlines()
        f.close()
        id = lines[0].strip()
        interface_name = lines[1].strip()

        self.id = id
        self.interface_name = interface_name

    def start_music_client(self):
        self.music_manager = CBMMusicManager()
        self.music_manager.start()

    def set_name(self):
        """
        Set the name appropriately.
        The Name is given from master

        :return: bool if master was found
        """

        res = self.master_scan()
        if res is None:
            return False
        else:
            self.name = res['data']['name']
            return True

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
