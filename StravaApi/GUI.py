from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import (Qt, pyqtSignal)
from StravaApi import *
import sys

class GUI(QObject):

    message = pyqtSignal(str)
    loginOk = False

    def __init__(self):
        super(QObject,self).__init__()
        self.app = QApplication([])
        self.mainWindow = QWidget()
        self.api = StravaApi(startWithGui=True)

        self.mainWindow.setMinimumSize(500,500)
        self.mainWindow.setWindowTitle("Strava API")
        self.api.apiMessage.connect(self.writeToLogBox)

        # Log in --------
        userInfoLayout = QHBoxLayout()
        userInfoGridLayout = QGridLayout()
        funcButtonLayout = QVBoxLayout()

        self.nameLabel = QLabel()
        self.usernameLabel = QLabel()
        self.genderLabel = QLabel()
        self.cityLabel = QLabel()
        self.countryLabel = QLabel()
        userInfoGridLayout.addWidget(QLabel("Name: "), 0, 0, Qt.AlignLeft)
        userInfoGridLayout.addWidget(self.nameLabel, 0, 1, Qt.AlignLeft)
        userInfoGridLayout.addWidget(QLabel("Username: "), 1, 0, Qt.AlignLeft)
        userInfoGridLayout.addWidget(self.usernameLabel, 1, 1, Qt.AlignLeft)
        userInfoGridLayout.addWidget(QLabel("Gender: "), 2, 0, Qt.AlignLeft)
        userInfoGridLayout.addWidget(self.genderLabel, 2, 1, Qt.AlignLeft)
        userInfoGridLayout.addWidget(QLabel("City: "), 3, 0, Qt.AlignLeft)
        userInfoGridLayout.addWidget(self.cityLabel, 3, 1, Qt.AlignLeft)
        userInfoGridLayout.addWidget(QLabel("Country: "), 4, 0, Qt.AlignLeft)
        userInfoGridLayout.addWidget(self.countryLabel, 4, 1, Qt.AlignLeft)

        athleteInfo = QPushButton("Fetch Athlete information")
        athleteInfo.clicked.connect(self.populateAthleteLabels)
        latestRun = QPushButton("Latest run")
        latestRun.clicked.connect(self.onGetLatestActivityClicked)
        summary = QPushButton("Workout summary")
        summary.clicked.connect(self.onSummaryClicked)
        uploadActivities = QPushButton("Upload Activities")
        uploadActivities.clicked.connect(self.onUploadActivitiesClicked)

        funcButtonLayout.addWidget(athleteInfo)
        funcButtonLayout.addWidget(latestRun)
        funcButtonLayout.addWidget(summary)
        funcButtonLayout.addWidget(uploadActivities)

        userInfoLayout.addLayout(userInfoGridLayout)
        userInfoLayout.addLayout(funcButtonLayout)

        self.activityDirectoryInputBox = QLineEdit()
        self.fileModel = QFileSystemModel()
        self.fileModel.setNameFilters(["*.gpx"])
        self.fileModel.setNameFilterDisables(False)
        self.fileListView = QListView()

        # Logger window --------
        loggerGroupBox = self.buildLoggerWindow()

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(userInfoLayout)
        self.mainLayout.addWidget(loggerGroupBox)

        self.mainWindow.setLayout(self.mainLayout)
        self.mainWindow.show()

        self.loginDialog()



    def loginDialog(self):
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
                loginOk = self.api.checkUser()
        except:
            error = sys.exc_info()[0]

    def buildCredentialsBox(self):
        logInGroupBox = QGroupBox("Log in")
        boxLayout = QHBoxLayout()
        lineLayout = QGridLayout()
        self.clientId = QLineEdit()
        lineLayout.addWidget(QLabel("Client Id: "), 0, 0)
        lineLayout.addWidget(self.clientId, 0,1)
        lineLayout.addWidget(QLabel("Client Secret: "), 1, 0)
        self.passEdit = QLineEdit()
        self.passEdit.setEchoMode(QLineEdit.Password)
        credentialButton = QPushButton("Verify Credentials")
        credentialButton.clicked.connect(self.onCredentialButtonClicked)
        lineLayout.addWidget(self.passEdit, 1, 1)
        lineLayout.addWidget(credentialButton, 2, 1)

        credTuple = self.api.readDefaultCredentialsFromConfig()
        self.clientId.insert(str(credTuple[0]))
        self.passEdit.insert(str(credTuple[1]))

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

    def populateAthleteLabels(self):
        athleteInfo = self.api.currentAthlete()
        self.nameLabel.setText(athleteInfo.name)
        self.usernameLabel.setText(athleteInfo.username)
        self.genderLabel.setText(athleteInfo.gender)
        self.cityLabel.setText(athleteInfo.city)
        self.countryLabel.setText(athleteInfo.country)

    def onSummaryClicked(self):
        self.api.athleteSummary()

    def onGetLatestActivityClicked(self):
        self.api.getLatestActivity()

    def onUploadActivitiesClicked(self):
        startUploadButton = QPushButton("Upload")
        dialog = QDialog()
        box = QDialogButtonBox(dialog)
        box.addButton("Upload", QDialogButtonBox.AcceptRole)
        box.addButton("Cancel", QDialogButtonBox.RejectRole)

        box.accepted.connect(dialog.accept)
        box.rejected.connect(dialog.reject)
        dialog.setMinimumSize(500, 500)
        dialog.setWindowTitle("Upload Activities")
        layout = QVBoxLayout()
        inputLayout = QHBoxLayout()

        label = QLabel("Location: ")
        inputPushButton = QPushButton("...")
        inputPushButton.setMaximumWidth(30)
        inputLayout.addWidget(label, Qt.AlignLeft)
        inputLayout.addWidget(self.activityDirectoryInputBox, Qt.AlignLeft)
        inputLayout.addWidget(inputPushButton, Qt.AlignRight)

        inputPushButton.clicked.connect(self.openActivityDirectorySelectionDialog)

        layout.addLayout(inputLayout)

        self.fileListView.setModel(self.fileModel)
        self.fileListView.setRootIndex(self.fileModel.index(QDir.currentPath()))

        layout.addWidget(self.fileListView)
        layout.addWidget(box)

        dialog.setLayout(layout)

        conclusion = dialog.exec()

        if conclusion == QDialog.Accepted:
            self.api.uploadActivitiesFromDirectory(self.fileModel.rootPath())



    def activityDirSelected(self, directoryStr, model):
        model.setRootPath(directoryStr)

    def openActivityDirectorySelectionDialog(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dirPath = dialog.getExistingDirectory()

        self.fileModel.setRootPath(dirPath)
        self.fileListView.setRootIndex(self.fileModel.index(dirPath))
        self.activityDirectoryInputBox.setText(dirPath)



    def startGui(self):
        self.app.exec_()

