import random
import string
import parser
import requests
import hashlib


#gloabal variable
global result
global announce
global info
global num_pieces
#constants
PORT=6881

with open('fight.club.10th.anniversary.edition.1999.1080p.brrip.x264.yify_201908_archive.torrent' , 'rb') as file:
    data=file.read()
# data=b'd4:name7:atharvai3e5:listl4:spam3:egge'
index=0
while index < len(data):# this code checks all the variation and doesn't let any of the object remain unread
    result, new_index=parser.decoder(data,index)
    print(result)
    announce=result[b"announce"].decode()
    info=result[b'info']
    index=new_index
url= announce

num_pieces=len(result[b'info'][b'pieces'] )//20 # for each peice consist 20 bytes of hash fucntion

# 1 of the param req with get req
info_start = data.find(b'4:info') + 6
_, end = parser.decoder(data, info_start)
info_hash = hashlib.sha1(data[info_start:end]).digest() #one of the param in GET req tracker need it in 20 bytes not python dic
print(f"info hash{info_hash} ")
# 2 param
peer_id= "-PC0001-" +"".join(random.choices(string.digits,k=12))
# 3 of the many params

#there are two types of torrent
#multi file torrent and single file torrent
left=0
if b'files' in result[b'info']:
    for f in result[b'info'][b'files']:
        left+=int(f[b'length'])
else:
     left=result[b'info'][b'length']


# dict of prams  # / ->line continuation if u forgot
params=\
{
    'info_hash':info_hash,
    'peer_id':peer_id,
    'port':PORT,
    'uploaded':0,
    'downloaded':0,
    'left':left,
    'compact':1,
    'numwant': 200, # telling the tracker i need aaround 200 pers
    'event':'started'
}

# mild starting of getting peer list
response=requests.get(url,params=params)
print(response.url) # tracker sends the responsible data  and peer list in b encoded
tracker_data,new_index=parser.decoder(response.content,0) # passing tracker data in  our deccoder


# getting peer list
peer_data=tracker_data[b'peers']# raw bytes from the tracker these have 6 bytes for each peer
peers=[]# for storing peer ip and port
for i in range(0,len(peer_data),6): # we need exact steping 6 bcz verything is clampppedin peer_data
    ip_bytes=peer_data[i:i+4] # selecting first four bytes through slicing but need to join in ip format
    ip=".".join(str(b) for b in ip_bytes) # this fucntion is similar to for b in ip_bytes
                                                                        #   ip=b+"."
    port_bytes=peer_data[i+4:i+6] # getting the port for that exact ip in that 6 ray byte range by grabing the exact
    port=int.from_bytes(port_bytes,'big') # port_bytes contain the  raw bits it need to convert into the integers
    peers.append((ip,port))
print(len(peers))
print(result[b'announce-list'])