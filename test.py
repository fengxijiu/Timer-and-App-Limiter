import os
import sys

if getattr(sys, 'frozen', False):
    # 打包后的路径
    base_path = sys._MEIPASS
else:
    # 源代码路径
    base_path = os.path.dirname(os.path.abspath(__file__))

print(base_path)