from dataclasses import replace
from tracemalloc import start
import pandas as pd
import sys
import numpy as np
from sklearn.metrics import cohen_kappa_score, confusion_matrix
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
        # print(df1)
        # print(df2)
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

        elif self.metric == 'IOA Backchannel':
            # time pressed, time released, label, interval
            # df1_unique_intervals = list(df1.unique())
            # df2_unique_intervals = list(df2.unique())

            # IOA backchannel = matching intevals/max # of coded intervals between the 2 coders in each submetric
            # num of unique coded intervals file 1
            df1_num_ci = len(df1['Interval'].unique())
            # num of unique coded intervals file 2
            df2_num_ci = len(df2['Interval'].unique())
            # max number of coded intervals between two files
            denom = max(df1_num_ci, df2_num_ci)
            # unique labels file 1
            df1_unique_labels = sorted(df1['Label'].unique())
            # unique lables file 2
            df2_unique_labels = sorted(df2['Label'].unique())

            print(df1_unique_labels)
            print(df2_unique_labels)
            # print(denom)
            # print(df1_num_ci)
            # print(df2_num_ci)

            # list of tuples with label and interval Ex: [(Label, Interval), (Label_2, Interval_2), (Label_2, Interval_2)]
            df1_val_int = list(set(zip(df1['Label'], df1['Interval'])))
            df2_val_int = list(set(zip(df2['Label'], df2['Interval'])))

            # difference between 2 lists
            discrepancies = list(
                set(df1_val_int).symmetric_difference(set(df2_val_int)))
            discrepancies = sorted(discrepancies, key=lambda x: x[1])

            print(discrepancies)

            # Make dictionary with key value pairs as label,total count of label. Ex: {'p': 3, 'n': 1, 'b': 3}
            dict_values_df1 = {}
            dict_values_df2 = {}
            # Instantiate an dictionary with the labels and total number of matching values between files. Set as 0 intially.
            matching_values_dict = {}
            # Instantiate a dictionary with max num of coded intervals in submetric
            max_submetric_ci_dict = {}
            # instantiate a dictionary with ioa values
            ioa_values_dict = {}
            union_unique_labels = sorted(
                list(set(df1_unique_labels)) + list(set(df2_unique_labels)))
            for val in union_unique_labels:
                max_submetric_ci_dict[val] = 0

            for label in df1_unique_labels:
                count = 0
                for val in df1_val_int:
                    if label == val[0]:
                        count += 1
                dict_values_df1[label] = count
                if label not in matching_values_dict:
                    matching_values_dict[label] = 0

            for label in df2_unique_labels:
                count = 0
                for val in df2_val_int:
                    if label == val[0]:
                        count += 1
                dict_values_df2[label] = count
                if label not in matching_values_dict:
                    matching_values_dict[label] = 0

            print('number of values for submetric file1', dict_values_df1)
            print('number of values for submetric file2', dict_values_df2)
           # print(matching_values_dict)
            for val in df1_val_int:
                if val in df2_val_int:
                    matching_values_dict[val[0]] += 1

            df1_keys = list(set(dict_values_df1.keys()))
            df2_keys = list(set(dict_values_df2.keys()))
            union_keys = sorted(df1_keys + df2_keys)

            for key in union_keys:
                if key in dict_values_df1.keys() and key in dict_values_df2.keys():
                    max_submetric_ci_dict[key] = max(
                        dict_values_df1[key], dict_values_df2[key])
                elif key in dict_values_df1.keys() and (key not in dict_values_df2.keys()):
                    max_submetric_ci_dict[key] = dict_values_df1[key]
                elif key not in dict_values_df1.keys() and key in dict_values_df2.keys():
                    max_submetric_ci_dict[key] = dict_values_df2[key]

            print('matching values for submetric:', matching_values_dict)
            print('max intervals for submetric', max_submetric_ci_dict)

            for key in sorted(matching_values_dict.keys()):
                if key in sorted(max_submetric_ci_dict.keys()):
                    if matching_values_dict[key] < max_submetric_ci_dict[key]:
                        ioa_val = matching_values_dict[key] / \
                            max_submetric_ci_dict[key]
                        ioa_values_dict[key] = ioa_val
                    else:
                        ioa_val = max_submetric_ci_dict[key] / \
                            matching_values_dict[key]
                        ioa_values_dict[key] = ioa_val

            print('ioa values:', ioa_values_dict)
            ioa_text = ioa_values_dict
            self.ui.textEdit_2.setText(str(ioa_text))
            self.ui.textEdit.setText("Discrepancies: " + str(discrepancies))
            # Note that there's not going to be any output for intervals to finx

            # intersection_list = []
            # for val in df1_val_int:
            #     if val in df2_val_int:
            #         intersection_list.append(val)
            # print(df1_val_int)
            # print(df2_val_int)
            # print(intersection_list)

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

            df1 = df1.drop_duplicates(subset=['Label', 'Interval'])
            df2 = df2.drop_duplicates(subset=['Label', 'Interval'])

            df1 = df1.sort_values(by=['Interval'])
            df2 = df2.sort_values(by=['Interval'])

            duplicate_df1 = df1[df1.duplicated(subset="Interval", keep=False)]
            duplicate_df1_list = sorted(duplicate_df1['Interval'].unique(
            ))
            df1 = df1[~df1['Interval'].isin(duplicate_df1_list)]
            for interval in duplicate_df1_list:
                add_row = {"Time Pressed": "N/A", "Time Released": "N/A",
                           "Label": "p&n", "Interval": interval}
                df1 = df1.append(add_row, ignore_index=True)
            duplicate_df2 = df2[df2.duplicated(subset="Interval", keep=False)]
            duplicate_df2_list = sorted(duplicate_df2['Interval'].unique(
            ))
            df2 = df2[~df2['Interval'].isin(duplicate_df2_list)]
            for interval in duplicate_df2_list:
                add_row = {"Time Pressed": "N/A", "Time Released": "N/A",
                           "Label": "p&n", "Interval": interval}
                df2 = df2.append(add_row, ignore_index=True)

            df1 = df1.sort_values(by=['Interval'])
            df2 = df2.sort_values(by=['Interval'])
            print(df1)
            print(df2)

            df1_labels = df1['Label'].tolist()
            df2_labels = df2['Label'].tolist()
            print(df1_labels)
            print(df2_labels)
            labels = ['positive', 'negative', 'neutral', 'p&n']
            cm = confusion_matrix(df1_labels, df2_labels, labels=labels)
            # Add 'Total' column and row to confusion matrix
            cm_with_total = np.vstack([cm, np.sum(cm, axis=0)])
            cm_with_total = np.column_stack(
                [cm_with_total, np.sum(cm_with_total, axis=1)])

            # Create a DataFrame for confusion matrix
            df_cm = pd.DataFrame(
                cm_with_total, index=labels+['Total'], columns=labels+['Total'])
            print("Confusion Matrix:")
            print(df_cm)
            print("Cohen's kappa score:")
            cks = cohen_kappa_score(df1_labels, df2_labels)
            print(cks)

            self.ui.textEdit_2.setText(
                df_cm.to_string() + "\n" + "\n" "Cohen's Kappa Score: " + str(cks))

            differ_indices = [
                (i + start_interval) for i, (x, y) in enumerate(zip(df1_labels, df2_labels)) if x != y]

            # for i in differ_indices:
            #     print(df1_labels[i-1])
            #     print(df2_labels[i-1])
            self.ui.textEdit.setText(
                "Differing Intervals: " + str(differ_indices))

            # df1['zip'] = list(zip(df1['Label'], df1['Interval']))
            # df2['zip'] = list(zip(df2['Label'], df2['Interval']))
            # df1_unique_val = list(df1['zip'].unique())
            # df2_unique_val = list(df2['zip'].unique())
            # print(len(df1_unique_val))
            # print(len(df2_unique_val))
            # print(cohen_kappa_score(df1))
            # df1_neg_count = 0
            # df1_pos_count = 0
            # df1_neut_count = 0
            # df2_neg_count = 0
            # df2_pos_count = 0
            # df2_neut_count = 0
            # pos_ioa = 0
            # neg_ioa = 0
            # neut_ioa = 0
            # for val in df1_unique_val:
            #     if val[0] == 'negative':
            #         df1_neg_count += 1
            #     elif val[0] == 'positive':
            #         df1_pos_count += 1
            #     else:
            #         df1_neut_count += 1
            # for val in df2_unique_val:
            #     if val[0] == 'negative':
            #         df2_neg_count += 1
            #     elif val[0] == 'positive':
            #         df2_pos_count += 1
            #     else:
            #         df2_neut_count += 1

            # if df1_neg_count == 0 and df2_neg_count == 0:
            #     neg_ioa = 'N/A'
            # elif df1_neg_count < df2_neg_count:
            #     neg_ioa = round(df1_neg_count / df2_neg_count, 3)
            # else:
            #     neg_ioa = round(df2_neg_count / df1_neg_count, 3)

            # if df1_pos_count == 0 and df2_pos_count == 0:
            #     pos_ioa = 'N/A'
            # elif df1_pos_count < df2_pos_count:
            #     pos_ioa = round(df1_pos_count / df2_pos_count, 3)
            # else:
            #     pos_ioa = round(df2_pos_count / df1_pos_count, 3)

            # if df1_neut_count == 0 and df2_neut_count == 0:
            #     neut_ioa = 'N/A'
            # elif df1_neut_count < df2_neut_count:
            #     neut_ioa = round(df1_neut_count / df2_neut_count, 3)
            # else:
            #     neut_ioa = round(df2_neut_count / df1_neut_count, 3)

            # count_match = sum(
            #     val in df2_unique_val for val in df1_unique_val)
            # total_ioa = round(
            #     count_match / (end_interval - start_interval + 1), 3)
            # ioa_text = "Total IOA: " + str(total_ioa) + "\n" + "Positive IOA: " + str(pos_ioa) + "\n" + "Negative IOA: " + str(neg_ioa) + \
            #     "\n" + "Neutral IOA: " + str(neut_ioa)
            # self.ui.textEdit_2.setText(ioa_text)
            # fix_int = list(
            #     sorted(set(df1_unique_val).symmetric_difference(set(df2_unique_val))))
            # res = sorted(set(list(zip(*fix_int))[-1]))
            # self.ui.textEdit.setText(str(res))
            # if total_ioa < float(self.ui.lineEdit_4.text()):
            #     self.ui.textEdit.setText(
            #         "fix ioa score. Recode the video together. These intervals:" + str(res))
            # else:
            #     self.ui.textEdit.setText("N/A")

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
