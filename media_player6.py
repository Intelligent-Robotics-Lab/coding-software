import sys
from typing import Sized
from PyQt5.QtWidgets import (
    QComboBox,
    QErrorMessage,
    QHBoxLayout,
    QApplication,
    QButtonGroup,
    QInputDialog,
    QLabel,
    QLayout,
    QDesktopWidget,
    QTableView,
    QHeaderView,
    QAbstractScrollArea
)
from PyQt5.QtWidgets import (
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QGridLayout,
    QFileDialog,
    QMessageBox,
    QDialog,
    QInputDialog,
    QDialogButtonBox,
    QFormLayout
)
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QCursor, QKeyEvent
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl
import os
from numpy import VisibleDeprecationWarning, e
import pandas as pd
import bisect
from pandas.api.types import is_numeric_dtype

# lel
# helper function ms to minutes:seconds
# test comment for madeline


def ms_fix(ms):
    seconds = (ms / 1000) % 60
    seconds = int(seconds)
    minutes = (ms / (1000 * 60)) % 60
    minutes = int(minutes)

    if seconds < 10:
        return "{}:0{}".format(minutes, seconds)
    else:
        return "{}:{}".format(minutes, seconds)


class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(600, 250)
        self.setWindowTitle("Naming of exported compliance file")
        self.label_file_name = QLabel("Name of File:")
        self.file_name = QLineEdit("Enter file name")
        self.label_dir_name = QLabel("Directory for File:")
        self.dir_name = QLineEdit("Save folder name")
        self.file_browse = QPushButton("Browse")
        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QVBoxLayout(self)
        # Row for file name
        h_layout_file_name = QHBoxLayout()
        h_layout_file_name.addWidget(self.label_file_name)
        h_layout_file_name.addWidget(self.file_name)
        # Row for directory name
        h_layout_dir_name = QHBoxLayout()
        h_layout_dir_name.addWidget(self.label_dir_name)
        h_layout_dir_name.addWidget(self.dir_name)
        h_layout_dir_name.addWidget(self.file_browse)

        layout.addLayout(h_layout_file_name)
        layout.addLayout(h_layout_dir_name)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.file_browse.clicked.connect(self.find_dir)

    def accept(self):
        try:
            df = pd.DataFrame(c_list, columns=[
                'Time Start', 'Time End', 'Label'])
            if not df.empty:
                df.sort_values(by='Time Start', inplace=True)
            file_name = str(self.dir_name.text()) + '/' + \
                str(self.file_name.text()) + '.csv'
            df.to_csv(
                file_name, index=False, header=True)
            print(df)
            self.close()
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(
                "Error saving file. Please check file name or save directory")
            msg.setWindowTitle("Error")
            msg.exec_()

    def find_dir(self):
        dir_name = str(QFileDialog.getExistingDirectory(
            self, 'Select Directory', options=QFileDialog.DontUseNativeDialog))
        if dir_name:
            self.dir_name.setText(dir_name)
# main window


class media_player(QWidget):
    def __init__(self):
        super().__init__()

        # window size and name
        self.setWindowTitle("Media Player")
        self.resize(600, 270)

        # flag for updater
        self.flagUpdate = False

        # creating widgts
        self.slider = QSlider()
        self.txtBox = QLineEdit()
        self.sliderEdit = QLineEdit()
        self.fileSelect = QPushButton()
        self.nextPage = QPushButton()
        self.cMetrics = QComboBox()
        self.hotKey = QPushButton("HotKey Setup")
        self.sliderLabel = QLabel()

        # Setting up file dialog
        self.videoFile = QFileDialog()

        # creating variables for global use
        self.data = ""
        self.sliderSize = ""
        self.comboList = []
        self.behavior = "test"

        # creating window inst for hotkey
        self.valueHK = hotKeyBinding()

        # makes sure we have default HK values
        # attributes of each instance defaultHK#
        self.defaultHK1 = self.valueHK.HKpass1
        self.defaultHK2 = self.valueHK.HKpass2
        self.defaultHK3 = self.valueHK.HKpass3
        self.defaultHK4 = self.valueHK.HKpass4

        # make default Label values
        self.Ltext1 = self.valueHK.HKpass1
        self.Ltext2 = self.valueHK.HKpass2
        self.Ltext3 = self.valueHK.HKpass3
        self.Ltext4 = self.valueHK.HKpass4

        # update combo textbox on open
        # self.ComboTextRead()
        # calling next frame
        self.frame1()

    def frame1(self):
        # grid layout
        grid = QVBoxLayout()
        outer_layout = QHBoxLayout()
        top_layout = QHBoxLayout()
        modes_hotkeys = QHBoxLayout()
        self.setLayout(grid)

        # Adding labels
        self.cMetrics.addItem("Engagement")
        self.cMetrics.addItem("Affect")
        self.cMetrics.addItem("Communication")
        self.cMetrics.addItem("Compliance")
        self.cMetrics.addItem("Performance")

        # setup slider
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setRange(5, 30)
        self.slider.setSingleStep(1)
        self.slider.setValue(10)
        self.sliderEdit.setText(str(10))
        self.sliderLabel.setText("Interval: ")

        # setup txtbox/nextPage
        self.txtBox.setText("Select A file")
        self.fileSelect.setText("Browse")
        self.nextPage.setText("Continue")

        # setting up cursor hover
        self.fileSelect.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.nextPage.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.cMetrics.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.hotKey.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # adding widgets to layouts for grid
        outer_layout.addWidget(self.txtBox)
        outer_layout.addWidget(self.fileSelect)

        # modes and hotkey layout
        modes_hotkeys.addWidget(self.cMetrics)
        modes_hotkeys.addWidget(self.hotKey)

        # slider layout
        top_layout.addWidget(self.sliderLabel)
        top_layout.addWidget(self.slider)
        top_layout.addWidget(self.sliderEdit)

        # adding grid layouts
        grid.addLayout(modes_hotkeys)
        grid.addLayout(outer_layout)
        grid.addLayout(top_layout)

        # continue button
        grid.addWidget(self.nextPage)

        # connect slider to textbox
        self.slider.valueChanged.connect(self.changeInValue)

        # connect fileselect and the file explore
        self.fileSelect.clicked.connect(self.fileExplore)

        # continue
        self.nextPage.clicked.connect(self.on_continue_clicked)

        # showing hotkey window on press
        self.hotKey.clicked.connect(self.on_hotkey_clicked)

        # Detects when value of combobox is changed
        self.cMetrics.currentTextChanged.connect(self.changed_text)

    # Change in text of combobox
    def changed_text(self):
        if str(self.cMetrics.currentText()) == 'Compliance':
            self.hotKey.setEnabled(False)
        else:
            self.hotKey.setEnabled(True)

    # slider value
    def changeInValue(self):
        self.sliderEdit.setText(str(self.slider.value()))

    # file selector
    def fileExplore(self):
        self.filename, _ = QFileDialog.getOpenFileName(
            self, "Open Video", filter="video (*.mp4)", options=QFileDialog.DontUseNativeDialog
        )
        self.txtBox.setText(self.filename)
        self.data = self.filename

    # this updates values if the default ones arent wanted. comes from hotkey class
    def defaultUpdater(self, HKpass1, HKpass2, HKpass3, HKpass4):
        self.defaultHK1 = HKpass1
        self.defaultHK2 = HKpass2
        self.defaultHK3 = HKpass3
        self.defaultHK4 = HKpass4

    # passes label names to main window from the hotkey class
    def LtxtGrab(self, Ltxt1, Ltxt2, Ltxt3, Ltxt4):
        self.Ltext1 = Ltxt1
        self.Ltext2 = Ltxt2
        self.Ltext3 = Ltxt3
        self.Ltext4 = Ltxt4

    # function to swap pages, brings up media player

    def on_continue_clicked(self):

        self.dialog = video_player(self.data, self.slider.value(), self.defaultHK1, self.defaultHK2,
                                   self.defaultHK3, self.defaultHK4, self.Ltext1, self.Ltext2, self.Ltext3, self.Ltext4, self.behavior, str(self.cMetrics.currentText()))

        self.dialog.show()

    # pass to hotey setting class
    def on_hotkey_clicked(self):
        self.valueHK.show()


class hotKeyBinding(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hotkey Settings")
        self.setGeometry(100, 100, 250, 100)
        self.center()

        # default values for hotkeys
        self.HKpass1 = "q"
        self.HKpass2 = "w"
        self.HKpass3 = "e"
        self.HKpass4 = "r"

        self.init_ui()

    def init_ui(self):
        # creating layout
        coreLayout = QVBoxLayout()
        btnLayout1 = QHBoxLayout()
        btnLayout2 = QHBoxLayout()
        btnLayout3 = QHBoxLayout()
        btnLayout4 = QHBoxLayout()

        coreLayout.addLayout(btnLayout1)
        coreLayout.addLayout(btnLayout2)
        coreLayout.addLayout(btnLayout3)
        coreLayout.addLayout(btnLayout4)

        self.setLayout(coreLayout)

        # creating flag for HK and label
        self.HKflag = -1
        self.labelFlag = -1

        # Qbuttons and labels for layout
        self.HKNum1 = QLabel("1.")
        self.HK1 = QPushButton("q")
        self.btnTxt1 = QLineEdit("Label 1")
        self.btnTxt1.setPlaceholderText("label name")

        self.HKNum2 = QLabel("2.")
        self.HK2 = QPushButton("w")
        self.btnTxt2 = QLineEdit("Label 2")
        self.btnTxt2.setPlaceholderText("label name")

        self.HKNum3 = QLabel("3.")
        self.HK3 = QPushButton("e")
        self.btnTxt3 = QLineEdit("Label 3")
        self.btnTxt3.setPlaceholderText("label name")

        self.HKNum4 = QLabel("4.")
        self.HK4 = QPushButton("r")
        self.btnTxt4 = QLineEdit("Label 4")
        self.btnTxt4.setPlaceholderText("label name")

        self.HKsave = QPushButton("save and exit")

        # connection
        self.HKsave.clicked.connect(self.HKSavenClose)

        # adding widgets
        btnLayout1.addWidget(self.HK1)
        btnLayout1.addWidget(self.btnTxt1)

        btnLayout2.addWidget(self.HK2)
        btnLayout2.addWidget(self.btnTxt2)

        btnLayout3.addWidget(self.HK3)
        btnLayout3.addWidget(self.btnTxt3)

        btnLayout4.addWidget(self.HK4)
        btnLayout4.addWidget(self.btnTxt4)

        coreLayout.addWidget(self.HKsave)

        # connect clicked with flags to stop multiple inputs on hotkey
        self.HK1.clicked.connect(self.HK1Clicked)
        self.HK2.clicked.connect(self.HK2Clicked)
        self.HK3.clicked.connect(self.HK3Clicked)
        self.HK4.clicked.connect(self.HK4Clicked)

    # Method for centering window
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # sets flag back to -1 and does hotkey setup
    def keyPressEvent(self, event: QEvent):
        if self.HKflag == 1:
            self.HK1.setText(event.text())
            self.HKpass1 = self.HK1.text()
            self.HKflag = -1

        elif self.HKflag == 2:
            self.HK2.setText(event.text())
            self.HKpass2 = self.HK2.text()
            self.HKflag = -1

        elif self.HKflag == 3:
            self.HK3.setText(event.text())
            self.HKpass3 = self.HK3.text()
            self.HKflag = -1

        elif self.HKflag == 4:
            self.HK4.setText(event.text())
            self.HKpass4 = self.HK4.text()
            self.HKflag = -1

    # hotkey flag
    def HK1Clicked(self):
        self.HKflag = 1

    def HK2Clicked(self):
        self.HKflag = 2

    def HK3Clicked(self):
        self.HKflag = 3

    def HK4Clicked(self):
        self.HKflag = 4

    # pass updated HK back to main class
    def HKSavenClose(self):
        window.defaultUpdater(self.HKpass1, self.HKpass2,
                              self.HKpass3, self.HKpass4)
        self.Ltxt1 = self.btnTxt1.text()
        self.Ltxt2 = self.btnTxt2.text()
        self.Ltxt3 = self.btnTxt3.text()
        self.Ltxt4 = self.btnTxt4.text()
        window.LtxtGrab(self.Ltxt1, self.Ltxt2, self.Ltxt3, self.Ltxt4)
        self.close()

    # pass updated HK txt to main class
    def HKsavenClose(self):
        window.defaultTxtUpdater()


# start of video player class
class video_player(QWidget):
    def __init__(self, data, sliderSize, hk1, hk2, hk3, hk4, L1, L2, L3, L4, behavior, metric):
        super().__init__()

        # sets the label
        self.metric = metric
        # List to hold compliance times pressed and released
        self.compliance_list = []
        self.compliance_time_pts = []
        # data for the file name
        self.data = data
        self.behavior = behavior
        self.completeList = []
        self.completeList.append(
            ['Key Pressed', 'Key Released', 'Label', 'Interval'])

        # this flag is so we can tell if the video is ready to be paused
        self.pauseFlag = True
        # data for the slider length
        self.sliderSize = int(sliderSize)

        self.setWindowTitle("Media Player")
        self.resize(900, 700)
        self.center()
        # save hk values
        self.HK1 = hk1
        self.HK2 = hk2
        self.HK3 = hk3
        self.HK4 = hk4

        # Label names
        self.L1 = L1
        self.L2 = L2
        self.L3 = L3
        self.L4 = L4

        # flag for key press events
        self.iskeyPressed = False
        self.keyPressed = ""

        self.init_ui()
        self.show()

    def init_ui(self):

        # counter for freq
        self.frequencyCounter = []
        self.interval_list = []

        # create media player object
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # speed up the notify rate
        self.mediaPlayer.setNotifyInterval(1)

        # Tells if video is running or not
        self.videoFlag = False

        # create videowidget object
        videowidget = QVideoWidget()

        self.setFile()

        # Create label for video position
        self.label = QLabel(
            ms_fix(self.mediaPlayer.duration()) + '/' + ms_fix(self.mediaPlayer.duration()))
        self.label.setAlignment(Qt.AlignCenter)

        # create play button
        playBtn = QPushButton("Play")
        playBtn.setMaximumWidth(80)
        playBtn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        playBtn.clicked.connect(self.play_video)

        # create pause button
        pauseBtn = QPushButton("Pause")
        pauseBtn.setMaximumWidth(80)
        pauseBtn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        pauseBtn.clicked.connect(self.pause_video)

        # create pause button
        end_collect = QPushButton("End Data")
        end_collect.setMaximumWidth(80)
        end_collect.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        end_collect.clicked.connect(self.collect_end)

        # Save data button prints output to terminal just in case the program crashes
        # save_button = QPushButton("Save Data")
        # save_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        # save_button.clicked.connect(self.save_data)

        # Text box for entering in start and end intervals for data collection
        self.start_interval_text = QLabel('Start Int')
        self.start_interval_input = QLineEdit()
        self.start_interval_input.setMaximumWidth(30)
        self.end_interval_text = QLabel('End Int')
        self.end_interval_input = QLineEdit()
        self.end_interval_input.setMaximumWidth(30)

        # If compliance is the metric add start compliance and end compliance buttons
        self.start_comp_button = QPushButton("Start Comp")
        self.start_comp_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        # When press start comp gets the time of button press
        self.start_comp_button.setEnabled(False)
        self.start_comp_button.clicked.connect(self.get_start_time)

        self.end_comp_button = QPushButton("End Comp")
        self.end_comp_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        # When press end comp button completes data point
        self.end_comp_button.setEnabled(False)
        self.end_comp_button.clicked.connect(self.get_end_time)

        # Add show data button for compliance
        self.show_compliance_data = QPushButton("Show Data")
        self.show_compliance_data.setCursor(
            QCursor(QtCore.Qt.PointingHandCursor))
        self.show_compliance_data.clicked.connect(self.show_comp_data)

        # Add save data button for compliance
        self.save_compliance_data = QPushButton("Save Data")
        self.save_compliance_data.setCursor(
            QCursor(QtCore.Qt.PointingHandCursor))
        self.save_compliance_data.clicked.connect(self.save_comp_data)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.interval_label = QLabel()
        vboxLayout_labels = QVBoxLayout()
        vboxLayout_labels.addWidget(self.label)
        vboxLayout_labels.addWidget(self.interval_label)
        # create hbox layout
        hboxLayout = QHBoxLayout()
        hboxLayout_buttons = QHBoxLayout()
        hboxLayout.setContentsMargins(0, 0, 0, 0)

        # create vbox layout
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(videowidget)
        hboxLayout.addLayout(vboxLayout_labels)
        hboxLayout.addWidget(self.positionSlider)
        # Setting video player layout for different metrics
        if self.metric == 'Compliance':
            hboxLayout_buttons.addWidget(playBtn)
            hboxLayout_buttons.addWidget(pauseBtn)
            hboxLayout_buttons.addWidget(self.show_compliance_data)
            hboxLayout_buttons.addWidget(self.save_compliance_data)
            hboxLayout_buttons.addWidget(self.start_comp_button)
            hboxLayout_buttons.addWidget(self.end_comp_button)
            vboxLayout.addLayout(hboxLayout)
            vboxLayout.addLayout(hboxLayout_buttons)
        else:
            hboxLayout.addWidget(playBtn)
            hboxLayout.addWidget(pauseBtn)
            hboxLayout.addWidget(end_collect)
            hboxLayout.addWidget(self.start_interval_text)
            hboxLayout.addWidget(self.start_interval_input)
            hboxLayout.addWidget(self.end_interval_text)
            hboxLayout.addWidget(self.end_interval_input)
            vboxLayout.addLayout(hboxLayout)
        # else:
        #     hboxLayout.addWidget(playBtn)
        #     hboxLayout.addWidget(pauseBtn)
        #     hboxLayout.addWidget(end_collect)
        #     # hboxLayout.addWidget(save_button)
        #     vboxLayout.addLayout(hboxLayout)

        self.setLayout(vboxLayout)

        # set up signal
        self.mediaPlayer.positionChanged.connect(self.sliderTimer)

        self.mediaPlayer.setVideoOutput(videowidget)

        self.mediaPlayer.positionChanged.connect(self.positionChanged)

        self.mediaPlayer.durationChanged.connect(self.interval_calc)

        self.mediaPlayer.durationChanged.connect(self.durationChanged)

        # When press end comp gets time and popup
        # self.start_comp_button.clicked.connect(self.)
    # Slot for saving compliance data

    # End of data collection button
    def collect_end(self):
        self.mediaPlayer.pause()
        self.promptEnd()

    def save_comp_data(self):
        self.pause_video()
        global c_list
        c_list = self.compliance_list  # set global variable to self.compliance_list
        dialog = InputDialog()
        dialog.exec_()

    # Slot for showing compliance data
    def show_comp_data(self):
        self.pause_video()
        df = pd.DataFrame(self.compliance_list, columns=[
                          'Time Start', 'Time End', 'Label'])
        if not df.empty:
            df.sort_values(by='Time Start', inplace=True)
        data = df.values.tolist()
        model_table_values = TableModel(data)
        self.tableWidget_values = QTableView()
        self.tableWidget_values.horizontalHeader(
        ).setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableWidget_values.setModel(model_table_values)
        self.tableWidget_values.setWindowTitle('Coded Values')
        self.tableWidget_values.resize(600, 600)
        self.tableWidget_values.show()

    # Gets value of video when button is pressed

    def get_start_time(self):
        self.compliance_time_pts.append(self.mediaPlayer.position()/1000)
        self.start_comp_button.setEnabled(False)
        self.end_comp_button.setEnabled(True)

    def get_end_time(self):
        self.pause_video()
        self.compliance_time_pts.append(self.mediaPlayer.position()/1000)
        labels = ['Compliant', 'Noncompliant', 'Anticipated']
        label, ok = QInputDialog().getItem(
            self, 'Label Compliancy', 'Please Select Label Name of Interval:', labels, current=0, editable=False)
        if label and ok:
            self.compliance_time_pts.append(label)
            self.compliance_list.append(self.compliance_time_pts)
            self.compliance_time_pts = []
        else:
            self.compliance_time_pts = []

        print(self.compliance_list)
        # self.start_comp_button.setEnabled(True)
        self.end_comp_button.setEnabled(False)

    # Function saves outputs data to terminal to prevent data loss if program crashes
    # def save_data(self):
    #     try:
    #         cwd = os.getcwd() + '\\' + 'saved_data'
    #         print(cwd)
    #         df = pd.DataFrame(
    #             self.completeList[1:], columns=self.completeList[0])
    #         df.to_csv(cwd, index=False, header=True)
    #         print(df)
    #     except:
    #         error_dialog = QErrorMessage()
    #         error_dialog.showMessage('Problem saving, try again please')
    #         error_dialog.exec_()
    #         print('error')

    # changes duration of content to duration param

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
        self.positionSlider.setStyleSheet(
            '''
            QSlider::groove:horizontal {
border: 1px solid #bbb;
background: white;
height: 10px;
border-radius: 4px;
}

QSlider::sub-page:horizontal {
background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
    stop: 0 #66e, stop: 1 #bbf);
background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
    stop: 0 #bbf, stop: 1 #55f);
border: 1px solid #777;
height: 10px;
border-radius: 4px;
}

QSlider::add-page:horizontal {
background: #fff;
border: 1px solid #777;
height: 10px;
border-radius: 4px;
}

QSlider::handle:horizontal {
background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #eee, stop:1 #ccc);
border: 1px solid #777;
width: 13px;
margin-top: -6px;
margin-bottom: -6px;
border-radius: 4px;
}

QSlider::handle:horizontal:hover {
background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #fff, stop:1 #ddd);
border: 1px solid #444;
border-radius: 4px;
}

QSlider::sub-page:horizontal:disabled {
background: #bbb;
border-color: #999;
}

QSlider::add-page:horizontal:disabled {
background: #eee;
border-color: #999;
}

QSlider::handle:horizontal:disabled {
background: #eee;
border: 1px solid #aaa;
border-radius: 4px;
}
            '''
        )

    def interval_calc(self, duration):
        for i in range(0, duration, self.sliderSize*1000):
            self.interval_list.append(i)
        self.interval_list.append(duration)
        self.interval_label.setText(
            'Interval:' + '0/' + str(len(self.interval_list)-1))
        # print(len(self.interval_list))

    def positionChanged(self, position):
        # Time is in milliseconds
        self.positionSlider.setValue(position)
        self.label.setText(ms_fix(position) + '/' +
                           ms_fix(self.mediaPlayer.duration()))
        internal_int_list = self.interval_list
        bisect.insort(internal_int_list, position)
        interval = internal_int_list.index(position)
        self.interval_label.setText(
            'Interval:' + str(interval) + '/' + str(len(self.interval_list)-2))
        internal_int_list.pop(interval)

    # Sets the time of the timer

    def setPosition(self, position):
        self.label.setText(ms_fix(position) + '/' +
                           ms_fix(self.mediaPlayer.duration()))
        self.mediaPlayer.setPosition(position)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        self.pause_video()
        event.accept()  # let the window close

    # not fully sure but is in all Qmedia code i find
    def setFile(self):
        if self.data != "":
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(self.data)))

    # function to play viceo
    def play_video(self):
        self.mediaPlayer.play()
        self.videoFlag = True
        self.pauseFlag = True
        if self.metric == 'Compliance' and not self.end_comp_button.isEnabled() and not self.start_comp_button.isEnabled():
            self.start_comp_button.setEnabled(True)
        elif self.metric == 'Compliance' and not self.end_comp_button.isEnabled():
            self.start_comp_button.setEnabled(True)

    # function to pause video
    def pause_video(self):
        self.mediaPlayer.pause()
        self.videoFlag = False
        #print("Pausing the Video.")

    # adds to the frequencyCounter list if the key is pressed at the end of the video
    def end_of_video_pressed(self):
        if self.iskeyPressed:
            self.frequencyCounter.append(
                self.mediaPlayer.position() / 1000)
            if self.keyPressed == self.HK1:
                self.frequencyCounter.append(self.L1)
            elif self.keyPressed == self.HK2:
                self.frequencyCounter.append(self.L2)
            elif self.keyPressed == self.HK3:
                self.frequencyCounter.append(self.L3)
            elif self.keyPressed == self.HK4:
                self.frequencyCounter.append(self.L4)
            else:
                self.frequencyCounter.append(self.keyPressed)
            self.frequencyCounter.append(
                self.interval_list.index(self.mediaPlayer.position()))
            self.iskeyPressed = False

    # adds to frequencyCounter list if key is pressed or if key is held at end of interval
    def add_to_list(self, slider_size):
        if self.iskeyPressed:
            self.frequencyCounter.append(
                self.mediaPlayer.position() / 1000)
            if self.keyPressed == self.HK1:
                self.frequencyCounter.append(self.L1)
            elif self.keyPressed == self.HK2:
                self.frequencyCounter.append(self.L2)
            elif self.keyPressed == self.HK3:
                self.frequencyCounter.append(self.L3)
            elif self.keyPressed == self.HK4:
                self.frequencyCounter.append(self.L4)
            else:
                self.frequencyCounter.append(self.keyPressed)
            if self.mediaPlayer.position() % slider_size == 1:
                self.frequencyCounter.append(
                    self.interval_list.index(self.mediaPlayer.position()-1))
                self.mediaPlayer.setPosition(
                    self.mediaPlayer.position() - 1)
            else:
                self.frequencyCounter.append(
                    self.interval_list.index(self.mediaPlayer.position()))
            self.iskeyPressed = False

    def sliderTimer(self):
        # print("The time in the Video is: ", self.mediaPlayer.position())
        # If video is at end then promptEnd, removed statusChanged function
        if self.metric != 'Compliance':
            if self.mediaPlayer.mediaStatus() == 7:
                self.end_of_video_pressed()
                self.promptEnd()

            elif self.pauseFlag == True:
                x = self.sliderSize * 1000
                if (int(self.mediaPlayer.position())) >= 1000:
                    if self.mediaPlayer.position() % x == 0:
                        self.pauseFlag = False
                        self.pause_video()
                        # adds values to frequencyCounter list
                        self.add_to_list(x)
                        # put the flag to reset the lock on other keys here
                        self.promptData()
        elif self.metric == 'Compliance' and self.mediaPlayer.mediaStatus() == 7 and len(self.compliance_time_pts) == 1:
            self.compliance_time_pts.append(self.mediaPlayer.duration()/1000)
            labels = ['Compliant', 'Noncompliant', 'Anticipated']
            label, ok = QInputDialog().getItem(self, 'Label Compliancy',
                                               'Please Select Label Name of Interval:', labels, current=0, editable=False)
            if label and ok:
                self.compliance_time_pts.append(label)
                self.compliance_list.append(self.compliance_time_pts)
                self.compliance_time_pts = []
            else:
                self.compliance_time_pts = []

            print(self.compliance_list)
            self.end_comp_button.setEnabled(False)

    def promptEnd(self):
        # mode 1 is end of video prompt
        self.pop_up = popUpTable(self.frequencyCounter, 1, self.completeList)

    def promptData(self):
        # popup box for data
        print(self.frequencyCounter)
        check_num = self.mediaPlayer.position() - (self.mediaPlayer.position() %
                                                   (self.sliderSize * 1000))
        interval = self.interval_list.index(check_num)
        #print('interval is:', interval)
        df = pd.DataFrame(self.completeList)
        print(df)
        if interval in list(df[3]):
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Data Present")
            dialog.setText(
                "Data is already in this interval. Do you want to overwrite the data? If yes, redo/save windows will popup. If no, then no window will popup and you can continue")
            dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dialog.setModal(False)
            button = dialog.exec_()
            if button == QMessageBox.Yes:
                df.drop(df[df[3] == interval].index, inplace=True)
                #print('df after deletion:', df)
                self.completeList = df.values.tolist()
                # mode 0 is regular slider interval
                self.pop_up = popUpTable(
                    self.frequencyCounter, 0, self.completeList)
            else:
                self.frequencyCounter = []
        else:
            # mode 0 is regular slider interval
            self.pop_up = popUpTable(
                self.frequencyCounter, 0, self.completeList)
    # hotkey for logging

    def keyPressEvent(self, e: QKeyEvent):
        pos = self.mediaPlayer.position()
        pos = pos / 1000.0
        if self.videoFlag == True:

            if e.text() == self.HK1 and not e.isAutoRepeat() and not self.iskeyPressed:
                self.frequencyCounter.append(pos)
                self.iskeyPressed = True
                self.keyPressed = self.HK1
                print(self.frequencyCounter)

            elif (
                e.text() == self.HK2 and not e.isAutoRepeat() and not self.iskeyPressed
            ):
                self.frequencyCounter.append(pos)
                self.iskeyPressed = True
                self.keyPressed = self.HK2
                print(self.frequencyCounter)

            elif (
                e.text() == self.HK3 and not e.isAutoRepeat() and not self.iskeyPressed
            ):
                self.frequencyCounter.append(pos)
                self.iskeyPressed = True
                self.keyPressed = self.HK3
                print(self.frequencyCounter)

            elif (
                e.text() == self.HK4 and not e.isAutoRepeat() and not self.iskeyPressed
            ):
                self.frequencyCounter.append(pos)
                self.iskeyPressed = True
                self.keyPressed = self.HK4
                print(self.frequencyCounter)
        elif self.videoFlag == False:
            print("video must be playing to use hotkeys")

    def keyReleaseEvent(self, e: QKeyEvent):
        pos = self.mediaPlayer.position()
        bisect.insort(self.interval_list, pos)
        interval = self.interval_list.index(pos)
        self.interval_list.pop(interval)
        pos = pos/1000.0
        if self.videoFlag == True:

            if e.text() == self.HK1 and not e.isAutoRepeat() and self.keyPressed == self.HK1:
                self.frequencyCounter.append(pos)
                if self.L1 != "":
                    self.frequencyCounter.append(self.L1)
                else:
                    self.frequencyCounter.append(self.HK1)
                self.iskeyPressed = False
                self.keyPressed = ""
                self.frequencyCounter.append(interval)
                print(self.frequencyCounter)

            elif e.text() == self.HK2 and not e.isAutoRepeat() and self.keyPressed == self.HK2:
                self.frequencyCounter.append(pos)
                if self.L2 != "":
                    self.frequencyCounter.append(self.L2)
                else:
                    self.frequencyCounter.append(self.HK2)
                self.iskeyPressed = False
                self.keyPressed = ""
                self.frequencyCounter.append(interval)
                print(self.frequencyCounter)

            elif e.text() == self.HK3 and not e.isAutoRepeat() and self.keyPressed == self.HK3:
                self.frequencyCounter.append(pos)
                if self.L3 != "":
                    self.frequencyCounter.append(self.L3)
                else:
                    self.frequencyCounter.append(self.HK3)
                self.iskeyPressed = False
                self.keyPressed = ""
                self.frequencyCounter.append(interval)
                print(self.frequencyCounter)

            elif e.text() == self.HK4 and not e.isAutoRepeat() and self.keyPressed == self.HK4:
                self.frequencyCounter.append(pos)
                if self.L4 != "":
                    self.frequencyCounter.append(self.L4)
                else:
                    self.frequencyCounter.append(self.HK4)
                self.iskeyPressed = False
                self.keyPressed = ""
                self.frequencyCounter.append(interval)
                print(self.frequencyCounter)

        elif self.videoFlag == False:
            print("video must be playing to use hotkeys")

    def updateSaveData(self):
        #print("Adding this list onto the 2D Final List")
        # self.pop_up.temp contains self.frequency coutner
        # only if frequecycounter isn't empty do this
        if len(self.pop_up._temp) > 0:
            for row in self.pop_up._convertedData:
                self.completeList.append(row)
        self.frequencyCounter = []
        # print('complete list:', self.completeList)
        # print('time in video is:', self.mediaPlayer.position())
        self.mediaPlayer.setPosition(self.mediaPlayer.position() + 1)

    def updateRedoData(self, num_int):
        #print("Deleting data and moving position back to before this run through.")
        self.frequencyCounter = []
        x = self.sliderSize * 1000
        if self.mediaPlayer.position() % x == 0:
            self.mediaPlayer.setPosition(
                self.mediaPlayer.position() - (num_int * self.sliderSize * 1000) + 1
            )

            # print("returning to:", self.mediaPlayer.position() -
            #       (self.sliderSize * 1000) + 1)

        elif self.mediaPlayer.position() % x == 1:
            self.mediaPlayer.setPosition(
                self.mediaPlayer.position() - (num_int * self.sliderSize * 1000)
            )
            # print("returning to:", self.mediaPlayer.position() -
            #       (self.sliderSize * 1000))

        elif self.mediaPlayer.position() % x == 2:
            self.mediaPlayer.setPosition(
                self.mediaPlayer.position() - (num_int * self.sliderSize * 1000) - 1
            )
            # print("returning to:", self.mediaPlayer.position() -
            #       (self.sliderSize * 1000) - 1)

        else:

            self.mediaPlayer.setPosition(
                self.mediaPlayer.position() - (num_int * self.mediaPlayer.position() % x) + 1
            )
            # print("returning to:", (self.mediaPlayer.position() -
            #                         (self.mediaPlayer.position() % x) + 1))

    def updateDataAndEnd(self):
        print("Make Window to show complete data and choose to save or not.")
        print(self.completeList)
        try:
            if len(self.pop_up._temp) > 0:
                for row in self.pop_up._convertedData:
                    self.completeList.append(row)
            if len(self.completeList) < 2:
                start_end_int_string = self.start_interval_input.text() + '-' + \
                    self.end_interval_input.text()
                self.completeList.append(
                    ['N/A', 'N/A', 'No Data Coded', start_end_int_string])
                self.finalWindow = FinalTable(
                    self.completeList[1:], self.metric, self.interval_list, int(self.start_interval_input.text()), int(self.end_interval_input
                                                                                                                       .text()))
            else:
                self.finalWindow = FinalTable(
                    self.completeList[1:], self.metric, self.interval_list, int(self.start_interval_input.text()), int(self.end_interval_input
                                                                                                                       .text()))
            self.frequencyCounter = []

        except:
            error_dialog = QErrorMessage()
            error_dialog.showMessage('Please check start and end intervals')
            error_dialog.exec_()

# popUp class


class popUpTable(QWidget):
    def __init__(self, data, mode, complete_list):  # data param is the frequencycounter list
        super().__init__()
        self.mode = mode
        # data for the file name
        self._data = self.buildList(data)
        print('self._data:', self._data)
        # Have to rebuild the list because python variables only act as labels rather than C/Java variables
        self._temp = self.buildList(data)
        self._convertedData = self.convertTo2DArray(self._data)
        self._complete_list = complete_list
        print('converted data:', self._convertedData)
        self.setWindowTitle("Data")
        self.resize(700, 500)
        self.center()
        self.init_ui()
        self.show()

    def init_ui(self):

        self.grid = QVBoxLayout()
        self.buttons = QHBoxLayout()
        self.setLayout(self.grid)

        self.redoData = QPushButton()
        self.saveData = QPushButton()
        self.show_complete_table = QPushButton()
        self.rev_text_box = QLineEdit()
        self.redoData.setText("Redo Data")
        self.rev_text_box.setText("Enter how many intervals want to go back")
        self.saveData.setText("Save Data")
        self.show_complete_table.setText("Show All Coded Values")
        self.buttons.addWidget(self.redoData)
        self.buttons.addWidget(self.rev_text_box)
        self.buttons.addWidget(self.saveData)
        self.buttons.addWidget(self.show_complete_table)
        self.grid.addLayout(self.buttons)

        self.redoData.clicked.connect(self.emitRedoSignal)
        self.saveData.clicked.connect(self.emitSaveSignal)
        self.show_complete_table.clicked.connect(self.show_table_values)

        if self._convertedData:
            self.tableWidget = QTableView()
            self.tableWidget.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeToContents)
            self.model = TableModel(self._convertedData)
            self.tableWidget.setModel(self.model)
            self.grid.addWidget(self.tableWidget)

        else:
            self.listLabel = QLabel()
            self.listLabel.setText(str(self._data))
            self.grid.addWidget(self.listLabel)

        # define two signals that are emitted when save/redo is pressed
        # save signal will tell the video_player window that it needs to save that list to the main list, --> 2d array
        # redo signal will tell the video_player window that it needs to del the list and remake it, also backup the position of the window to slider timer backwards
    def show_table_values(self):
        df = pd.DataFrame(self._complete_list[1:])
        if not df.empty:
            df.sort_values(by=3, inplace=True)
        data = df.values.tolist()
        model_table_values = TableModel(data)
        self.tableWidget_values = QTableView()
        self.tableWidget_values.horizontalHeader(
        ).setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableWidget_values.setModel(model_table_values)
        self.tableWidget_values.setWindowTitle('Coded Values')
        self.tableWidget_values.resize(600, 600)
        self.tableWidget_values.show()

    def emitSaveSignal(self):
        if self.mode == 0:
            window.dialog.updateSaveData()
            self.close()

        # end of video
        elif self.mode == 1:
            window.dialog.updateDataAndEnd()
            self.close()

    def emitRedoSignal(self):
        try:
            num_int = int(self.rev_text_box.text())
            window.dialog.updateRedoData(num_int)
            self.close()
        except ValueError:
            error_dialog = QErrorMessage()
            error_dialog.showMessage('Not valid number, please try again')
            error_dialog.exec_()

    def buildList(self, x):
        newList = []
        for i in range(len(x)):
            newList.append(x[i])
        return newList

    def convertTo2DArray(self, data):
        if len(data) > 4:
            final = []
            for i in range(0, int(len(data) / 4)):
                tmp = []
                for j in range(0, 4):
                    tmp.append(data[0])
                    data.pop(0)

                final.append(tmp)

            return final
        else:
            return [data]

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, *args):
        super(TableModel, self).__init__()
        self._data = data
        self.headers = ['Time Pressed', 'Time Released',
                        'Label', 'Interval']

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

        # if index.isValid():
        #     if role == Qt.DisplayRole or role == Qt.EditRole:
        #         value = self._data[index.row()][index.column()]
        #         return str(value)

    # def setData(self, index, value, role):
    #     if role == Qt.EditRole:
    #         self._data[index.row()][index.column()] = value
    #         return True

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        try:
            return len(self._data[0])
        except:
            return 0

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)


class FinalTable(QWidget):
    def __init__(self, data, metric, interval_list, *args, **kwargs):
        super().__init__()
        # instance variable to store metric (ex: engagement, performance)
        self.metric = metric
        # instance variable to store interval list
        self.interval_list = interval_list
        # instance variable to store number of intervals
        self.start_interval = args[0]
        self.end_interval = args[1]
        if args:
            self.num_intervals = self.end_interval - \
                self.start_interval + 1
        else:
            self.num_intervals = len(self.interval_list) - 1
        # make empty dataframe if data is empty list
        df = pd.DataFrame(data)
        if not df.empty:
            df.sort_values(by=0, inplace=True)
        if is_numeric_dtype(df[3]):
            df = df[(df[3] >= self.start_interval) &
                    (df[3] <= self.end_interval)]
        self.new_data = df.values.tolist()

        self.setWindowTitle("Final Save Table")
        self.resize(700, 500)
        self.center()
        self.init_ui()
        self.show()

    def init_ui(self):
        self.file_save_name = QLineEdit()
        self.file_save_name.setText('Enter name of file want to save as')
        self.folder_save_name = QLineEdit('Folder save directory')
        self.grid = QVBoxLayout()
        self.buttons = QHBoxLayout()
        self.setLayout(self.grid)

        self.browse_folder = QPushButton('Browse')
        self.saveData = QPushButton()
        self.saveData.setText("Save Data")
        self.buttons.addWidget(self.file_save_name)
        self.buttons.addWidget(self.folder_save_name)
        self.buttons.addWidget(self.browse_folder)
        self.buttons.addWidget(self.saveData)
        self.grid.addLayout(self.buttons)

        self.saveData.clicked.connect(self.emitSaveSignal)
        self.browse_folder.clicked.connect(self.save_folder)

        if self.new_data:
            self.tableWidget = QTableView()
            self.tableWidget.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeToContents)
            self.model_2 = TableModel(self.new_data, self.metric)
            self.tableWidget.setModel(self.model_2)
            self.grid.addWidget(self.tableWidget)

        else:
            self.listLabel = QLabel()
            self.listLabel.setText(str(self.data))
            self.grid.addWidget(self.listLabel)

    def save_folder(self):
        try:
            dirName = str(QFileDialog.getExistingDirectory(
                self, 'Select Directory', options=QFileDialog.DontUseNativeDialog))
            if dirName:
                self.folder_save_name.setText(dirName)
        except:
            error_dialog = QErrorMessage()
            error_dialog.showMessage('Not valid directory')
            error_dialog.exec_()

    def emitSaveSignal(self):
        self.new_file_name = self.file_save_name.text() + '.csv'
        #print(self.folder_save_name.text() + '/' + self.new_file_name)
        df = pd.DataFrame(self.new_data, columns=[
                          'Time Pressed', 'Time Released', 'Label', 'Interval'])
        # df = df[(df['Interval'] >= self.start_interval) &
        #         (df['Interval'] <= self.end_interval)]
        try:
            df.to_csv(self.folder_save_name.text() + '/' + self.new_file_name,
                      index=False, header=True)
            self.close()
            # window.dialog.close()
        except:
            error_dialog = QErrorMessage()
            error_dialog.showMessage('Invalid save name')
            error_dialog.exec_()

    def buildList(self, x):
        newList = []
        for i in range(len(x)):
            newList.append(x[i])
        return newList

    def convertTo2DArray(self, data):
        if len(data) > 4:
            final = []
            for i in range(0, int(len(data) / 4)):
                tmp = []
                for j in range(0, 4):
                    tmp.append(data[0])
                    data.pop(0)

                final.append(tmp)

            return final
        else:
            return [data]

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = media_player()
    window.show()
    sys.exit(app.exec_())
