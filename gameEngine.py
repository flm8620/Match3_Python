'''
FENG Leman
Sorry, I don't have too much time to put all comments

Please run match3.py
'''
import random
from enum import Enum


class GameState(Enum):
    Ready = 0
    Erasing = 1
    NewTileComing = 2
    Busy = 3


class GameEngineException(Exception):
    pass


class Match():

    def __init__(self, i1=-1, j1=-1, i2=-1, j2=-1, length=0, isHoriz=True):
        self.i1, self.j1, self.i2, self.j2 = i1, j1, i2, j2
        self.length = length
        self.isHoriz = isHoriz

    def pointA(self):
        return self.i1, self.j1

    def pointB(self):
        return self.i2, self.j2


class Engine():

    def __init__(self, n, m, typeNum):
        assert n > 0 and m > 0
        self._typeNum = max(4, typeNum)
        self._n = n
        self._m = m
        self._data = []
        self.score = 0
        self.state = GameState.Busy
        self.toBeRemoved = set()
        for i in range(n * m):
            self._data.append(random.randint(0, self._typeNum - 1))
        self.removeMatch()
        self.state = GameState.Ready

    def getMatrix(self):
        return self._data

    def item(self, i, j):
        assert i >= 0 and i < self._n
        assert j >= 0 and j < self._m
        return self._data[i * self._m + j]

    def itemSafe(self, i, j):
        ''' with index check'''
        if i >= 0 and i < self._n:
            if j >= 0 and j < self._m:
                return self._data[i * self._m + j]
        return -1

    def itemSet(self, i, j, value):
        assert i >= 0 and i < self._n
        assert j >= 0 and j < self._m
        self._data[i * self._m + j] = value

    def haveMatch(self):
        return self.findMatchHorizontal().length > 0 or self.findMatchVertical().length > 0

    def removeMatch(self):
        while self.haveMatch():
            noMoreMatch = False
            nextI, nextJ = 0, 0
            while not noMoreMatch:
                match = self.findMatchHorizontal(nextI, nextJ)
                if match.length != 0:
                    # change color of some one in middle to break this match
                    self.itemSet(
                        match.i1, match.j1 + random.randint(1, match.length - 2), (self.item(*match.pointA()) + random.randint(1, self._typeNum - 1)) % self._typeNum)
                else:
                    noMoreMatch = True
                nextI, nextJ = match.pointA()
            noMoreMatch = False
            nextI, nextJ = 0, 0
            while not noMoreMatch:
                match = self.findMatchVertical(nextI, nextJ)
                if match.length != 0:
                    # change color of some one in middle to break this match
                    self.itemSet(
                        match.i1 + random.randint(1, match.length - 2), match.j1, (self.item(*match.pointA()) + random.randint(1, self._typeNum - 1)) % self._typeNum)
                else:
                    noMoreMatch = True
                nextI, nextJ = match.pointA()

    def findAllMatch(self):
        matches = []
        nextI, nextJ = 0, 0
        noMoreMatch = False
        while not noMoreMatch:
            match = self.findMatchHorizontal(nextI, nextJ)
            if match.length != 0:
                i, j = match.pointA()
                for k in range(match.length):
                    matches.append((i, j + k))
            else:
                noMoreMatch = True
            nextI, nextJ = match.pointB()
        noMoreMatch = False
        nextI, nextJ = 0, 0
        while not noMoreMatch:
            match = self.findMatchVertical(nextI, nextJ)
            if match.length != 0:
                i, j = match.pointA()
                for k in range(match.length):
                    matches.append((i + k, j))
            else:
                noMoreMatch = True
            nextI, nextJ = match.pointB()
            return set(matches)

    def findMatchHorizontal(self, startI=0, startJ=0):
        i = startI
        while i < self._n:
            if i == startI:
                j = startJ
            else:
                j = 0
            lastColor = -1
            matchNum = 0
            while j < self._m:
                if lastColor == self.item(i, j):
                    matchNum += 1
                    if matchNum >= 3:
                        if j == self._m - 1 or self.item(i, j + 1) != lastColor:
                            return Match(i, j - matchNum + 1, i, j, matchNum, isHoriz=True)
                else:
                    matchNum = 1
                    lastColor = self.item(i, j)
                j += 1
            i += 1
        return Match()

    def findMatchVertical(self, startI=0, startJ=0):
        j = startJ
        while j < self._m:
            if j == startJ:
                i = startI
            else:
                i = 0
            lastColor = -1
            matchNum = 0
            while i < self._n:
                if lastColor == self.item(i, j):
                    matchNum += 1
                    if matchNum >= 3:
                        if i == self._n - 1 or self.item(i + 1, j) != lastColor:
                            return Match(i - matchNum + 1, j, i, j, matchNum, isHoriz=False)
                else:
                    matchNum = 1
                    lastColor = self.item(i, j)
                i += 1
            j += 1
        return Match()

    def exchangable(self, i, j, isHoriz):
        '''return True/False, set of (i,j) with will be erased'''
        tiles = []
        if isHoriz:
            assert 0 <= i < self._n and 0 <= j < self._m - 1
            '''
              17
              28
            34xy9a
              5b
              6c
            '''
            x = self.item(i, j)
            y = self.item(i, j + 1)
            j2 = j + 1
            t1, t2 = self.itemSafe(i - 2, j), self.itemSafe(i - 1, j)
            t3, t4 = self.itemSafe(i, j - 2), self.itemSafe(i, j - 1)
            t5, t6 = self.itemSafe(i + 1, j), self.itemSafe(i + 2, j)
            t7, t8 = self.itemSafe(i - 2, j2), self.itemSafe(i - 1, j2)
            t9, ta = self.itemSafe(i, j2 + 1), self.itemSafe(i, j2 + 2)
            tb, tc = self.itemSafe(i + 1, j2), self.itemSafe(i + 2, j2)
            if y == t1 == t2:
                tiles.append((i, j))
                tiles.append((i - 2, j))
                tiles.append((i - 1, j))
            if y == t3 == t4:
                tiles.append((i, j))
                tiles.append((i, j - 2))
                tiles.append((i, j - 1))
            if y == t5 == t6:
                tiles.append((i, j))
                tiles.append((i + 1, j))
                tiles.append((i + 2, j))
            if y == t2 == t5:
                tiles.append((i, j))
                tiles.append((i - 1, j))
                tiles.append((i + 1, j))
            if x == t7 == t8:
                tiles.append((i, j2))
                tiles.append((i - 2, j2))
                tiles.append((i - 1, j2))
            if x == t9 == ta:
                tiles.append((i, j2))
                tiles.append((i, j2 + 1))
                tiles.append((i, j2 + 2))
            if x == tb == tc:
                tiles.append((i, j2))
                tiles.append((i + 1, j2))
                tiles.append((i + 2, j2))
            if x == t8 == tb:
                tiles.append((i, j2))
                tiles.append((i - 1, j2))
                tiles.append((i + 1, j2))

        else:
            assert 0 <= i < self._m and 0 <= j < self._m
            '''
              1
              2
            34x56
            78y9a
              b
              c
            '''
            x = self.item(i, j)
            y = self.item(i + 1, j)
            i2 = i + 1
            t1, t2 = self.itemSafe(i - 2, j), self.itemSafe(i - 1, j)
            t3, t4 = self.itemSafe(i, j - 2), self.itemSafe(i, j - 1)
            t5, t6 = self.itemSafe(i, j + 1), self.itemSafe(i, j + 2)
            t7, t8 = self.itemSafe(i2, j - 2), self.itemSafe(i2, j - 1)
            t9, ta = self.itemSafe(i2, j + 1), self.itemSafe(i2, j + 2)
            tb, tc = self.itemSafe(i2 + 1, j), self.itemSafe(i2 + 2, j)
            if y == t1 == t2:
                tiles.append((i, j))
                tiles.append((i - 2, j))
                tiles.append((i - 1, j))
            if y == t3 == t4:
                tiles.append((i, j))
                tiles.append((i, j - 2))
                tiles.append((i, j - 1))
            if y == t5 == t6:
                tiles.append((i, j))
                tiles.append((i, j + 1))
                tiles.append((i, j + 2))
            if y == t4 == t5:
                tiles.append((i, j))
                tiles.append((i, j + 1))
                tiles.append((i, j - 1))
            if x == t7 == t8:
                tiles.append((i2, j))
                tiles.append((i2, j - 1))
                tiles.append((i2, j - 2))
            if x == t9 == ta:
                tiles.append((i2, j))
                tiles.append((i2, j + 1))
                tiles.append((i2, j + 2))
            if x == tb == tc:
                tiles.append((i2, j))
                tiles.append((i2 + 1, j))
                tiles.append((i2 + 2, j))
            if x == t8 == t9:
                tiles.append((i2, j))
                tiles.append((i2, j + 1))
                tiles.append((i2, j - 1))
        tiles = set(tiles)
        return len(tiles) > 0, tiles

    def findMove(self):
        '''Todo: a hint button for player'''
        for i in range(self._n):
            for j in range(self._m - 1):
                have, tiles = self.exchangable(i, j, isHoriz=True)
                if have:
                    return i, j, i, j + 1
        for i in range(self._n - 1):
            for j in range(self._m):
                have, tiles = self.exchangable(i, j, isHoriz=False)
                if have:
                    return i, j, i + 1, j
        return -1, -1, -1, -1

    def printAll(self):
        '''for debug'''
        for i in range(self._n):
            for j in range(self._m):
                print(self.item(i, j), end='')
            print("")

    def playerMove(self, i1, j1, i2, j2):
        self.state = GameState.Busy
        A = i1 == i2 and (j1 == j2 + 1 or j1 == j2 - 1)
        B = j1 == j2 and (i1 == i2 + 1 or i1 == i2 - 1)
        assert A or B
        assert 0 <= i1 < self._n and 0 <= i2 < self._n
        assert 0 <= j1 < self._m and 0 <= j2 < self._m
        i1, i2 = min(i1, i2), max(i1, i2)
        j1, j2 = min(j1, j2), max(j1, j2)

        haveMatch, matchSet = self.exchangable(i1, j1, (i1 == i2))
        if haveMatch:
            a, b = self.item(i1, j1), self.item(i2, j2)
            self.itemSet(i1, j1, b)
            self.itemSet(i2, j2, a)
            self.state = GameState.Erasing
        else:
            self.state = GameState.Ready
        return haveMatch, matchSet

    def eraseTiles(self):
        if self.state != GameState.Erasing:
            raise GameEngineException("Wrong state: erasing")
        matches = self.findAllMatch()
        for tile in matches:
            x, y = tile
            self.itemSet(x, y, -1)
        fallingMap = []
        for i in reversed(range(self._n)):
            for j in range(self._m):
                if self.item(i, j) == -1:
                    k = i
                    while k >= 0 and self.item(k, j) == -1:
                        k -= 1
                    if k == -1:  # this col is empty
                        continue
                    else:
                        self.itemSet(i, j, self.item(k, j))
                        self.itemSet(k, j, -1)
                        fallingMap.append((k, j, i, j))
        self.state = GameState.NewTileComing
        return matches,fallingMap

    def tilesComing(self):
        if self.state != GameState.NewTileComing:
            raise GameEngineException("Wrong state: newtilecoming")
        newTiles = []
        for i in range(self._n):
            for j in range(self._m):
                if self.item(i, j) == -1:
                    self.itemSet(i, j, random.randint(0, self._typeNum - 1))
                    newTiles.append((i, j, self.item(i, j)))
        if self.haveMatch():
            self.state = GameState.Erasing
        else:
            self.state = GameState.Ready
        return newTiles
