import eyed3
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QKeyEvent, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from urllib.request import urlopen
from utils import escape, search


class Widget(QWidget):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.title = 'ID3 Tag Modifier'
        self.initUI()

    def initUI(self) -> None:
        """initialize user interface"""
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, 900, 550)
        main = QVBoxLayout()

        grid = QGridLayout()
        self.select = QLineEdit(self)
        self.select.setReadOnly(True)
        grid.addWidget(self.select, 0, 0)
        selectBtn = QPushButton(QIcon('figure/select.png'), ' Select', self)
        selectBtn.clicked.connect(self.selectAudio)
        grid.addWidget(selectBtn, 0, 1)

        self.search = QLineEdit(self)
        grid.addWidget(self.search, 1, 0)
        searchBtn = QPushButton(QIcon('figure/search.png'), ' Search', self)
        searchBtn.clicked.connect(self.searchInfo)
        grid.addWidget(searchBtn, 1, 1)
        main.addLayout(grid)
        main.addSpacing(20)

        grid = QGridLayout()
        grid.addWidget(QLabel('Title', self), 0, 0, 1, 3)
        self.title = QLineEdit(self)
        grid.addWidget(self.title, 1, 0, 1, 3)

        grid.addWidget(QLabel('Artist', self), 2, 0, 1, 3)
        self.artist = QLineEdit(self)
        grid.addWidget(self.artist, 3, 0, 1, 3)

        grid.addWidget(QLabel('Album', self), 4, 0, 1, 3)
        self.album = QLineEdit(self)
        grid.addWidget(self.album, 5, 0, 1, 3)

        grid.addWidget(QLabel('Disc', self), 6, 0, 1, 3)
        self.disc = QLineEdit(self)
        grid.addWidget(self.disc, 7, 0, 1, 3)

        grid.addWidget(QLabel('Track', self), 8, 0, 1, 3)
        self.track = QLineEdit(self)
        grid.addWidget(self.track, 9, 0, 1, 1)
        grid.addWidget(QLabel('/', self), 9, 1, 1, 1)
        self.total = QLineEdit(self)
        grid.addWidget(self.total, 9, 2, 1, 1)

        self.cover = QLabel('cover', self)
        self.image = None
        self.pixmap = QPixmap('figure/cover.png').scaledToHeight(350)
        self.cover.setPixmap(self.pixmap)
        grid.addWidget(self.cover, 0, 3, 10, 1)
        main.addLayout(grid)
        main.addSpacing(40)

        line = QHBoxLayout()
        self.prevBtn = QPushButton('<', self)
        self.prevBtn.clicked.connect(self.showPrev)
        self.prevBtn.setEnabled(False)
        line.addWidget(self.prevBtn)
        modifyBtn = QPushButton(QIcon('figure/modify.png'), ' Modify', self)
        modifyBtn.clicked.connect(self.modifyTags)
        line.addWidget(modifyBtn)
        self.nextBtn = QPushButton('>', self)
        self.nextBtn.clicked.connect(self.showNext)
        self.nextBtn.setEnabled(False)
        line.addWidget(self.nextBtn)
        main.addLayout(line)

        self.setLayout(main)
        self.show()
        self.center()

    def center(self) -> None:
        """move widget to the center of screen"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """keyboard shortcut for searching"""
        if event.key() == Qt.Key_Return and self.search.hasFocus():
            self.searchInfo()

    def showPrev(self) -> None:
        """show previous set of tags"""
        self.page -= 1
        self.prevBtn.setEnabled(self.page != 0)
        self.nextBtn.setEnabled(True)
        self.showInfo()

    def showNext(self) -> None:
        """show next set of tags"""
        self.page += 1
        self.nextBtn.setEnabled(self.page != len(self.tracks) - 1)
        self.prevBtn.setEnabled(True)
        self.showInfo()

    def selectAudio(self) -> None:
        """select audio file from the file dialog"""
        path, _ = QFileDialog.getOpenFileName(self, 'Select an Audio File', '',
                                              'Audio Files (*.mp3)')
        if not path:
            return
        self.dir, self.file = path.rsplit('/', 1)
        self.search.setText(self.file.replace('.mp3', ''))
        self.select.setText(path)

    def searchInfo(self) -> None:
        """search tags and reset page number"""
        if not self.select.text():
            self.showMsg(False, 'Select an audio file first!')
            return
        if not self.search.text():
            self.showMsg(False, 'Query string should not be empty!')
            return

        self.tracks = search(self.search.text())
        if not self.tracks:
            self.showMsg(True, 'No results found!')
            return
        self.page = 0
        self.nextBtn.setEnabled(self.page != len(self.tracks) - 1)
        self.prevBtn.setEnabled(False)
        self.showInfo()

    def showInfo(self) -> None:
        """fill widgets with the tags of current page"""
        cur = self.tracks[self.page]
        self.image = urlopen(cur['album']['images'][0]['url']).read()
        self.pixmap.loadFromData(self.image)
        self.cover.setPixmap(self.pixmap.scaledToHeight(350))

        self.disc.setText(str(cur['disc_number']))
        self.track.setText(str(cur['track_number']))
        self.total.setText(str(cur['album']['total_tracks']))
        self.album.setText(cur['album']['name'])
        self.artist.setText(cur['artists'][0]['name'])
        self.title.setText(cur['name'])

    def modifyTags(self) -> None:
        """apply changes to ID3 tags and filename of the audio file"""
        if not self.select.text():
            self.showMsg(False, 'Select an audio file first!')
            return
        if not self.image:
            self.showMsg(False, 'Tag fields should not be empty!')
            return

        for c in self.findChildren(QLineEdit):
            if c != self.search and not c.text():
                self.showMsg(False, 'Tag fields should not be empty!')
                return

        file = eyed3.load(self.select.text())
        if not file:
            self.showMsg(False, 'Invalid file format!')
            return
        file.initTag()
        file.tag.title = self.title.text()
        file.tag.artist = self.artist.text()
        file.tag.album = self.album.text()
        file.tag.track_num = int(self.track.text()), int(self.total.text())
        file.tag.disc_num = int(self.disc.text())
        file.tag.images.set(3, self.image, 'image/jpeg')
        file.tag.save()

        path = f'{self.dir}/{escape(self.title.text())}.mp3'
        os.rename(self.select.text(), path)
        self.showMsg(True, 'ID3 tags modified!')
        self.select.setText(path)

    def showMsg(self, info: bool, msg: str) -> None:
        """show information or warning in the message box"""
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle('Information' if info else 'Warning')
        msgBox.setIcon(QMessageBox.Information if info else QMessageBox.Warning)
        msgBox.setText(msg)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName('ID3 Tag Modifier')

    font = QFont('Courier')
    font.setStyleHint(QFont.TypeWriter)
    app.setFont(font)

    widget = Widget()
    widget.setStyleSheet("""
        QPushButton { padding-left: 10px; padding-right: 10px; padding-top: 5px; padding-bottom: 5px; }
        QLabel { font-weight: bold; } 
        QLineEdit { margin-right: 5px; } 
    """)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
