from PIL import Image
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def select_file():
    filename = filedialog.askopenfilename(
        title="PNGファイルを選択",
        filetypes=[("PNG Files", "*.png")]
    )
    if filename:
        file_var.set(filename)

def convert_image():
    input_file = file_var.get()
    if not input_file:
        messagebox.showerror("エラー", "PNGファイルを選択してください")
        return
    try:
        scale = float(scale_var.get())
    except ValueError:
        messagebox.showerror("エラー", "倍率を数値で入力してください")
        return
    if scale <= 0:
        messagebox.showerror("エラー", "倍率は0より大きい値を入力してください")
        return
    try:
        img = Image.open(input_file)
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
        resized = img.resize(
            (new_width, new_height),
            Image.Resampling.NEAREST
        )
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_x{scale:g}.png"
        resized.save(output_file)
        messagebox.showinfo(
            "完了",
            f"保存しました\n\n{output_file}"
        )

    except Exception as e:
        messagebox.showerror(
            "エラー",
            str(e)
        )

def drop_file(event):
    file_path = event.data
    # WindowsのD&Dでは {} が付くことがある
    file_path = file_path.strip("{}")
    file_var.set(file_path)

# -----------------------
# GUI作成
# -----------------------
root = TkinterDnD.Tk()
root.title("PNG拡大縮小ツール")
root.geometry("600x250")
root.resizable(False, False)
file_var = tk.StringVar()
scale_var = tk.StringVar(value="2")

# D&D用ラベル
drop_label = tk.Label(
    root,
    text="PNGをここへドロップ",
    relief="groove",
    width=40,
    height=4
)
drop_label.grid(
    row=3,
    column=0,
    columnspan=3,
    pady=10
)
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind("<<Drop>>", drop_file)

# ファイル選択
tk.Label(
    root,
    text="PNGファイル"
).grid(
    row=0,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)

tk.Entry(
    root,
    textvariable=file_var,
    width=60
).grid(
    row=0,
    column=1,
    padx=5
)

tk.Button(
    root,
    text="参照",
    command=select_file
).grid(
    row=0,
    column=2,
    padx=5
)
# 倍率入力
tk.Label(
    root,
    text="倍率"
).grid(
    row=1,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)
tk.Entry(
    root,
    textvariable=scale_var,
    width=10
).grid(
    row=1,
    column=1,
    sticky="w"
)
tk.Label(
    root,
    text="例: 2 = 200%, 0.5 = 50%"
).grid(
    row=1,
    column=1,
    padx=80,
    sticky="w"
)
# 実行ボタン
tk.Button(
    root,
    text="変換実行",
    width=20,
    height=2,
    command=convert_image
).grid(
    row=2,
    column=1,
    pady=15
)
root.mainloop()