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
print(ibc1.current_song.play())

time.sleep(2)

ibc1.pop_song()
print(ibc1.current_song.play())

time.sleep(2)

ibc1.pop_song()
print(ibc1.current_song.play())

i = 70
dir = 'up'
while True:
    if i < 70:
        dir = 'up'
    if i > 100:
        dir = 'down'

    if dir == 'up':
        i += 2
    elif dir == 'down':
        i -= 2
    ibc1.current_song.set_volume(str(i))
    time.sleep(.3)