from dataclasses import replace
from tracemalloc import start
import pandas as pd
import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QErrorMessage, QFileDialog
)

from ioa_gui import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.metric = str(self.ui.comboBox.currentText())

        self.ui.pushButton.clicked.connect(self.csv_one)
        self.ui.pushButton_2.clicked.connect(self.csv_two)
        self.ui.pushButton_3.clicked.connect(self.calculate)
        self.ui.comboBox.currentTextChanged.connect(self.text_changed)

    def csv_one(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, ".csv file", "", ".csv file (*.csv)")
            if file_name:
                self.ui.lineEdit.setText(file_name)
        except:
            error_dialog = QErrorMessage()
            error_dialog.showMessage('Not valid file')
            error_dialog.exec_()

    def csv_two(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, ".csv file", "", ".csv file (*.csv)")
            if file_name:
                self.ui.lineEdit_2.setText(file_name)
        except:
            error_dialog = QErrorMessage()
            error_dialog.showMessage('Not valid file')
            error_dialog.exec_()

    def calculate(self):
        # try:
        df1 = pd.read_csv(self.ui.lineEdit.text())
        df2 = pd.read_csv(self.ui.lineEdit_2.text())
        df1['Label'] = df1['Label'].str.lower()
        df2['Label'] = df2['Label'].str.lower()
        df1['Label'] = df1['Label'].str.strip()
        df2['Label'] = df2['Label'].str.strip()
        # print(self.metric)
        if self.metric == 'Performance' or self.metric == 'Communication':
            freq_df1 = df1.shape[0]
            freq_df2 = df2.shape[0]
            ioa = 0
            if freq_df1 < freq_df2:
                ioa = freq_df1/freq_df2
            else:
                ioa = freq_df2/freq_df1
            self.ui.textEdit_2.setText(str(ioa))

            if ioa < float(self.ui.lineEdit_4.text()):
                self.ui.textEdit.setText(
                    "fix ioa score. Recode the video together")
            else:
                self.ui.textEdit.setText("N/A")

        elif self.metric == 'Affect (Total)':
            start_interval = int(self.ui.lineEdit_5.text())
            end_interval = int(self.ui.lineEdit_6.text())
            df1_unique_intervals = list(df1['Interval'].unique())
            df2_unique_intervals = list(df2['Interval'].unique())
            # print(df1_unique_intervals)
            # print(df2_unique_intervals)

            for i in range(start_interval, end_interval+1):
                if i not in df1_unique_intervals:
                    time_pressed = (i-1) * 10 + 0.001
                    time_released = i * 10
                    label = "neutral"
                    interval = i
                    add_row = {"Time Pressed": time_pressed,
                               "Time Released": time_released, "Label": label, "Interval": interval}
                    df1 = df1.append(add_row, ignore_index=True)

                if i not in df2_unique_intervals:
                    time_pressed = (i-1) * 10 + 0.001
                    time_released = i * 10
                    label = "neutral"
                    interval = i
                    add_row = {"Time Pressed": time_pressed,
                               "Time Released": time_released, "Label": label, "Interval": interval}
                    df2 = df2.append(add_row, ignore_index=True)

            df1 = df1[(df1['Interval'] >= start_interval)
                      & (df1['Interval'] <= end_interval)]
            df2 = df2[(df2['Interval'] >= start_interval)
                      & (df2['Interval'] <= end_interval)]
            df1['zip'] = list(zip(df1['Label'], df1['Interval']))
            df2['zip'] = list(zip(df2['Label'], df2['Interval']))
            df1_unique_val = list(df1['zip'].unique())
            df2_unique_val = list(df2['zip'].unique())
            df1_neg_count = 0
            df1_pos_count = 0
            df1_neut_count = 0
            df2_neg_count = 0
            df2_pos_count = 0
            df2_neut_count = 0
            pos_ioa = 0
            neg_ioa = 0
            neut_ioa = 0
            for val in df1_unique_val:
                if val[0] == 'negative':
                    df1_neg_count += 1
                elif val[0] == 'positive':
                    df1_pos_count += 1
                else:
                    df1_neut_count += 1
            for val in df2_unique_val:
                if val[0] == 'negative':
                    df2_neg_count += 1
                elif val[0] == 'positive':
                    df2_pos_count += 1
                else:
                    df2_neut_count += 1

            if df1_neg_count == 0 and df2_neg_count == 0:
                neg_ioa = 'N/A'
            elif df1_neg_count < df2_neg_count:
                neg_ioa = round(df1_neg_count / df2_neg_count, 3)
            else:
                neg_ioa = round(df2_neg_count / df1_neg_count, 3)

            if df1_pos_count == 0 and df2_pos_count == 0:
                pos_ioa = 'N/A'
            elif df1_pos_count < df2_pos_count:
                pos_ioa = round(df1_pos_count / df2_pos_count, 3)
            else:
                pos_ioa = round(df2_pos_count / df1_pos_count, 3)

            if df1_neut_count == 0 and df2_neut_count == 0:
                neut_ioa = 'N/A'
            elif df1_neut_count < df2_neut_count:
                neut_ioa = round(df1_neut_count / df2_neut_count, 3)
            else:
                neut_ioa = round(df2_neut_count / df1_neut_count, 3)

            count_match = sum(
                val in df2_unique_val for val in df1_unique_val)
            total_ioa = round(
                count_match / (end_interval - start_interval + 1), 3)
            ioa_text = "Total IOA: " + str(total_ioa) + "\n" + "Positive IOA: " + str(pos_ioa) + "\n" + "Negative IOA: " + str(neg_ioa) + \
                "\n" + "Neutral IOA: " + str(neut_ioa)
            self.ui.textEdit_2.setText(ioa_text)
            fix_int = list(
                sorted(set(df1_unique_val).symmetric_difference(set(df2_unique_val))))
            res = sorted(set(list(zip(*fix_int))[-1]))
            if total_ioa < float(self.ui.lineEdit_4.text()):
                self.ui.textEdit.setText(
                    "fix ioa score. Recode the video together. These intervals:" + str(res))
            else:
                self.ui.textEdit.setText("N/A")

        elif self.metric == 'Engagement':
            start_interval = int(self.ui.lineEdit_5.text())
            end_interval = int(self.ui.lineEdit_6.text())
            df1 = df1[(df1['Interval'] >= start_interval)
                      & (df1['Interval'] <= end_interval)]
            df2 = df2[(df2['Interval'] >= start_interval)
                      & (df2['Interval'] <= end_interval)]
            df1_unique_labels = sorted(list(df1['Label'].unique()))
            df2_unique_labels = sorted(list(df2['Label'].unique()))
            total_time = (end_interval - start_interval + 1) * 10
            # print(df1_unique_labels)
            # print(df2_unique_labels)
            replace_list = ["bt/peers", "instructor/screen/on task"]
            if len(df1_unique_labels) > 1:
                df1['Label'].replace(
                    df1_unique_labels, replace_list, inplace=True)
            if len(df2_unique_labels) > 1:
                df2['Label'].replace(
                    df2_unique_labels, replace_list, inplace=True)
            # print(df1)
            # print(df2)
            df1_fixed_labels = sorted(list(df1['Label'].unique()))
            df2_fixed_labels = sorted(list(df2['Label'].unique()))
            times_1 = {}
            times_2 = {}
            for label in df1_fixed_labels:
                df_label = df1[df1['Label'] == label].copy()
                # print(df_label)
                df_label['time held'] = df_label['Time Released'] - \
                    df_label['Time Pressed']
                time_held = round(df_label['time held'].sum(), 4)
                times_1[label] = time_held

            for label in df2_fixed_labels:
                df_label = df2[df2['Label'] == label].copy()
                # print(df_label)
                df_label['time held'] = df_label['Time Released'] - \
                    df_label['Time Pressed']
                time_held = round(df_label['time held'].sum(), 4)
                times_2[label] = time_held

            times_1['off target'] = round(
                total_time - sum(times_1.values()), 4)
            times_2['off target'] = round(
                total_time - sum(times_2.values()), 4)

            ioa_scores_eng = {}
            for key in times_1.keys():
                if key in times_2.keys():
                    if times_1[key] > times_2[key]:
                        ioa_scores_eng[key] = round(
                            times_2[key] / times_1[key], 4)
                    else:
                        ioa_scores_eng[key] = round(
                            times_1[key] / times_2[key], 4)
                else:
                    ioa_scores_eng[key] = 0
            if len(times_1.keys()) < len(times_2.keys()):
                key_diff = set(list(times_1.keys())) ^ set(
                    list(times_2.keys()))
                for label in key_diff:
                    ioa_scores_eng[label] = 0

            text_edit_str = ""
            for k, v in ioa_scores_eng.items():
                ioa_value = k + ': ' + str(v) + '\n'
                text_edit_str += ioa_value
                if v < float(self.ui.lineEdit_4.text()):
                    self.ui.textEdit.setText(
                        "fix ioa score. Recode the video together")
            self.ui.textEdit_2.setText(text_edit_str)
            if self.ui.textEdit.toPlainText() == "":
                self.ui.textEdit.setText("N/A")

                #print(k, v,sep=': ')
            # print(times_1)
            # print(times_2)
            # print(ioa_scores_eng)

        # except:
        #     error_dialog = QErrorMessage()
        #     error_dialog.showMessage('Check inputs, something went wrong')
        #     error_dialog.exec_()

    def text_changed(self):
        self.metric = str(self.ui.comboBox.currentText())
        if self.metric == 'Communication' or self.metric == 'Performance':
            self.ui.lineEdit_5.setEnabled(False)
            self.ui.lineEdit_6.setEnabled(False)
        else:
            self.ui.lineEdit_5.setEnabled(True)
            self.ui.lineEdit_6.setEnabled(True)


if __name__ == '__main__':
    sys._excepthook = sys.excepthook

    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = exception_hook

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
