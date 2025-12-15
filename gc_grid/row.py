import os
import glob
import csv

# 현재 파일이 있는 디렉토리
base_dir = os.path.dirname(__file__)

# dat숫자.dat 패턴 파일 전부 찾기
dat_files = sorted(glob.glob(os.path.join(base_dir, "dat*.dat")))

output_csv = os.path.join(base_dir, "dat_row_counts.csv")

with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["filename", "row_count"])

    for filepath in dat_files:
        try:
            with open(filepath, "r") as df:
                row_count = sum(1 for _ in df)
            writer.writerow([os.path.basename(filepath), row_count])
        except Exception as e:
            writer.writerow([os.path.basename(filepath), f"ERROR: {e}"])

print(f"Saved row counts to {output_csv}")
