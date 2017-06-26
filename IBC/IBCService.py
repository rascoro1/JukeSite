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
        Interface.music_client.stop()

        return ret



# API resource routing
api.add_resource(PlaySong, '/PlaySong/<string:username>/<string:password>/<string:song_id>')

if __name__ == '__main__':
    # Start Flask
    app.run(debug=True)