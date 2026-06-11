import os
import shutil

src_path = r"c:\Users\skc\AppData\Local\Packages\5319275A.WhatsAppDesktop_cv1g1gvanyjgm\LocalState\sessions\84870F41E7E67D5E96A93357DE7492ADABC7565F\transfers\2026-24\pureweaves-full-bug-report.md"
dest_path = r"c:\Users\skc\Desktop\Handcrafted-with-Love-Pure-Weaves-main\scratch\pureweaves-full-bug-report.md"

if os.path.exists(src_path):
    shutil.copy(src_path, dest_path)
    print("Successfully copied full bug report to scratch/pureweaves-full-bug-report.md")
else:
    print("Source path does not exist:", src_path)
