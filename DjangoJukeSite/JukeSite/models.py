from django.db import models

# Create your models here.

from django.db import models

class Track(models.Model):
    """
    database table containing track information
    """
    beatsPerMinute = models.IntegerField(default=0)
    playCount = models.IntegerField(default=0)
    storeId = models.CharField(max_length=256, primary_key=True)
    title = models.CharField(max_length=256)
    albumArtRef = models.CharField(max_length=1024)
    artistId = models.CharField(max_length=256)
    creationTimestamp = models.CharField(max_length=256)
    album = models.CharField(max_length=256)
    recentTimestamp = models.CharField(max_length=256)
    artist = models.CharField(max_length=256)
    nid = models.CharField(max_length=256)
    estimatedSize = models.CharField(max_length=256)
    albumId = models.CharField(max_length=256)
    genre = models.CharField(max_length=256)
    artistArtRef = models.CharField(max_length=1024)
    kind = models.CharField(max_length=256)
    lastModifiedTimestamp = models.CharField(max_length=256)
    durationMillis = models.CharField(max_length=256)

    def __str__(self):
        return self.title


class Room(models.Model):
    """
    database table containing room information
    """
    id = models.AutoField(primary_key=True)
    hostname = models.CharField(max_length=256)
    ip = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    queue_id = models.CharField(max_length=256, default=None)

    def __str__(self):
        return self.name

class Queue(models.Model):
    id = models.AutoField(primary_key=True)
    storeId = models.CharField(max_length=256)
    room_id = models.CharField(max_length=256)
    position = models.IntegerField(default=0)
    # user = models.CharField(max_length=256)
