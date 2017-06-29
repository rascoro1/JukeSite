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
    Plays a song from the IBC
    """
    def get(self, song_id):
        """
        Play a song from local storage

        :return: String URL to our website
        """
        ret = {'message': '', 'status': ''}

        try:
            Interface.music_client.play_song(song_id)
            ret['message'] += "Song '{}' is playing.".format(song_id)
            ret['status'] = 'OK'
        except errors.SongIsNotDownloadedError as e:
            ret['status'] = 'ERROR'
            ret['message'] = "The song '{}' has not been downloaded.".format(song_id)

        return ret

class DownloadSong(Resource):
    """
    Download a song from the CBM
    """

    def get(self, cbm_url, song_id):
        ret = {'message': '', 'status': ''}

        try:
            Interface.music_client.download_song(cbm_url, song_id)
            ret['status'] = 'OK'
            ret['message'] = "Song '{}' successfully downloaded. ".format(song_id)
        except errors.SongAlreadyDownloadedException as e:
            ret['status'] = 'OK'
            ret['message'] = "Song '{}' already cached. Did not download.".format(song_id)

        return ret


class StopSong(Resource):
    """
    Stops the song that is currently playing.
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
    Resumes the song that is already being played.
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

class Status(Resource):
    """
    Resumes the song that is already being played.
    """
    def get(self):
        """
        Get Status of ibc song and track id

        :return: String URL to our website
        """
        ret = {'message': '', 'status': ''}
        res = Interface.music_client.get_duration()
        if res is True:
            ret['message'] = {'song_id': Interface.music_client.current_song, 'duration': res}
            ret['status'] = "OK"
        elif res is False:
            ret['message'] = "No song to start playing."
            ret['status'] = 'WARNING'
        return ret

class SetVolume(Resource):
    """
    Sets the volume of the IBC device.
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
api.add_resource(PlaySong, '/PlaySong/<string:song_id>')
api.add_resource(DownloadSong, '/DownloadSong/<string:cbm_url>/<string:song_id>')
api.add_resource(StopSong, '/StopSong')
api.add_resource(ResumeSong, '/ResumeSong')
api.add_resource(SetVolume, '/SetVolume/<string:volume_perc>')
api.add_resource(Status, '/Status')


if __name__ == '__main__':
    # Start Flask
    app.run(host='0.0.0.0', debug=True)
