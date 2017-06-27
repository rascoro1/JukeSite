from IBCMusicClient import IBCMusicClient
import errors
import netifaces as ni
from netifaces import AF_INET, AF_INET6, AF_LINK
import requests

class IBCInterface():
    CONFIG_FPATH = "/home/pi/Desktop/JukeSite/ibcconfig"

    def __init__(self):
        self.id = None
        self.interface_name = None
        self.name = None
        self.ip = None
        self.master_ip = None
        self.music_client = None

    def set_id_and_interface(self):
        """
        Each IBC will have its own ID starting from 1 and going up.
        The interface name connected in to the wifi needs to be on the line below the id.
        """
        try:
            f = open(IBCInterface.CONFIG_FPATH, 'r')
        except:
            raise errors.CouldNotOpenIBCConfigFile('Could not open {}'.format(IBCInterface.CONFIG_FPATH), 2002)
        lines = f.readlines()
        f.close()
        id = lines[0].strip()
        interface_name = lines[1].strip()

        self.id = id
        self.interface_name = interface_name

    def start_music_client(self):
        self.music_client = IBCMusicClient()
        self.music_client.start()

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

    def master_scan(self):
        """
        For loop over the network and make a request call to ever webserver.
        The device that gives a response is the master server.

        :return: bool if it could find a master server
        """
        if self.ip is None:
            errors.SetIpAddressError('Set the IBCInterface IP address to a valid ip address.', 2001)

        netmask = ni.ifaddresses(self.interface_name)[AF_INET][0]['netmask']

        if netmask == '255.255.255.0':
            first_part = self.ip.split('.')[0:3]
            first_part = ".".join(first_part)
            for i in range(256):
                new_ip = "{}.{}".format(first_part, i)
                res = requests.get('http://{}/rest/master/info/id'.format(new_ip))
                if res.status_code == 200:
                    # Found the master server
                    res = res.json()
                    return res

        return None

    def get_current_ip(self):
        """
        Get the current ip from the interface

        :return: the current ip as a string || None if not possible
        """
        if self.interface_name is None:
            errors.SetInterfaceError('Set the interface name before performing this method.', 2004)

        return ni.ifaddresses(self.interface_name)[AF_INET][0]['addr']

        # May need to implement some type of subprocess here

    def set_current_ip(self):
        """
        This should work
        """
        self.ip = self.get_current_ip()
