# JukeSite
Create wifi enabled speaker with a raspberry pi and manage collaborative playlists with users within your LAN through a mobile friendly website.
</br>

Rooms/Queue
![Demo](https://github.com/rascoro1/SeleniumINI/blob/master/room.png)

Search
![Demo](https://github.com/rascoro1/SeleniumINI/blob/master/search.png)

## JukeSite Implementation
To implement JukeSite in your network you will need at least 2 Raspberry pis and 2 auxilary cables. Thats it!
JukeSite uses a master slave architecture to manage all of the speakers in your house/LAN.
The master will host the website users interact with which will control speakers.
The slaves will be connected to speakers via auxilary cords.

### Creating the Master
The master should be created first and contains the most dependancies.
Connect to your raspberry pi that will be the master and enter the following commands:

```
# Set hostname to 'jukesite'
pi@192.168.1.60:~ $ sudo echo 'JukeSite' > /etc/hostname
pi@192.168.1.60:~ $ sudo reboot

# Download the dependancies and master software
pi@JukeSite:~/Desktop $ sudo apt-get install nmap
pi@JukeSite:~/Desktop $ sudo apt-get install apache2
pi@JukeSite:~/Desktop $ git clone https://github.com/rascoro1/JukeSite
pi@JukeSite:~/Desktop $ mkdir songs
pi@JukeSite:~/Desktop $ sudo ln -s /home/pi/Desktop/songs /var/www/html
pi@JukeSite:~/Desktop $ cd JukeSite/DjangoJukeSite/DjangoJukeSite/
# Install the python3 requirments
pi@JukeSite:~/Desktop/JukeSite/DjangoJukeSite/DjangoJukeSite/ $ pip3 install cbm_requirements.txt
# Setup the django website
pi@JukeSite:~/Desktop/JukeSite/DjangoJukeSite/DjangoJukeSite/ $ python3 manage.py makemigrations
pi@JukeSite:~/Desktop/JukeSite/DjangoJukeSite/DjangoJukeSite/ $ python3 manage.py migrate
# Follow the instruction on creating a user, this will be an admin account that has more fearures.
pi@JukeSite:~/Desktop/JukeSite/DjangoJukeSite/DjangoJukeSite/ $ python3 manage.py createsuperuser

Open ~/Desktop/JukeSite/DjangoJukeSite/DjangoJukeSite/JukeSite/views.py file.
On the 10th line or so replace:
Interface.music_manager_logon('username', 'password')
With you actual google username and password
```
At this point everything should have downloaded and worked correctly.
PYTHON3 ONLY, ALWAYS REMEMBER THAT
The master website 'JukeSite' is not up yet and we will start it with the next command.
```
pi@JukeSite:~/Desktop/JukeSite/DjangoJukeSite/DjangoJukeSite/ $ python3 manage.py runserver jukesite:8000
```
JukeSite should come up and can be located at http://jukesite:8000 in your browser.
Click login on the top right and register a account. This is how a normal user signs up. Try testing your admin account also.

As of right no there will be nothing in your rooms or your Queue. We have to setup our slaves to do this.

#### Creating the Slaves
Slaves are very simple controllers that can perform certain tasks to the speaker connected to it.
They have a restful API on them as a service that the master uses to control the speakers behaviour.
The slave can play, stop, resume and download a song. The slave can also control the volume of speaker.


Connect to your raspberry pi that will be the slave(s) and enter the following commands:


```

# Make sure the hostname begins with the 3 characters 'ibc' this indicates that it is a slave to the master.
# Set hostname to 'ibc<any unique chars/numbers>' e.g. 'ibcKitchen'
pi@192.168.1.60:~ $ sudo echo 'ibcKitchen' > /etc/hostname
pi@192.168.1.60:~ $ sudo reboot

pi@ibcKitchen:~ $ cd ~/Desktop
# Download the dependancies and master software
pi@JukeSite:~/Desktop $ sudo apt-get install wget
pi@JukeSite:~/Desktop $ git clone https://github.com/rascoro1/JukeSite
pi@JukeSite:~/Desktop $ mkdir songs
pi@JukeSite:~/Desktop $ cd JukeSite/IBC_service/
# Install the python3 requirments
pi@JukeSite:~/Desktop/JukeSite/IBC_service/ $ pip3 install ibc_requirements.txt
# start the flask restful api
pi@JukeSite:~/Desktop/JukeSite/IBC_service/ $ python3 IBCService.py
```
Now you have one slave up this process is repeated for the other slaves.
The slaves will be automatically added to 'JukeSite' only if the host name started with 'ibc'.

Now lets test the slave by opening a browser and typing:
http://ibcKitchen:5000/Status

it should return with:
{
    "status": "WARNING",
    "message": "No song is playing."
}

At this point you have one slave up and one master.
Logon to the master raspi and restart the JukeSite service you started previously.
On startup JukeSite will perform a scan of the network looking for devices with hostnames starting with ibc.
These devices are then added as rooms onto the website on the left hand column.

Now Logon to JukeSite (jukesite:8000) as admin.
Select the room 'ibcKitchen'.
You will see that there is a text box with 'ibcKitchen' in it. Enter a name into there and hit submit if you would like to rename the room.

Connect your slave to a speaker with an auxilary cable.
Now search for a song and select a song to add it to the 'ibcKitchen' Queue.
The song should start playing from the speaker once it has been downloaded.
Feel free too add as many songs to the Queue as you would like.

Repeat and enjoy!
