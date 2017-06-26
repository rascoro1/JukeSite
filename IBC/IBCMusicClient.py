from gmusicapi import Mobileclient
import errors
from subprocess import check_output
import os
from gmusicapi.exceptions import AlreadyLoggedIn
import pyglet

class IBCMusicClient():
    # Please have this be an absolute path
    SONG_DIR = "/Users/copelanda1/Desktop"

    def __init__(self):
        self.api = None
        self.player = None

    def start(self):
        """
        Starts the MobileClient
        """
        self.api = Mobileclient()

    def stop(self):
        """
        Deletes MobileClient and sets self.api to default(None)
        """
        del self.api
        self.api = None

    def logon(self, email, password):
        """
        Logs onto google music as a mobile client. Returns true is sucessful.

        :param email: Email of the Google user
        :param password: Pass of the google user
        :return: Bool if connection was successful
        """
        if self.api is None:
            raise errors.MobileClientNotInitError("The Client has not been init therefor it cannot logon.", 1000)

        try:
            res = self.api.login(email, password, self.api.FROM_MAC_ADDRESS)
        except AlreadyLoggedIn as e:
            self.api.logout()
            res = self.api.login(email, password, self.api.FROM_MAC_ADDRESS)

        del email
        del password
        return res

    def logout(self):
        """
        logs out of google music mobile client.

        :return: if it was succesful
        """
        return self.api.logout()

    def is_authenticated(self):
        if not self.api.is_authenticated():
            raise errors.SessionNotActive("The session is no longer active. Either it timedout or you have not logged in", 1001)

    def search_song(self, query):
        """
        Searchs for the given query and return the song results
        Will check for authentication.

        [{
            'track': {
                'album': 'Work Out',
                'albumArtRef': [{
                    'aspectRatio': '1',
                    'autogen': False,
                    'kind': 'sj#imageRef',
                    'url': 'http://lh5.ggpht.com/DVIg4GiD6msHfgPs_Vu_2eRxCyAoz0fFdxj5w...'
                }],
                'albumArtist': 'J.Cole',
                'albumAvailableForPurchase': True,
                'albumId': 'Bfp2tuhynyqppnp6zennhmf6w3y',
                'artist': 'J Cole',
                'artistId': ['Ajgnxme45wcqqv44vykrleifpji', 'Ampniqsqcwxk7btbgh5ycujij5i'],
                'composer': '',
                'discNumber': 1,
                'durationMillis': '234000',
                'estimatedSize': '9368582',
                'explicitType': '1',
                'genre': 'Pop',
                'kind': 'sj#track',
                'nid': 'Tq3nsmzeumhilpegkimjcnbr6aq',
                'primaryVideo': {
                    'id': '6PN78PS_QsM',
                    'kind': 'sj#video',
                    'thumbnails': [{
                        'height': 180,
                        'url': 'https://i.ytimg.com/vi/6PN78PS_QsM/mqdefault.jpg',
                        'width': 320
                    }]
                },
                'storeId': 'Tq3nsmzeumhilpegkimjcnbr6aq',
                'title': 'Work Out',
                'trackAvailableForPurchase': True,
                'trackAvailableForSubscription': True,
                'trackNumber': 1,
                'trackType': '7',
                'year': 2011
            },
            'type': '1'
        }]
        :param query: The song query
        :return: [list] all the song hits
        """
        self.is_authenticated()
        res = self.api.search(query)
        songs = res['song_hits']
        return songs

    def search_album(self, query):
        """
        Searchs for the given query and returns the album results.
        Will check for authenitcation.

        e.g return:
        [{
            'album': {
                'albumArtRef': 'http://lh5.ggpht.com/DVIg4GiD6msHfgPs_Vu_2eRxCyAoz0fF...',
                'albumArtist': 'J.Cole',
                'albumId': 'Bfp2tuhynyqppnp6zennhmf6w3y',
                'artist': 'J.Cole',
                'artistId': ['Ajgnxme45wcqqv44vykrleifpji'],
                'description_attribution': {
                    'kind': 'sj#attribution',
                    'license_title': 'Creative Commons Attribution CC-BY',
                    'license_url': 'http://creativecommons.org/licenses/by/4.0/legalcode',
                    'source_title': 'Freebase',
                    'source_url': ''
                },
                'explicitType': '1',
                'kind': 'sj#album',
                'name': 'Work Out',
                'year': 2011
            },
            'type': '3'
        }]

        :param query: [string] The album query
        :return: [list] A list of all the album hits
        """
        self.is_authenticated()
        res = self.api.search(query)
        albums = res['album_hits']
        return albums

    def get_album_info(self, album_id):
        """
        Returns information about an album

        e.g return:
        {
            'kind': 'sj#album',
            'name': 'Circle',
            'artist': 'Amorphis',
            'albumArtRef': 'http://lh6.ggpht.com/...',
            'tracks': [  # if `include_tracks` is True
            {
                'album': 'Circle',
                'kind': 'sj#track',
                'storeId': 'T5zb7luo2vkroozmj57g2nljdsy',  # can be used as a song id
                'artist': 'Amorphis',
                'albumArtRef': [
                {
                    'url': 'http://lh6.ggpht.com/...'
                }],
                'title': 'Shades of Grey',
                'nid': 'T5zb7luo2vkroozmj57g2nljdsy',
                'estimatedSize': '13115591',
                'albumId': 'Bfr2onjv7g7tm4rzosewnnwxxyy',
                'artistId': ['Apoecs6off3y6k4h5nvqqos4b5e'],
                'albumArtist': 'Amorphis',
                'durationMillis': '327000',
                'composer': '',
                'genre': 'Metal',
                'trackNumber': 1,
                'discNumber': 1,
                'trackAvailableForPurchase': True,
                'trackType': '7',
                'albumAvailableForPurchase': True
            }, # ...
            ],
            'albumId': 'Bfr2onjv7g7tm4rzosewnnwxxyy',
            'artistId': ['Apoecs6off3y6k4h5nvqqos4b5e'],
            'albumArtist': 'Amorphis',
            'year': 2013
        }

        :param album_id: The albumId
        :return: Dictionary in the format above
        """
        self.is_authenticated()
        return self.api.get_album_info(album_id)

    def get_song_info(self, song_id):
        """
        Returns information about a song

        e.g return
        {
            'album': 'Best Of',
            'kind': 'sj#track',
            'storeId': 'Te2qokfjmhqxw4bnkswbfphzs4m',
            'artist': 'Amorphis',
            'albumArtRef': [
            {
                'url': 'http://lh5.ggpht.com/...'
            }],
            'title': 'Hopeless Days',
            'nid': 'Te2qokfjmhqxw4bnkswbfphzs4m',
            'estimatedSize': '12325643',
            'albumId': 'Bsbjjc24a5xutbutvbvg3h4y2k4',
            'artistId': ['Apoecs6off3y6k4h5nvqqos4b5e'],
            'albumArtist': 'Amorphis',
            'durationMillis': '308000',
            'composer': '',
            'genre': 'Metal',
            'trackNumber': 2,
            'discNumber': 1,
            'trackAvailableForPurchase': True,
            'trackType': '7',
            'albumAvailableForPurchase': True
        }

        :param song_id: The songds storeId
        :return: A dict with the above information
        """
        self.is_authenticated()
        return self.api.get_track_info(song_id)

    def get_song_url(self, song_id):
        self.is_authenticated()
        res = self.api.get_stream_url(song_id)
        return res

    def download_song(self, song_id):
        """
        Download the song from the storeId.

        :param song_id: the 'storeId' of the specific song
        """
        url = self.get_song_url(song_id)
        song_file_path = "{}/{}.mp3".format(IBCMusicClient.SONG_DIR, song_id)
        if os.path.isfile(song_file_path):
            raise errors.SongAlreadyDownloadedException("The song '{}' has already been downloaded and cached".format(song_file_path), 8002)
        # This need to not use subprocessing
        command = ['wget', url, '-O', song_file_path]
        res = check_output(command)
        lines = res.decode().split('\n')
        error_lines = [line for line in lines if 'failed' in line]

        if len(error_lines) > 0:
            # We have an error
            raise errors.CannotDownloadSongError("Could not download the given song. {}".format(str(error_lines)), 1003)

    def play_song(self, song_id):
        """
        Plays the specific song

        :param song_id: the storeId
        """
        """
        LETS TRY THIS WAY FIRST OF PI

        song_file_path = "{}/{}.mp3".format(IBCMusicClient.SONG_DIR, song_id)
        print(song_file_path)
        mixer.init()
        mixer.music.load(song_file_path)
        mixer.music.play()
        """
        song_file_path = "{}/{}.mp3".format(IBCMusicClient.SONG_DIR, song_id)
        if os.path.isfile(song_file_path):
            # res = os.system('mpg123 {}'.format(song_file_path))
            # command = ['mpg123', song_file_path]
            # res = check_output(command)
            if self.player is None:
                self.player = pyglet.media.Player()
                song = pyglet.media.load(song_file_path)
                self.player.queue(song)
                self.player.play()
            else:
                self.player.pause()
                self.player.delete()
                self.player = pyglet.media.Player()
                song = pyglet.media.load(song_file_path)
                self.player.queue(song)
                self.player.play()
            return True
        else:
            raise errors.SongIsNotDownloadedError("the song '{}' has not been downloaded. download_song() must be performed before this method", 8005)

