from CBM import *
import time

from CBM import *
import time

i = CBMInterface()
i.find_rooms()
i.interface_name = "wlan0"
i.set_current_ip()
i.start_music_client()
i.music_manager.logon("", "")
res = i.music_manager.search_song("sublime")

ibc1 = i.rooms[0]

ibc1.add_song(res[0])

for i in range(5):
    ibc1.pop_song()
    ibc1.current_song.play()
    ibc1.add_song(res[i+1])
    while True:
        ibc_info = ibc1.current_song.status()
        ibc_duration = ibc_info['message']['duration']
        ibc_song_id = ibc_info['message']['song_id']

        if ibc_duration > ibc1.current_song.duration - 1:
            break
        time.sleep(1)
