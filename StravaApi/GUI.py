from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import (Qt, pyqtSignal)
from StravaApi import *
import sys

class GUI(QObject):

    message = pyqtSignal(str)

    def __init__(self):
        super(QObject,self).__init__()
        self.app = QApplication([])
        self.mainWindow = QWidget()
        self.api = StravaApi(startWithGui=True)

        self.mainWindow.setMinimumSize(500,500)
        self.mainWindow.setWindowTitle("Strava API")
        self.api.apiMessage.connect(self.writeToLogBox)

        # Log in --------
        userInfoLayout = QVBoxLayout()
        userInfoLayout.addWidget(QLabel("User info goes here"), Qt.AlignLeft)


        # Logger window --------
        loggerGroupBox = self.buildLoggerWindow()

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(userInfoLayout)
        self.mainLayout.addWidget(loggerGroupBox)

        self.mainWindow.setLayout(self.mainLayout)
        self.mainWindow.show()

        try:
            dialog = QDialog()
            dialog.setWindowTitle("Strava authorization")
            layout = QVBoxLayout(dialog)
            logInGroupBox = self.buildCredentialsBox()
            layout.addWidget(logInGroupBox)


            urlLabel = QLabel()
            urlLabel.setText("Paste the link in an url and then use the \"code\" value in the response and paste that value in the empty box below. ")
            self.urlEdit = QTextEdit()
            self.urlEdit.setReadOnly(True)
            layout.addWidget(urlLabel)
            layout.addWidget(self.urlEdit)
            input = QLineEdit()
            layout.addWidget(input)
            button = QPushButton("Ok")
            layout.addWidget(button)

            button.clicked.connect(dialog.accept)
            if(dialog.exec() == QDialog.Accepted):
                self.api.authorize(input.text().strip())
                self.writeToLogBox("Login successful!")
                self.api.checkUser()
        except:
            error = sys.exc_info()[0]

    def buildCredentialsBox(self):
        logInGroupBox = QGroupBox("Log in")
        boxLayout = QHBoxLayout()
        lineLayout = QGridLayout()
        self.clientId = QLineEdit()
        lineLayout.addWidget(QLabel("Client Id: "), 0,0)
        lineLayout.addWidget(self.clientId, 0,1)
        lineLayout.addWidget(QLabel("Client Secret: "), 1,0)
        self.passEdit = QLineEdit()
        self.passEdit.setEchoMode(QLineEdit.Password)
        credentialButton = QPushButton("Verify Credentials")
        lineLayout.addWidget(self.passEdit, 1,1)
        lineLayout.addWidget(credentialButton, 2, 1)

        credentialButton.clicked.connect(self.onCredentialButtonClicked)
        boxLayout.addItem(lineLayout)
        logInGroupBox.setLayout(boxLayout)

        return logInGroupBox

    def onCredentialButtonClicked(self):
        self.api.readCredentialsFromGui(self.clientId.text().strip(), self.passEdit.text().strip())
        self.urlEdit.setText(self.api.buildAuthUrl())

    def buildLoggerWindow(self):
        loggerGroupBox = QGroupBox("Log")

        self.logBox = QTextEdit()
        self.logBox.setMinimumSize(150,300)
        self.logBox.setReadOnly(True)
        self.logBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bottomLineLayout = QVBoxLayout()
        bottomLineLayout.addWidget(self.logBox, Qt.AlignBottom )
        loggerGroupBox.setLayout(bottomLineLayout)
        self.message.connect(self.writeToLogBox)

        return loggerGroupBox


    def writeToLogBox(self, message):
        self.logBox.moveCursor(QTextCursor.End)
        self.logBox.insertPlainText(message + "\n")
        self.logBox.moveCursor(QTextCursor.End)

    def startGui(self):
        self.app.exec_()

