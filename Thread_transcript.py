from speech_to_text import *
from PyQt5.QtCore import QThread, pyqtSignal
import time
import os


class DynamicLoad(QThread):
    threadMessage = pyqtSignal(str)
    generatingDone = pyqtSignal(list)

    def __init__(self, filenames, file_format):
        super().__init__()
        self.filenames = filenames
        self.file_format = file_format
        self.fileTranscripts = []

    def run(self):
        for fileName in self.filenames[0]:
            name = fileName.split(".")
            name = name[0].split("/")
            audio_path = "audios/"+name[-1]+"."+self.file_format

            try:
                filetext = open("transcripts/"+name[-1]+".txt")
                self.fileTranscripts.append(
                    [name[-1], "plain", filetext.read()])
                filetext.close()

            except IOError:
                self.threadMessage.emit("getting audio from "+name[-1])
                transform_video_to_audio(fileName, audio_path)
                self.threadMessage.emit(
                    "generating transcription from "+name[-1])
                transcript = speech_to_text_converter(audio=open(audio_path, 'rb').read(),
                                                      headers={'Content-Type': f'audio/{self.file_format}'})
                os.remove(audio_path)
                self.fileTranscripts.append(
                    [name[-1], "transcript", transcript])

        self.generatingDone.emit(self.fileTranscripts)
