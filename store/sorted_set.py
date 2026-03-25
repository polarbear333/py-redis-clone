# store/sorted_set.py
import random
from typing import List, Optional, Dict

SKIPLIST_MAXLEVEL = 32
SKIPLIST_P = 0.25


class SkipListLevel:
    __slots__ = ('forward', 'span')

    def __init__(self) -> None:
        self.forward: Optional['SkipListNode'] = None
        self.span: int = 0

class SkipListNode:
    __slots__ = ('score', 'member', 'backward', 'level')

    def __init__(self, level: int, score: float, member: bytes) -> None:
        self.score: float = score
        self.member: bytes = member
        self.backward: Optional['SkipListNode'] = None
        self.level: List[SkipListLevel] = [SkipListLevel() for _ in range(level)]

class SortedSet:

    def __init__(self) -> None:
        self._scores: Dict[bytes, float] = {}
        self.header: SkipListNode = SkipListNode(SKIPLIST_MAXLEVEL, 0.0, b"")
        self.tail: Optional[SkipListNode] = None
        self.length: int = 0
        self.level: int = 1

    def __len__(self) -> int:
        return self.length

    def _random_level(self) -> int:
        level = 1
        while random.random() < SKIPLIST_P and level < SKIPLIST_MAXLEVEL:
            level += 1
        return level

    def _insert(self, score: float, member: bytes) -> SkipListNode:
        update: List[Optional[SkipListNode]] = [None] * SKIPLIST_MAXLEVEL
        rank: List[int] = [0] * SKIPLIST_MAXLEVEL

        x = self.header
        for i in range(self.level - 1, -1, -1):
            rank[i] = rank[i + 1] if i != self.level - 1 else 0
            while x.level[i].forward and \
                  (x.level[i].forward.score < score or \
                  (x.level[i].forward.score == score and x.level[i].forward.member < member)):
                rank[i] += x.level[i].span
                x = x.level[i].forward
            update[i] = x

        level = self._random_level()
        if level > self.level:
            for i in range(self.level, level):
                rank[i] = 0
                update[i] = self.header
                update[i].level[i].span = self.length
            self.level = level

        x = SkipListNode(level, score, member)
        for i in range(level):
            x.level[i].forward = update[i].level[i].forward
            update[i].level[i].forward = x
            x.level[i].span = update[i].level[i].span - (rank[0] - rank[i])
            update[i].level[i].span = (rank[0] - rank[i]) + 1

        for i in range(level, self.level):
            update[i].level[i].span += 1

        x.backward = update[0] if update[0] != self.header else None
        if x.level[0].forward:
            x.level[0].forward.backward = x
        else:
            self.tail = x

        self.length += 1
        return x

    def _delete_node(self, x: SkipListNode, update: List[SkipListNode]) -> None:
        for i in range(self.level):
            if update[i].level[i].forward == x:
                update[i].level[i].span += x.level[i].span - 1
                update[i].level[i].forward = x.level[i].forward
            else:
                update[i].level[i].span -= 1
        
        if x.level[0].forward:
            x.level[0].forward.backward = x.backward
        else:
            self.tail = x.backward
            
        while self.level > 1 and self.header.level[self.level - 1].forward is None:
            self.level -= 1
        self.length -= 1

    def _delete(self, score: float, member: bytes) -> bool:
        update: List[Optional[SkipListNode]] = [None] * SKIPLIST_MAXLEVEL
        x = self.header
        for i in range(self.level - 1, -1, -1):
            while x.level[i].forward and \
                  (x.level[i].forward.score < score or \
                  (x.level[i].forward.score == score and x.level[i].forward.member < member)):
                x = x.level[i].forward
            update[i] = x
        
        x = x.level[0].forward
        if x and x.score == score and x.member == member:
            self._delete_node(x, update)
            return True
        return False

    def add(self, member: bytes, score: float) -> bool:
        if member in self._scores:
            old_score = self._scores[member]
            if old_score == score:
                return False  
            self._delete(old_score, member)
            self._insert(score, member)
            self._scores[member] = score
            return False  
        else:
            self._insert(score, member)
            self._scores[member] = score
            return True   

    def remove(self, member: bytes) -> bool:
        if member not in self._scores:
            return False
        score = self._scores.pop(member)
        self._delete(score, member)
        return True

    def score(self, member: bytes) -> Optional[float]:
        return self._scores.get(member)

    def rank(self, member: bytes) -> Optional[int]:
        if member not in self._scores:
            return None
        
        score = self._scores[member]
        rank_idx = 0
        x = self.header
        for i in range(self.level - 1, -1, -1):
            while x.level[i].forward and \
                  (x.level[i].forward.score < score or \
                  (x.level[i].forward.score == score and x.level[i].forward.member <= member)):
                rank_idx += x.level[i].span
                x = x.level[i].forward
                
        if x and x.member == member:
            return rank_idx - 1  
            
        raise RuntimeError(f"Internal state corrupted: {member!r} in dict but not in skiplist")

    def _get_element_by_rank(self, rank_idx: int) -> Optional[SkipListNode]:
        traversed = 0
        x = self.header
        for i in range(self.level - 1, -1, -1):
            while x.level[i].forward and traversed + x.level[i].span <= rank_idx:
                traversed += x.level[i].span
                x = x.level[i].forward
        if traversed == rank_idx:
            return x
        return None

    def range_by_rank(self, start: int, stop: int) -> List[bytes]:
        if start < 0 or start > stop or start >= self.length:
            return []
        
        node = self._get_element_by_rank(start + 1)
        res = []
        count = stop - start + 1
        
        while node and count > 0:
            res.append(node.member)
            node = node.level[0].forward
            count -= 1
        return res

    def range(self, start: int, stop: int) -> List[bytes]:
        return self.range_by_rank(start, stop)

    def count(self, min_score: float, max_score: float) -> int:
        if min_score > max_score or self.length == 0:
            return 0
            
        rank_first = 0
        x = self.header
        for i in range(self.level - 1, -1, -1):
            while x.level[i].forward and x.level[i].forward.score < min_score:
                rank_first += x.level[i].span
                x = x.level[i].forward
                
        first = x.level[0].forward
        
        if not first or first.score > max_score:
            return 0
        
        rank_last = 0
        y = self.header
        for i in range(self.level - 1, -1, -1):
            while y.level[i].forward and y.level[i].forward.score <= max_score:
                rank_last += y.level[i].span
                y = y.level[i].forward
                
        return rank_last - rank_first

    def zcard(self) -> int:
        return self.length