import csv


def read_csv(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        label = next(reader)[0]  # 1行目のラベル
        data = [float(row[0]) for row in reader]  # 2行目以降のデータ
    return label, data
