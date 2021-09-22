from ui.video_player_ui import *
from tableView_Pandas_Model import PandasModel
from speech_to_text import add_keywords
from Thread_transcript import *

from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QFileDialog, QHeaderView, QMessageBox
from PyQt5.QtCore import QUrl, QSortFilterProxyModel
from PyQt5.QtGui import QPixmap, QMovie
import datetime
import time
import pandas as pd


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, app, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.app = app
        self.file_format = 'mp3'
        self.transcriptIndex = 0
        self.fileTranscripts = []

        self.videoPlayer.installEventFilter(self)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(self.videoPlayer)
        self.mediaPlayer.setVolume(50)

        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.mediaPlayer.setNotifyInterval(100)

        self.selectButton.clicked.connect(self.abrir)
        self.pauseButton.clicked.connect(self.pausar)
        self.generateButton.clicked.connect(self.generateTranscription)
        self.timeSlider.sliderMoved.connect(self.setPosition)
        self.volumeSlider.sliderMoved.connect(self.setVolume)
        self.listWidget.itemDoubleClicked.connect(self.changeVideo)
        self.checkBox.stateChanged.connect(self.changePlaybackMode)
        self.saveButton.clicked.connect(self.saveTranscript)
        self.codesButton.clicked.connect(self.insertCodes)

        self.statusBar.showMessage("Ready")

        """ PRUEBAS DE TEXTOS """
        # self.loadTableView()
        """ PRUEBAS DE TEXTOS """

    def eventFilter(self, watched, event):
        if watched == self.videoPlayer and event.type() == QtCore.QEvent.MouseButtonDblClick:
            # print("pos: ", event.pos())
            if self.videoPlayer.isFullScreen():
                self.videoPlayer.setFullScreen(False)
            else:
                self.videoPlayer.setFullScreen(True)
        return QtWidgets.QWidget.eventFilter(self, watched, event)

    def abrir(self):
        self.filenames = QFileDialog.getOpenFileNames(
            self, "Selecciona los medios", ".", "Video Files (*.mp4 *.flv *.ts *.mts *.avi)")

        if len(self.filenames[0]) != 0:
            self.listWidget.clear()
            self.playlist = QMediaPlaylist(self.mediaPlayer)
            self.playlist.currentIndexChanged.connect(self.currentIndexChanged)

            for fileName in self.filenames[0]:
                self.playlist.addMedia(QMediaContent(
                    QUrl.fromLocalFile(fileName)))
                self.listWidget.addItem(fileName)

            self.mediaPlayer.setPlaylist(self.playlist)
            self.generateButton.setEnabled(True)
            self.statusLabel.setEnabled(True)

    def pausar(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.pauseButton.setText("pause")
        else:
            self.pauseButton.setText("resume")

    def positionChanged(self, position):
        print("positionChanged triggered")
        self.timeSlider.setValue(position)
        self.currentTimeLabel.setText(
            str(datetime.timedelta(seconds=int(position/1000))))
        print(self.listWidget.currentRow())
        currentIndex = self.listWidget.currentRow()

        if self.fileTranscripts and self.fileTranscripts[currentIndex][1] == "transcript":
            try:
                while self.fileTranscripts[currentIndex][2][self.transcriptIndex][1] < position/1000:
                    text = self.textEdit.toPlainText() + " " + "<b><font color=\"red\">" + \
                        self.fileTranscripts[currentIndex][2][self.transcriptIndex][0]+"</font></b>"
                    self.textEdit.setHtml(text)
                    self.transcriptIndex += 1
                    self.textEdit.moveCursor(QtGui.QTextCursor.End)
            except:
                pass
        elif self.fileTranscripts and self.fileTranscripts[currentIndex][1] == "plain" and self.textEdit.toPlainText() == "":
            self.textEdit.setHtml(self.fileTranscripts[currentIndex][2])
            self.insertCodes()
            # self.textEdit.setPlainText(self.fileTranscripts[currentIndex][2])

    def durationChanged(self, duration):
        self.timeSlider.setRange(0, duration)
        self.durationTimeLabel.setText(
            str(datetime.timedelta(seconds=int(duration/1000))))

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def setVolume(self, volume):
        self.mediaPlayer.setVolume(volume)
        self.volValueLabel.setText(str(volume))

    def changeVideo(self, item):
        self.textEdit.clear()
        self.transcriptIndex = 0
        self.playlist.setCurrentIndex(self.listWidget.row(item))
        self.mediaPlayer.play()

    def currentIndexChanged(self, index):
        if index != -1:
            self.listWidget.setCurrentRow(index)
            self.statusBar.showMessage(self.listWidget.currentItem().text())
            self.textEdit.clear()
            self.transcriptIndex = 0

    def changePlaybackMode(self, state):
        if state == 2:
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)
        else:
            self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemOnce)

    def handleError(self):
        self.pauseButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())

    def generateTranscription(self):
        self.movie = QMovie("loader.gif")
        self.loadingLabel.setMovie(self.movie)
        self.movie.start()
        self.statusLabel.setStyleSheet(
            "QLabel {font-weight: normal;color : black;}")
        self.hilo = DynamicLoad(
            self.filenames, self.file_format)
        self.hilo.threadMessage.connect(self.onThreadMessage)
        self.hilo.generatingDone.connect(self.onGeneratingDone)
        self.hilo.start()

    def onThreadMessage(self, text):
        self.statusLabel.setText(text)
        self.statusBar.showMessage(text)

    def onGeneratingDone(self, fileTranscripts):
        self.fileTranscripts = fileTranscripts
        self.hilo.terminate()
        self.statusLabel.setStyleSheet(
            "QLabel {font-weight: bold;color: rgb(0, 221, 0);}")
        self.statusLabel.setText("Done!")
        self.statusBar.showMessage(self.listWidget.currentItem().text())
        app.processEvents()

        self.pauseButton.setEnabled(True)
        self.currentTimeLabel.setEnabled(True)
        self.timeSlider.setEnabled(True)
        self.durationTimeLabel.setEnabled(True)
        self.volumeLabel.setEnabled(True)
        self.volumeSlider.setEnabled(True)
        self.volValueLabel.setEnabled(True)
        self.listWidget.setEnabled(True)
        self.textEdit.setEnabled(True)
        self.checkBox.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.codesButton.setEnabled(True)
        self.tableView.setEnabled(True)
        self.movie.stop()
        self.loadingLabel.clear()
        self.mediaPlayer.play()

    def saveTranscript(self):
        currentIndex = self.listWidget.currentRow()

        if self.fileTranscripts[currentIndex][1] == "transcript":
            while self.transcriptIndex < len(self.fileTranscripts[currentIndex][2]):
                text = self.textEdit.toPlainText() + " " + \
                    self.fileTranscripts[currentIndex][2][self.transcriptIndex][0]
                self.textEdit.setHtml(text)
                self.transcriptIndex += 1

        text = self.textEdit.toPlainText()
        self.fileTranscripts[currentIndex][1] = "plain"
        self.fileTranscripts[currentIndex][2] = text
        text_path = "transcripts/"+self.fileTranscripts[currentIndex][0]+".txt"
        f = open(text_path, "w")
        f.write(text)
        f.close()
        self.statusLabel.setText(
            "Transcript saved to transcripts/"+self.fileTranscripts[currentIndex][0]+".txt")
        self.statusBar.showMessage(
            "Transcript saved to transcripts/"+self.fileTranscripts[currentIndex][0]+".txt")

    def insertCodes(self):
        currentIndex = self.listWidget.currentRow()

        if self.fileTranscripts[currentIndex][1] == "transcript":
            while self.transcriptIndex < len(self.fileTranscripts[currentIndex][2]):
                text = self.textEdit.toPlainText() + " " + \
                    self.fileTranscripts[currentIndex][2][self.transcriptIndex][0]
                self.textEdit.setHtml(text)
                self.transcriptIndex += 1

        text = self.textEdit.toPlainText()
        text_inserted, keywords_df = add_keywords(text)
        self.fileTranscripts[currentIndex][1] = "plain"
        self.fileTranscripts[currentIndex][2] = text_inserted
        self.textEdit.setHtml(self.fileTranscripts[currentIndex][2])

        model = PandasModel(keywords_df, header=True)
        self.tableView.setModel(model)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow(app)
    window.show()
    app.exec_()
