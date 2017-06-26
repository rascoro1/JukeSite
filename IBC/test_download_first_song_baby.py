from IBCMusicManager import IBCMusicClient

client = IBCMusicClient()
client.start()
client.logon('username', 'password')
songs = client.search_song('baby')
first_song = songs[0]
first_song_id = first_song['track']['storeId']

res = client.download_song_url(first_song_id)

print("RESULTS: {}".format(res))

client.logout()
client.stop()
