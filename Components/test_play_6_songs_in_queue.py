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
    time.sleep(ibc1.current_song.duration)
