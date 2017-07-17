import errors
from subprocess import check_output
import os
import pygame


class IBCMusicClient():
    # Please have this be an absolute path
    SONG_DIR = "/home/pi/Desktop/songs"

    def __init__(self):
        self.api = None
        self.player = None
        self.current_song = None
        self.current_song_pid = None

    def download_song(self, cbm_url, song_id):
        """
        Download the song from the storeId.

        :param song_id: the 'storeId' of the specific song
        """
        # create the song directory on the IBC device if it doesnt exits
        if not os.path.isdir(IBCMusicClient.SONG_DIR):
            os.mkdir(IBCMusicClient.SONG_DIR)

        url = "http://{}/songs/{}.mp3".format(cbm_url, song_id)
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

    def stop_song(self):
        if self.player is None:
            return False
        else:
            self.player.music.pause()
            return True

    def resume_song(self):
        if self.player is None:
            return False
        else:
            self.player.music.unpause()
            return True

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
            self.current_song = song_id
            """
            if self.player is None:
                self.player = pygame.mixer
                self.player.init()
                self.player.music.load(song_file_path)
                self.player.music.set_volume(1)
                self.player.music.play()
            else:
                # Player has already been init meaning that a song may be playing
                # We will have to stop the current song and then play the newly requested song
                self.player.music.pause()
                self.player.music.load(song_file_path)
                self.player.music.play()
             """
            # command = "mpg123 -q {} & echo".format(song_file_path).split(' ')
            os.system("mpg123 -q {} & echo".format(song_file_path))
            res = check_output(command)
            
            return True
        else:
            raise errors.SongIsNotDownloadedError("the song '{}' has not been downloaded. download_song() must be performed before this method", 8005)

    def set_volume(self, volume_perc):

        volume_perc = int(volume_perc)
            
        if volume_perc > 100 or volume_perc < 0:
            raise errors.InvalidVolumePercentageError("Volume perc must be between 0-100", 8005)

        # Getting the mixer control name associated with the AUX
        command = "amixer scontrols".split(' ')
        res = check_output(command)
        res = res.decode()
        
        mixer_control_name = res.split("'")[1].split("'")[0]

        # Changing the colume on that specific mixer controller        
        command = "amixer sset '{}' {}%".format(mixer_control_name, volume_perc).split(' ')
        res = check_output(command)
        res = res.decode()

        # There was an error
        if res.startswith('amixer: '):
            raise errors.FailedToSetVolumeError('Failed to set volume. bash error "{}"'.format(res), 8021)

        return True
        
    def get_duration(self):
        if self.player is None:
            return None
        else:
            return self.player.music.get_pos()



        
