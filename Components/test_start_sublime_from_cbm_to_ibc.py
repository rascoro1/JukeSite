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
ibc1.add_song(res[1])
ibc1.add_song(res[2])

ibc1.pop_song()
print(ibc1.current_song.download())
print(ibc1.current_song.play())

while True:
    print(ibc1.current_song.status())
    time.sleep(2)
