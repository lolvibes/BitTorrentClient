import struct


# handeling any message checking the standard message format
def recv_any_message_from_peer(client):
    raw_bytes=recv_any_message_exact(client,4) # reading the prefix
    msg_len=struct.unpack(">I",raw_bytes)[0]# our message length aside from the prefix
    if msg_len==0:
        return None,None
    raw_msg=recv_any_message_exact(client,msg_len)# we are reading the exact message length
    message_id=raw_msg[0]# within our exact message this is the first byte
    payload=raw_msg[1:] # remaining size slicing trough
    return message_id,payload # returning message id and payload

def recv_any_message_exact(sock,n):# reading what we are recving
    buf=b""
    while len(buf)<n:
        chunk=sock.recv(n- len(buf))
        if not chunk:
            raise ConnectionError("peer disconnect")
        buf+=chunk

    return buf
#-------------------------* hahah ----------------------------------------

# parsing the bitfield that we will recive as payload bcz its in raw bytes
def bitfield_parser(payload, num_peices):
    has_piece=[]
    for bytes in payload:# for each byte in  payload we will check
        for bit in range(7,-1,-1): # we will get MSB first and then go to LSB
            # 1<<3 is like 1000 its like masking the 1 at 2^3 which is 8
            #1<<7 is like 1000000
            bool_val=bool(bytes & 1<<bit)# performing bit wise and with the massk to get the value at that particiluar bit is it one or zero
            has_piece.append(bool_val) # passing the values in has list like it  tttftft
    return has_piece[:num_peices] # stoping the grabage value from our bytes and trim that to  our peices

# building our own bitfield
def build_bitfield(my_pieces, num_piececs):
    num_bytes=(num_piececs +7)//8 # rounding off our peice so  we can get the extraw space
    bitfield=bytearray(num_bytes) # how many bytes do we need in our bitfield initallly all zeros
    #byte array is mutable bytes of array unlike  regular bytes which are frozen u can manipulate individual bit
    for i in my_pieces:
        bitfield[i//8] |=(1<<(7-(i%8))) # intially we see that peice belongs to which byte
        # then we  see the position of that peice in that byte  then we mask it to get that bit onn
        #with the help o
    length=1+ len(bitfield)
    return struct.pack(">I", length)+bytes([5])+ bytes(bitfield) # packing it in raw bytes

# we need to sendd the intrested to the clientin theri peice
def send_intrested():
     return struct.pack(">I",1 )+ bytes([2])

# no we are ginna assk the peer for the block of the piece
BLOCK_SIZE=16*1024
def send_block_req(sock,begin, piece_index=1,length=BLOCK_SIZE):
    payload=struct.pack(">III",piece_index,begin,length)
    sock.send(struct.pack(">I",1+len(payload))+bytes([6])+payload)
# after a  request we  send the peer send the message peice which have payload

def parser_peice(payload):
    index= struct.unpack(">I",payload[0:4])[0]
    begin_offset=struct.unpack(">I",payload[4:8])[0]
    actual_data=payload[8:]
    return index,begin_offset,actual_data



