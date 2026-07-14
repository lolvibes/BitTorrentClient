import asyncio

from handeling_peer_message import build_bitfield



class PieceManager:

    def __init__(self,num_pieces,piece_length,total_file_length):
        self.num_pieces=num_pieces
        self.piece_length=piece_length
        self.my_piece=set()
        self.piece_in_progress=set()
        self.lock=asyncio.Lock()
        self.total_file_length=total_file_length
        self.file=open("test_file_n.bin", "wb")
        self.file.truncate(total_file_length)
        self.file_lock=asyncio.Lock()
    async def claim_piece(self, available_piece_indices):
        async with self.lock:
            for indx in available_piece_indices:
                if indx not in self.my_piece and indx not in self.piece_in_progress:
                    self.piece_in_progress.add(indx)
                    return indx
            return None
    async def release_piece(self, piece_index, sucess:bool):
        async with self.lock:
            self.piece_in_progress.discard(piece_index)
            if sucess:
                self.my_piece.add(piece_index)
    async def get_my_bitfield_bytes(self):
        async with self.lock:
            piece_copy=set(self.my_piece)
            return build_bitfield(piece_copy,self.num_pieces)
    def am_I_done(self):
        return len(self.my_piece) == self.num_pieces

    def get_piece_length(self,piece_index):
        #for the last piece which are usually shorter than the standard piece lengths
        if piece_index==self.num_pieces-1:
            return self.total_file_length - self.piece_length * (self.num_pieces -1)
        return self.piece_length
    async def write_piece(self,piece_index,piece_data):
        offset = piece_index *self.piece_length
        async with self.file_lock:
            self.file.seek(offset)
            self.file.write(piece_data)
            self.file.flush()
    def close(self):
        self.file.close()