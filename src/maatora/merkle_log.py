import hashlib


def _sha(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


class MerkleLog:
    def __init__(self) -> None:
        self._leaves: list[bytes] = []

    def append(self, entry: bytes) -> int:
        self._leaves.append(_sha(entry))
        return len(self._leaves) - 1

    def _levels(self) -> list[list[bytes]]:
        levels: list[list[bytes]] = [list(self._leaves)]
        while len(levels[-1]) > 1:
            prev = levels[-1]
            nxt: list[bytes] = []
            i = 0
            while i < len(prev):
                if i + 1 < len(prev):
                    nxt.append(_sha(prev[i] + prev[i + 1]))
                    i += 2
                else:
                    nxt.append(prev[i])
                    i += 1
            levels.append(nxt)
        return levels

    def root(self) -> bytes:
        if not self._leaves:
            return _sha(b"")
        return self._levels()[-1][0]

    def proof(self, index: int) -> list[bytes]:
        if not (0 <= index < len(self._leaves)):
            raise IndexError("index out of range")
        path: list[bytes] = []
        idx = index
        for level in self._levels()[:-1]:
            if idx % 2 == 0:
                if idx + 1 < len(level):
                    path.append(level[idx + 1])
                else:
                    path.append(b"")
            else:
                path.append(level[idx - 1])
            idx //= 2
        return path

    @staticmethod
    def verify_proof(entry: bytes, index: int, proof: list[bytes], root: bytes) -> bool:
        h = _sha(entry)
        idx = index
        for sibling in proof:
            if sibling != b"":
                if idx % 2 == 0:
                    h = _sha(h + sibling)
                else:
                    h = _sha(sibling + h)
            idx //= 2
        return h == root
