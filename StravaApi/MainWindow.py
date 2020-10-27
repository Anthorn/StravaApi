import sys
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QGridLayout, QWidget, QPushButton, QLineEdit \
                            , QFileSystemModel, QListView, QApplication, QTextEdit, QDialog, QGroupBox \
                            , QSizePolicy, QDialogButtonBox, QFileDialog
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import (Qt, pyqtSignal, QDir, QObject)
from StravaApi import StravaApi

class MainWindow(QObject):
    """
    Main class that is responsible for the graphical user interface.
    """

    message = pyqtSignal(str)
    login_ok = False

    def __init__(self):
        super(self).__init__()
        self.app = QApplication([])
        self.main_window = QWidget()
        self.api = StravaApi(startWithGui=True)

        self.main_window.setMinimumSize(500, 500)
        self.main_window.setWindowTitle("Strava API")
        self.api.apiMessage.connect(self.write_to_logbox, )

        # Log in --------
        user_info_layout = QHBoxLayout()
        user_info_grid_layout = QGridLayout()
        func_button_layout = QVBoxLayout()

        self.name_label = QLabel()
        self.username_label = QLabel()
        self.gender_label = QLabel()
        self.city_label = QLabel()
        self.country_label = QLabel()
        user_info_grid_layout.addWidget(QLabel("Name: "), 0, 0, Qt.AlignLeft)
        user_info_grid_layout.addWidget(self.name_label, 0, 1, Qt.AlignLeft)
        user_info_grid_layout.addWidget(QLabel("Username: "), 1, 0, Qt.AlignLeft)
        user_info_grid_layout.addWidget(self.username_label, 1, 1, Qt.AlignLeft)
        user_info_grid_layout.addWidget(QLabel("Gender: "), 2, 0, Qt.AlignLeft)
        user_info_grid_layout.addWidget(self.gender_label, 2, 1, Qt.AlignLeft)
        user_info_grid_layout.addWidget(QLabel("City: "), 3, 0, Qt.AlignLeft)
        user_info_grid_layout.addWidget(self.city_label, 3, 1, Qt.AlignLeft)
        user_info_grid_layout.addWidget(QLabel("Country: "), 4, 0, Qt.AlignLeft)
        user_info_grid_layout.addWidget(self.country_label, 4, 1, Qt.AlignLeft)

        self.client_id = QLineEdit()
        self.pass_edit = QLineEdit()

        athlete_info = QPushButton("Fetch Athlete information")
        athlete_info.clicked.connect(self.populate_athlete_labels)
        latest_run = QPushButton("Latest run")
        latest_run.clicked.connect(self.on_get_latest_activity_clicked)
        summary = QPushButton("Workout summary")
        summary.clicked.connect(self.on_summary_clicked)
        upload_activities = QPushButton("Upload Activities")
        upload_activities.clicked.connect(self.on_upload_activities_clicked)

        func_button_layout.addWidget(athlete_info)
        func_button_layout.addWidget(latest_run)
        func_button_layout.addWidget(summary)
        func_button_layout.addWidget(upload_activities)

        user_info_layout.addLayout(user_info_grid_layout)
        user_info_layout.addLayout(func_button_layout)

        self.activity_directory_input_box = QLineEdit()
        self.file_model = QFileSystemModel()
        self.file_model.setNameFilters(["*.gpx"])
        self.file_model.setNameFilterDisables(False)
        self.file_list_view = QListView()

        # Logger window --------
        logger_group_box = self.build_logger_window()

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(user_info_layout)
        self.main_layout.addWidget(logger_group_box)

        self.main_window.setLayout(self.main_layout)
        self.main_window.show()

        self.login_dialog()



    def login_dialog(self):
        try:
            dialog = QDialog()
            dialog.setWindowTitle("Strava authorization")
            layout = QVBoxLayout(dialog)
            login_group_box = self.build_credentials_box()
            layout.addWidget(login_group_box)


            url_label = QLabel()
            url_label.setText("Paste the link in an url and then use the \"code\" value in the response and paste that value in the empty box below. ")
            self.url_edit = QTextEdit()
            self.url_edit.setReadOnly(True)
            layout.addWidget(url_label)
            layout.addWidget(self.url_edit)
            login_input = QLineEdit()
            layout.addWidget(login_input)
            button = QPushButton("Ok")
            layout.addWidget(button)

            button.clicked.connect(dialog.accept)
            if(dialog.exec() == QDialog.Accepted):
                self.api.authorize(login_input.text().strip())
                self.write_to_logbox("Login successful!")
        except ValueError:
            error = sys.exc_info()[0]
            self.api.apiMessage(error)

    def build_credentials_box(self):
        login_group_box = QGroupBox("Log in")
        box_layout = QHBoxLayout()
        line_layout = QGridLayout()
        line_layout.addWidget(QLabel("Client Id: "), 0, 0)
        line_layout.addWidget(self.client_id, 0, 1)
        line_layout.addWidget(QLabel("Client Secret: "), 1, 0)
        self.pass_edit.setEchoMode(QLineEdit.Password)
        credential_button = QPushButton("Verify Credentials")
        credential_button.clicked.connect(self.on_credential_button_clicked)
        line_layout.addWidget(self.pass_edit, 1, 1)
        line_layout.addWidget(credential_button, 2, 1)

        cred_tuple = self.api.readDefaultCredentialsFromConfig()
        self.client_id.insert(str(cred_tuple[0]))
        self.pass_edit.insert(str(cred_tuple[1]))

        box_layout.addItem(line_layout)
        login_group_box.setLayout(box_layout)

        return login_group_box

    def on_credential_button_clicked(self):
        self.api.readCredentialsFromGui(self.client_id.text().strip(), self.pass_edit.text().strip())
        self.url_edit.setText(self.api.buildAuthUrl())

    def build_logger_window(self):
        logger_group_box = QGroupBox("Log")

        self.logBox = QTextEdit()
        self.logBox.setMinimumSize(150, 300)
        self.logBox.setReadOnly(True)
        self.logBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bottom_line_layout = QVBoxLayout()
        bottom_line_layout.addWidget(self.logBox, Qt.AlignBottom)
        logger_group_box.setLayout(bottom_line_layout)
        self.message.connect(self.write_to_logbox)

        return logger_group_box


    def write_to_logbox(self, message):
        self.logBox.moveCursor(QTextCursor.End)
        self.logBox.insertPlainText(message + "\n")
        self.logBox.moveCursor(QTextCursor.End)

    def populate_athlete_labels(self):
        athlete_info = self.api.currentAthlete()
        self.name_label.setText(athlete_info.name)
        self.username_label.setText(athlete_info.username)
        self.gender_label.setText(athlete_info.gender)
        self.city_label.setText(athlete_info.city)
        self.country_label.setText(athlete_info.country)

    def on_summary_clicked(self):
        self.api.athleteSummary()

    def on_get_latest_activity_clicked(self):
        self.api.getLatestActivity()

    def on_upload_activities_clicked(self):
        dialog = QDialog()
        box = QDialogButtonBox(dialog)
        box.addButton("Upload", QDialogButtonBox.AcceptRole)
        box.addButton("Cancel", QDialogButtonBox.RejectRole)

        box.accepted.connect(dialog.accept)
        box.rejected.connect(dialog.reject)
        dialog.setMinimumSize(500, 500)
        dialog.setWindowTitle("Upload Activities")
        layout = QVBoxLayout()
        input_layout = QHBoxLayout()

        label = QLabel("Location: ")
        input_push_button = QPushButton("...")
        input_push_button.setMaximumWidth(30)
        input_layout.addWidget(label, Qt.AlignLeft)
        input_layout.addWidget(self.activity_directory_input_box, Qt.AlignLeft)
        input_layout.addWidget(input_push_button, Qt.AlignRight)

        input_push_button.clicked.connect(self.open_activity_directory_selection_dialog)

        layout.addLayout(input_layout)

        self.file_list_view.setModel(self.file_model)
        self.file_list_view.setRootIndex(self.file_model.index(QDir.currentPath()))

        layout.addWidget(self.file_list_view)
        layout.addWidget(box)

        dialog.setLayout(layout)

        conclusion = dialog.exec()

        if conclusion == QDialog.Accepted:
            self.api.uploadActivitiesFromDirectory(self.file_model.rootPath())

    def activity_dir_selected(self, directoryStr, model):
        model.setRootPath(directoryStr)

    def open_activity_directory_selection_dialog(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dirPath = dialog.getExistingDirectory()

        self.file_model.setRootPath(dirPath)
        self.file_list_view.setRootIndex(self.file_model.index(dirPath))
        self.activity_directory_input_box.setText(dirPath)

    def start_gui(self):
        self.app.exec_()

