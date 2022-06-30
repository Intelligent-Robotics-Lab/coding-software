import os
import pandas as pd

folder_path = r"C:\Users\nhuan\Desktop\coding-data\2022-06-29"
for file in os.listdir(folder_path):
    f = os.path.join(folder_path,file)
    if os.path.isfile(f):
        print(f)
        df = pd.read_csv(f)
        unique_labels = sorted(list(df['Label'].unique()))
        times = {}
        start_interval = int(input("start interval: "))
        end_interval = int(input("end interval: "))
        total_time = (end_interval - start_interval + 1) * 10
        replace_list = ["bt/peers","instructor/screen/on task"]
        df = df[(df['Interval'] >= start_interval)
                            & (df['Interval'] <= end_interval)]
        if len(unique_labels) > 1:
            df.replace(unique_labels, replace_list, inplace=True)

        fixed_labels = sorted(list(df['Label'].unique()))
        for label in fixed_labels:
            df_label = df[df['Label'] == label].copy()
            # print(df_label)
            df_label['time held'] = df_label['Time Released'] - df_label['Time Pressed'] 
            time_held = round(df_label['time held'].sum(),4)
            times[label] = time_held
        times['off target'] = round(total_time - sum(times.values()),4)

        total = sum(times.values(),0.0)
        perc = {k: round(v/total,4) for k,v in times.items()}
        print(times)
        print(perc)
        print('-----------------------------------------------------------------------------------------')
