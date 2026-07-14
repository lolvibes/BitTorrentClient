import asyncio

from handeling_peer_message import build_bitfield


class PieceManager:

    def __init__(self,num_pieces,piece_length,total_file_length):
        self.num_pieces=num_pieces
        self.piece_length=piece_length
        self.my_piece=set()
        self.piece_in_progress=set()
        self.lock=asyncio.Lock()
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

async def test():
    pm = PieceManager(num_pieces=5, piece_length=1048576, total_file_length=5242880)

    idx = await pm.claim_piece([0, 1, 2, 3, 4])
    print(f"claimed piece: {idx}")  # should print 0

    idx2 = await pm.claim_piece([0, 1, 2])  # 0 already claimed
    print(f"claimed piece: {idx2}")  # should print 1

    await pm.release_piece(0, sucess=True)
    print(f"my_pieces: {pm.my_piece}")  # {0}
    print(f"done: {pm.am_I_done()}")  # False


asyncio.run(test())