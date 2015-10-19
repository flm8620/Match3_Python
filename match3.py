'''
FENG Leman
Sorry, I don't have too much time to put all comments

Please run this file with gameEngine.py
'''


import sys
import time
from PyQt4 import QtGui, QtCore
from PyQt4.Qt import pyqtSignal, QSize
import gameEngine
from enum import Enum


class Direction(Enum):
    Up = 0
    Down = 1
    Left = 2
    Right = 3


class DelegateState(Enum):
    Ready = 0
    Busy = 1


class Delegate(QtCore.QObject):
    # all signals for MainWindow
    delegateReady = pyqtSignal()
    createTile = pyqtSignal(int, int, list)  # int int list = i,j,matrix
    moveButton = pyqtSignal(int, int, int, int, float)  # i1,j1,i2,j2,percent
    exchangeButton = pyqtSignal(int, int, int, int)  # i1,j1,i2,j2
    zoomButton = pyqtSignal(int, int, float)  # i,j,zoomPercent
    removeButton = pyqtSignal(int, int)  # i,j
    fallButton = pyqtSignal(list, float)  # falling map,percent
    fallButtonFinish = pyqtSignal(list)  # falling map
    newTilesComingInit = pyqtSignal(list)  # newtile list
    newTilesComing = pyqtSignal(list, float)  # newtile list, percent
    newTilesFinish = pyqtSignal(list)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    def setMainWindow(self, window):
        self.window = window

    def windowInitGameReceiver(self):
        self.createTile.emit(
            self.engine._n, self.engine._m, self.engine.getMatrix())

    def exchangeTile(self, i1, j1, i2, j2):
        n = 10
        for t in range(n):
            self.moveButton.emit(i1, j1, i2, j2, t / n)
            time.sleep(0.025)
        self.exchangeButton.emit(i1, j1, i2, j2)

    def PlayerMoveReceiver(self, i, j, dirction):
        if self.engine.state != gameEngine.GameState.Ready:
            print("engine still busy!")
            return
        if dirction == Direction.Up and i >= 1:
            pair = i, j, i - 1, j
        elif dirction == Direction.Down and i < self.engine._n - 1:
            pair = i, j, i + 1, j
        elif dirction == Direction.Right and j < self.engine._m - 1:
            pair = i, j, i, j + 1
        elif dirction == Direction.Left and j >= 1:
            pair = i, j, i, j - 1
        else:
            self.delegateReady.emit()
            return
        haveMatch, matchSet = self.engine.playerMove(*pair)
        self.exchangeTile(*pair)
        if not haveMatch:
            time.sleep(0.2)
            self.exchangeTile(*pair)
            # player can go on now
            self.delegateReady.emit()
            return
        # Main game loop
        while self.engine.state != gameEngine.GameState.Ready:
            # remove tiles
            matchSet, falling = self.engine.eraseTiles()
            n = 10
            for t in range(n, 1, -1):
                for coords in matchSet:
                    i, j = coords[0], coords[1]
                    self.zoomButton.emit(i, j, t / n)
                time.sleep(0.025)

            for coords in matchSet:
                i, j = coords[0], coords[1]
                self.removeButton.emit(i, j)

            # tiles fall
            n = 10
            for t in range(n):
                self.fallButton.emit(falling, t / n)
                time.sleep(0.025)
            self.fallButtonFinish.emit(falling)

            # tiles coming
            newTiles = self.engine.tilesComing()
            self.newTilesComingInit.emit(newTiles)
            n = 10
            for t in range(n):
                self.newTilesComing.emit(newTiles, t / n)
                time.sleep(0.025)
            self.newTilesFinish.emit(newTiles)
        # player can go on now
        self.delegateReady.emit()


class MyButton(QtGui.QPushButton):
    exchange = pyqtSignal(int, int, Direction)
    color=['#FF4040','#9ACD32','#7B68EE','#EEEE00','#7D26CD']

    def __init__(self, name, parent, i, j):
        super().__init__(name, parent)
        self._i = i
        self._j = j
        self.setStyleSheet('QPushButton {background-color: '+self.color[int(name)%5]+'; color: black;}')

    def mouseReleaseEvent(self, e):
        x, y = e.x(), e.y()
        w, h = self.size().width(), self.size().height()

        if x > w and 0 <= y < h:
            self.exchange.emit(self._i, self._j, Direction.Right)
        elif x < 0 and 0 <= y < h:
            self.exchange.emit(self._i, self._j, Direction.Left)
        elif y > h and 0 <= x < w:
            self.exchange.emit(self._i, self._j, Direction.Down)
        elif y < 0 and 0 <= x < w:
            self.exchange.emit(self._i, self._j, Direction.Up)

        return QtGui.QPushButton.mouseMoveEvent(self, e)


class MainWindow(QtGui.QWidget):
    playerMoved = pyqtSignal(int, int, Direction)
    initialRequest = pyqtSignal()

    def __init__(self, gameDelegate):
        super(MainWindow, self).__init__()
        self.state = DelegateState.Busy
        self.gameDelegate = gameDelegate
        self.setGeometry(300, 300, 500, 500)
        self.setWindowTitle('Match 3')
        self.show()

    def initGame(self):
        self.initialRequest.emit()

    def initializeReceiver(self, n, m, matrix):
        self.tiles = []
        self._n = n
        self._m = m
        for i in range(n):
            for j in range(m):
                btn = MyButton(str(matrix[i * m + j]), self, i, j)
                self.tiles.append(btn)
                x, y, s = self.getSize(i, j)
                btn.move(x, y)
                btn.resize(s)
                btn.exchange.connect(self.buttonDraged)
                btn.show()
        self.state = DelegateState.Ready

    def buttonMoveReceiver(self, i1, j1, i2, j2, percent):
        btn1 = self.getTile(i1, j1)
        btn2 = self.getTile(i2, j2)
        x1, y1, s1 = self.getSize(i1, j1)
        x2, y2, s2 = self.getSize(i2, j2)
        btn2.move(x2 + percent * (x1 - x2), y2 + percent * (y1 - y2))
        btn1.move(x1 + percent * (x2 - x1), y1 + percent * (y2 - y1))

    def buttonExchangeReceiver(self, i1, j1, i2, j2):
        btn1 = self.getTile(i1, j1)
        btn2 = self.getTile(i2, j2)
        self.setTile(i1, j1, btn2)
        self.setTile(i2, j2, btn1)
        btn1._i, btn1._j = i2, j2
        btn2._i, btn2._j = i1, j1
        x1, y1, s1 = self.getSize(i1, j1)
        x2, y2, s2 = self.getSize(i2, j2)
        btn2.move(x1, y1)
        btn1.move(x2, y2)

    def buttonZoomReceiver(self, i, j, percent):
        btn = self.getTile(i, j)
        x, y, s = self.getSize(i, j)
        w, h = s.width(), s.height()
        x1, y1 = x + (1 - percent) * w / 2, y + (1 - percent) * h / 2
        btn.resize(w * percent, h * percent)
        btn.move(x1, y1)

    def buttonRemoveReceiver(self, i, j):
        btn = self.getTile(i, j)
        btn.deleteLater()
        self.tiles[i * self._m + j] = None

    def buttonFallReceiver(self, fallingMap, percent):
        for fall in fallingMap:
            i1, j1, i2, j2 = fall
            btn = self.getTile(i1, j1)
            x1, y1, s1 = self.getSize(i1, j1)
            x2, y2, s2 = self.getSize(i2, j2)
            btn.move(x1 + percent * (x2 - x1), y1 + percent * (y2 - y1))

    def buttonFallFinishReceiver(self, fallingMap):
        tempList = [None] * (self._n * self._m)
        for fall in fallingMap:
            i1, j1, i2, j2 = fall
            btn = self.getTile(i1, j1)
            tempList[i1 * self._m + j1] = btn
            self.setTile(i1, j1, None)
        for fall in fallingMap:
            i1, j1, i2, j2 = fall
            btn = tempList[i1 * self._m + j1]
            assert self.getTile(i2, j2) == None
            self.setTile(i2, j2, btn)
            x2, y2, s2 = self.getSize(i2, j2)
            btn.move(x2, y2)
            btn._i, btn._j = i2, j2

    def buttonComingInitReceiver(self, newTiles):
        for tile in newTiles:
            i, j, value = tile
            btn = MyButton(str(value), self, i, j)
            assert self.getTile(i, j) == None
            self.setTile(i, j, btn)
            x, y, s = self.getSize(i, j)
            btn.move(x, y)
            btn.resize(s)
            btn.exchange.connect(self.buttonDraged)
            btn.show()

    def buttonComingReceiver(self, newTiles, percent):
        for tile in newTiles:
            i, j, value = tile
            btn = self.getTile(i, j)
            x, y, s = self.getSize(i, j)
            w, h = s.width(), s.height()
            x1, y1 = x + (1 - percent) * w / 2, y + (1 - percent) * h / 2
            btn.resize(w * percent, h * percent)
            btn.move(x1, y1)

    def buttonComingFinishReceiver(self, newTiles):
        for tile in newTiles:
            i, j, value = tile
            btn = self.getTile(i, j)
            assert btn != None
            x, y, s = self.getSize(i, j)
            btn.move(x, y)
            btn.resize(s)

    def getSize(self, i, j):
        s = self.size()
        h, w = s.height(), s.width()
        n, m = self._n, self._m
        width, height = w / m, h / n
        x, y = width * j, height * i
        return x, y, QSize(width, height)

    def getTile(self, i, j):
        assert 0 <= i < self._n
        assert 0 <= j < self._m
        return self.tiles[i * self._m + j]

    def setTile(self, i, j, tile):
        assert 0 <= i < self._n
        assert 0 <= j < self._m
        self.tiles[i * self._m + j] = tile

    def buttonDraged(self, i, j, direction):
        if self.state == DelegateState.Busy:
            print('Delegate still busy!!!')
        else:
            self.state = DelegateState.Busy
            self.playerMoved.emit(i, j, direction)

    def delegateFinished(self):
        self.state = DelegateState.Ready


def main():
    '''
    Program structure:
    3 module: MainWindow, Delegate, GameEngine
                ----------              \
                |        |              |
                | Window |              |>  main Thread   
                |        |              |
                ----------              /
                  ^   |  
    GuiControl    |   |  initialRequest   >>> signals
      Request     |   V
                ----------               \
                |        |               |
                |Delegate|               |
                |        |               |
                ----------               |
                  ^   |                  |
    GuiControl    |   |  initialRequest  |> worker Thread
      Request     |   V         \        |   
                ----------       \       |
                |        |        -------|---> function call
                | Engine |               |
                |        |               |
                ----------               /
    '''
    app = QtGui.QApplication(sys.argv)
    engine = gameEngine.Engine(8, 8, 4)
    delegate = Delegate(engine)
    workerThread = QtCore.QThread()
    delegate.moveToThread(workerThread)
    win = MainWindow(delegate)

    # connect all signals and slots between delegate and window
    delegate.setMainWindow(win)
    delegate.createTile.connect(win.initializeReceiver)
    delegate.moveButton.connect(win.buttonMoveReceiver)
    delegate.exchangeButton.connect(win.buttonExchangeReceiver)
    delegate.zoomButton.connect(win.buttonZoomReceiver)
    delegate.removeButton.connect(win.buttonRemoveReceiver)
    delegate.delegateReady.connect(win.delegateFinished)
    delegate.fallButton.connect(win.buttonFallReceiver)
    delegate.fallButtonFinish.connect(win.buttonFallFinishReceiver)
    delegate.newTilesComing.connect(win.buttonComingReceiver)
    delegate.newTilesFinish.connect(win.buttonComingFinishReceiver)
    delegate.newTilesComingInit.connect(win.buttonComingInitReceiver)
    
    win.initialRequest.connect(delegate.windowInitGameReceiver)
    win.playerMoved.connect(delegate.PlayerMoveReceiver)
    #
    
    # start workerThread's event loop
    workerThread.start()
    win.initGame()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
