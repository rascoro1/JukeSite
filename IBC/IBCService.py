from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from IBCInterface import IBCInterface
import errors
"""
Created by: Andrew Copeland
"""
Interface = IBCInterface()
Interface.start_music_client()

# Setup the URL paramter
parser = reqparse.RequestParser()
parser.add_argument('url')


# Start Flask and the REST API
app = Flask(__name__)
api = Api(app)

class PlaySong(Resource):
    """
    Returns new URL of all the scraped pages of the url given.
    """
    def get(self, username, password, song_id):
        """
        Get the url for the desired website scraped pages

        :return: String URL to our website
        """
        ret = {'message': '', 'status': ''}

        res = Interface.music_client.logon(username, password)


        if res is False:
            raise errors.CouldNotLoginError('Could not login using username: {} and password: {}'.format(username, password), 8001)

        try:
            Interface.music_client.download_song(song_id)
            ret['status'] = 'OK'
            ret['message'] = "Song '{}' successfully downloaded. ".format(song_id)
        except errors.CouldNotLoginError as e:
            ret['status'] = 'ERROR'
            ret['message'] = 'Could not login to google with account {}'.format(username)

        except errors.SongAlreadyDownloadedException as e:
            ret['status'] = 'OK'
            ret['message'] = "Song '{}' already cached. Did not download.".format(song_id)
        except errors.CannotDownloadSongError as e:
            ret['status'] = 'ERROR'
            ret['message'] = "Could not download song '{}' from google.".format(song_id)

        try:
            Interface.music_client.play_song(song_id)
            ret['message'] += "Song '{}' is playing.".format(song_id)


        except errors.SongIsNotDownloadedError as e:
            ret['status'] = 'ERROR'
            ret['message'] = "The song '{}' has not been downloaded.".format(song_id)

        Interface.music_client.logout()

        return ret

class StopSong(Resource):
    """
    Returns new URL of all the scraped pages of the url given.
    """
    def get(self):
        """
        Get the url for the desired website scraped pages

        :return: String URL to our website
        """
        ret = {'message': '', 'status': ''}
        res = Interface.music_client.stop_song()
        if res is True:
            ret['message'] = "Song stopped successfully"
            ret['status'] = "OK"
        elif res is False:
            ret['message'] = "No song to stop playing."
            ret['status'] = 'WARNING'
        return ret

class ResumeSong(Resource):
    """
    Returns new URL of all the scraped pages of the url given.
    """
    def get(self):
        """
        Get the url for the desired website scraped pages

        :return: String URL to our website
        """
        ret = {'message': '', 'status': ''}
        res = Interface.music_client.resume_song()
        if res is True:
            ret['message'] = "Song resumed successfully"
            ret['status'] = "OK"
        elif res is False:
            ret['message'] = "No song to start playing."
            ret['status'] = 'WARNING'
        return ret

class SetVolume(Resource):
    """
    Returns new URL of all the scraped pages of the url given.
    """
    def get(self, volume_perc):
        """
        Get the url for the desired website scraped pages

        :return: String URL to our website
        """
        ret = {'message': '', 'status': ''}

        try:
            Interface.music_client.set_volume(volume_perc)
            ret['status'] = "OK"
            ret['message'] = "Volume changed successfully"
        except ValueError:
            ret['status'] = 'ERROR'
            ret['message'] = '{} is not an integer. Use a integer.'.format(volume_perc)
        except errors.InvalidVolumePercentageError as e:
            ret['status'] = 'ERROR'
            ret['message'] = "'{}' is an invalid volume percentage (0-100).".format(volume_perc)
        except errors.FailedToSetVolumeError as e:
            ret['status'] = 'ERROR'
            ret['message'] = "Could not set Volume. Bash error code: {}".format(e.message)

        
        return ret


    
# API resource routing
api.add_resource(PlaySong, '/PlaySong/<string:username>/<string:password>/<string:song_id>')
api.add_resource(StopSong, '/StopSong')
api.add_resource(ResumeSong, '/ResumeSong')
api.add_resource(SetVolume, '/SetVolume/<string:volume_perc>')

if __name__ == '__main__':
    # Start Flask
    app.run(host='0.0.0.0', debug=True)
