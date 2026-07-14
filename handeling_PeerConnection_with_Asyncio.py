import asyncio
import logging

from matplotlib.style.core import available

from announce import num_pieces

from handeling_peer_message import recv_any_message_from_peer, build_bitfield, send_intrested, send_block_req, \
    parser_peice, bitfield_parser
from peer_handeling import handshake as h
# import threading
from announce import peers
BLOCK_SIZE=16384
logging.basicConfig(filename="peerdata.log",level=logging.INFO)




# ____________________________________________________________________________________________________________________________
# tried creating one thread per peer to handel it all its functionality but not scalable architecture alternates are better
# def starting_thread(peer,handshake):
#     asyncio.run(try_connecting_with_peer(peer,handshake))
#
# for peer in peers:
#     thread=threading.Thread(target=starting_thread,args=(peer,handshake))
#     thread.start()
# _______________________________________________________________________________________________________________________________

class PeerConnection:
    def __init__(self,reader,writer,piece_manager):
        self.reader=reader
        self.writer=writer
        self.piece_manager=piece_manager
        self.remote_bitfield=[]
        self.am_chocked=True
        self.am_interested=False
    async def do_handhsake(self,handshake,peer):
        peer_ip, peer_port = peer
       # self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(peer_ip, peer_port), timeout=5)
        self.writer.write(handshake)
        await self.writer.drain()

        received_handshake_from_peer = await asyncio.wait_for(self.reader.readexactly(68), timeout=5)
        # checking validity of handshake we recived from peer
        if len(received_handshake_from_peer) < 68:
            raise ValueError("incomplete handshake")
        if received_handshake_from_peer[1:20] != b'BitTorrent protocol':
            raise ValueError("not the right protocol")
        logging.info(f"peer connected : {peer_ip} {peer_port}")
        return True

    async def receive_message(self):
        return await recv_any_message_from_peer(self.reader)
    async def exchange_bitfields(self):
        message_id, payload = await asyncio.wait_for(self.receive_message(), timeout=5)
        if message_id == 5:
            peer_bitfield = bitfield_parser(payload,num_pieces)
            self.remote_bitfield=peer_bitfield
            my_bitfield=await self.piece_manager.get_my_bitfield_bytes()
            self.writer.write(my_bitfield)
            await self.writer.drain()
    async def send_interested(self):
        self.writer.write(send_intrested())

    async def download_piece(self,piece_index):
        num_pieces_in_torrent = num_pieces  # this gives the total in the torrent
        # now here we are trying to get all the blocks in a particular piece
        #piece_index = 0  # startign from the intial block for now
        piece_length =self.piece_manager.get_piece_length(piece_index)  # getting the size of particular piece
        block_numbers = (piece_length + BLOCK_SIZE -1) // BLOCK_SIZE
        blocks = {}
        print(f"downloading peice {piece_index}")
        for block_num in range(block_numbers):  # looping through our no. of blocks per piece
                begin = block_num * BLOCK_SIZE
                length=min(BLOCK_SIZE,piece_length - begin)# calculating from where the block should begin
                send_block_req(self.writer, begin=begin, piece_index=piece_index,length=length)  # sending the req to block
                while True:
                    msg_id_of_recived_data, load =await  recv_any_message_from_peer(self.reader)
                    if msg_id_of_recived_data == 7:  # this means the it send the piece we need so we can further process the payload
                        index, begin_offset, actual_data = parser_peice(load)
                        blocks[
                            begin_offset] = actual_data  # stroing the block in the dict with the offset for later stiching
                        print(
                            f'got peice {index} which begins at the offset {begin_offset} and the length of the rest of the data {len(actual_data)}')
                        # with open(f"peice_{index} begins_{begin_offset}.bin", 'wb') as f:
                        #     f.write(actual_data)
                        #     print("done writing stuff")
                        break
                    elif msg_id_of_recived_data == 1:
                        send_block_req(self.writer, begin=begin, piece_index=piece_index,length=length)
                    elif msg_id_of_recived_data == 4:
                        continue
                    else:
                        print(f"unexpected the peice with message id 7 but got{msg_id_of_recived_data}")
        full_piece = b""
        for offset in sorted(blocks.keys()):
                full_piece += blocks[offset]
                print(f"assembled full piece {len(full_piece)} bytes")
        return True , full_piece
    async  def download_loop(self):
        while not self.piece_manager.am_I_done():
            available=[i for i, has in enumerate(self.remote_bitfield) if has]
            if not available:
                break
            idx=await self.piece_manager.claim_piece(available)
            if idx is None:
                break
            success,piece_data=await self.download_piece(idx)
            await self.piece_manager.release_piece(idx, success)
            if piece_data:
                await self.piece_manager.write_piece(idx,piece_data)








