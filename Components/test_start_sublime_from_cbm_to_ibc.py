from CBM import *

i = CBMInterface()
i.find_rooms()
i.start_music_client()
i.music_client.logon("", "")
res = i.music_client.search_song("sublime")

ibc1 = i.rooms[0]
ibc1.add_song(res[0])
ibc1.add_song(res[1])
ibc1.add_song(res[2])

ibc1.pop_song()
ibc1.current_song.download()
ibc1.current_song.play()
