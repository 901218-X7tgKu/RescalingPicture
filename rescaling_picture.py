from PIL import Image
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

# -----------------------
# 状態
# -----------------------
file_list = []  # 追加されたファイルの絶対パス一覧


# -----------------------
# ファイル操作
# -----------------------
def add_files(paths):
    added = 0
    for p in paths:
        p = p.strip("{}")
        if not p.lower().endswith(".png"):
            continue
        if p in file_list:
            continue
        file_list.append(p)
        listbox.insert(tk.END, os.path.basename(p))
        added += 1
    update_status(f"{added}件追加しました（合計 {len(file_list)}件）")


def browse_files():
    paths = filedialog.askopenfilenames(
        title="PNGファイルを選択（複数選択可）",
        filetypes=[("PNG Files", "*.png")]
    )
    if paths:
        add_files(paths)


def remove_selected():
    selected = list(listbox.curselection())
    if not selected:
        return
    for idx in reversed(selected):
        listbox.delete(idx)
        del file_list[idx]
    update_status(f"選択項目を削除しました（合計 {len(file_list)}件）")


def clear_list():
    listbox.delete(0, tk.END)
    file_list.clear()
    update_status("リストをクリアしました")


def drop_files(event):
    paths = root.tk.splitlist(event.data)
    add_files(paths)


# -----------------------
# 保存先フォルダ
# -----------------------
def toggle_output_folder():
    if same_folder_var.get():
        output_entry.config(state="disabled")
        output_browse_btn.config(state="disabled")
    else:
        output_entry.config(state="normal")
        output_browse_btn.config(state="normal")


def select_output_folder():
    folder = filedialog.askdirectory(title="保存先フォルダを選択")
    if folder:
        output_var.set(folder)


# -----------------------
# ステータス表示
# -----------------------
def update_status(text):
    status_var.set(text)


# -----------------------
# 変換処理
# -----------------------
def convert_all():
    if not file_list:
        messagebox.showerror("エラー", "PNGファイルを追加してください")
        return

    try:
        scale = float(scale_var.get())
    except ValueError:
        messagebox.showerror("エラー", "倍率を数値で入力してください")
        return
    if scale <= 0:
        messagebox.showerror("エラー", "倍率は0より大きい値を入力してください")
        return

    if not same_folder_var.get():
        out_folder = output_var.get()
        if not out_folder:
            messagebox.showerror("エラー", "保存先フォルダを選択してください")
            return
        if not os.path.isdir(out_folder):
            messagebox.showerror("エラー", "保存先フォルダが存在しません")
            return
    else:
        out_folder = None

    total = len(file_list)
    success = 0
    errors = []

    progress_bar["maximum"] = total
    progress_bar["value"] = 0

    for i, input_file in enumerate(file_list, start=1):
        update_status(f"変換中... ({i}/{total}) {os.path.basename(input_file)}")
        root.update_idletasks()
        try:
            img = Image.open(input_file)
            new_width = int(img.width * scale)
            new_height = int(img.height * scale)
            resized = img.resize(
                (new_width, new_height),
                Image.Resampling.NEAREST
            )
            base = os.path.splitext(os.path.basename(input_file))[0]
            target_folder = out_folder if out_folder else os.path.dirname(input_file)
            output_file = os.path.join(target_folder, f"{base}_x{scale:g}.png")
            resized.save(output_file)
            success += 1
        except Exception as e:
            errors.append(f"{os.path.basename(input_file)}: {e}")

        progress_bar["value"] = i
        root.update_idletasks()

    if errors:
        update_status(f"完了: 成功 {success}件 / 失敗 {len(errors)}件")
        messagebox.showwarning(
            "一部失敗しました",
            f"成功: {success}件\n失敗: {len(errors)}件\n\n" + "\n".join(errors[:10])
        )
    else:
        update_status(f"完了: {success}件すべて変換しました")
        messagebox.showinfo("完了", f"{success}件のファイルを変換しました")


# -----------------------
# GUI作成
# -----------------------
root = TkinterDnD.Tk()
root.title("PNG拡大縮小ツール（複数ファイル対応）")
root.geometry("460x560")
root.resizable(False, False)

scale_var = tk.StringVar(value="2")
same_folder_var = tk.BooleanVar(value=True)
output_var = tk.StringVar()
status_var = tk.StringVar(value="PNGファイルを追加してください")

main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack(fill="both", expand=True)

tk.Label(main_frame, text="対象PNGファイル一覧", font=("", 10, "bold")).pack(anchor="w")

list_frame = tk.Frame(main_frame, relief="groove", borderwidth=2)
list_frame.pack(pady=5, fill="x")

listbox = tk.Listbox(list_frame, width=45, height=14, selectmode="extended")
listbox.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(list_frame, command=listbox.yview)
scrollbar.pack(side="right", fill="y")
listbox.config(yscrollcommand=scrollbar.set)

list_frame.drop_target_register(DND_FILES)
list_frame.dnd_bind("<<Drop>>", drop_files)
listbox.drop_target_register(DND_FILES)
listbox.dnd_bind("<<Drop>>", drop_files)

drop_hint = tk.Label(
    main_frame,
    text="↑ ここへPNGをドラッグ＆ドロップ（複数可）",
    fg="gray"
)
drop_hint.pack(anchor="w")

btn_frame = tk.Frame(main_frame)
btn_frame.pack(pady=8, anchor="w")

tk.Button(btn_frame, text="ファイル追加", command=browse_files).pack(side="left", padx=3)
tk.Button(btn_frame, text="選択項目を削除", command=remove_selected).pack(side="left", padx=3)
tk.Button(btn_frame, text="全てクリア", command=clear_list).pack(side="left", padx=3)

# 倍率
scale_frame = tk.Frame(main_frame)
scale_frame.pack(pady=10, anchor="w")
tk.Label(scale_frame, text="倍率").pack(side="left")
tk.Entry(scale_frame, textvariable=scale_var, width=8).pack(side="left", padx=5)
tk.Label(scale_frame, text="例: 2 = 200%, 0.5 = 50%", fg="gray").pack(side="left")

# 保存先
output_frame = tk.LabelFrame(main_frame, text="保存先", padx=8, pady=8)
output_frame.pack(pady=5, fill="x")

tk.Checkbutton(
    output_frame,
    text="元のファイルと同じ場所に保存",
    variable=same_folder_var,
    command=toggle_output_folder
).pack(anchor="w")

out_row = tk.Frame(output_frame)
out_row.pack(fill="x", pady=3)
output_entry = tk.Entry(out_row, textvariable=output_var, width=32, state="disabled")
output_entry.pack(side="left", padx=(0, 5))
output_browse_btn = tk.Button(
    out_row, text="参照", command=select_output_folder, state="disabled"
)
output_browse_btn.pack(side="left")

# 実行ボタン & 進捗
tk.Button(
    main_frame,
    text="変換実行",
    width=20,
    height=2,
    bg="#4a90d9",
    fg="white",
    command=convert_all
).pack(pady=10)

progress_bar = ttk.Progressbar(main_frame, length=300, mode="determinate")
progress_bar.pack(pady=3)

tk.Label(main_frame, textvariable=status_var, fg="#333").pack(anchor="w")

toggle_output_folder()

root.mainloop()
