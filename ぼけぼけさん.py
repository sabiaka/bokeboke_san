import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import cv2
import os
import numpy as np  # ← 追加！
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os

# ウィンドウ作成
root = tk.Tk()
root.title("ぼけぼけさん")
root.geometry("500x700")  # 縦長に変更

# アイコン設定
root.iconbitmap("your_icon.ico")

# タイトルラベル
title_label = tk.Label(root, text="ぼけぼけさん", font=("メイリオ", 24))
title_label.pack(pady=10)

# ファイル選択ボタン
def select_files():
    files = filedialog.askopenfilenames(
        title="画像ファイルを選んでね！",
        filetypes=[("画像ファイル", "*.png *.jpg *.jpeg *.bmp")]
    )
    file_listbox.delete(0, tk.END)
    for file in files:
        file_listbox.insert(tk.END, file)
    
    # サムネイルを表示
    display_thumbnails(files)
    
    # 画像が選ばれた場合、選択解除ボタンを有効に
    deselect_btn.config(state=tk.NORMAL)

    # モード1選択時に保存先ボタンをグレーアウト
    if save_option.get() == 1:
        output_select_btn.config(state=tk.DISABLED)
    else:
        output_select_btn.config(state=tk.NORMAL)

# ファイル選択解除ボタン
def deselect_files():
    file_listbox.delete(0, tk.END)
    display_thumbnails([])  # サムネイルをクリア
    
    # 選択解除後、選択解除ボタンを無効に
    deselect_btn.config(state=tk.DISABLED)

    # モード1選択時に保存先ボタンをグレーアウト
    if save_option.get() == 1:
        output_select_btn.config(state=tk.DISABLED)
    else:
        output_select_btn.config(state=tk.NORMAL)

file_select_btn = tk.Button(root, text="画像を選ぶ", command=select_files)
file_select_btn.pack(pady=5)

# 選択解除ボタン（初期状態では無効）
deselect_btn = tk.Button(root, text="選択解除", command=deselect_files, state=tk.DISABLED)
deselect_btn.pack(pady=5)

# 画像サムネイル表示用Canvasとスクロールバー
canvas = tk.Canvas(root, height=120)  # ← 高さだけ固定
canvas.pack(fill=tk.X, padx=10, pady=5)  # ← 横方向だけfill

scrollbar = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
scrollbar.pack(fill=tk.X)
canvas.config(xscrollcommand=scrollbar.set)

thumbnail_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=thumbnail_frame, anchor="nw")

def display_thumbnails(files):
    # サムネイル表示エリアをクリア
    for widget in thumbnail_frame.winfo_children():
        widget.destroy()

    # サムネイル画像を追加
    for file in files:
        img = Image.open(file)
        img.thumbnail((100, 100))  # サムネイルサイズ調整
        img_tk = ImageTk.PhotoImage(img)

        thumbnail_label = tk.Label(thumbnail_frame, image=img_tk)
        thumbnail_label.image = img_tk  # 参照を保持しておかないと消えちゃう
        thumbnail_label.pack(side="left", padx=5)

    # Canvasのスクロール領域を更新
    thumbnail_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# 選択したファイルの表示
file_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, height=5)
file_listbox.pack(fill=tk.X, padx=10, pady=5)

def update_save_button_state():
    if save_option.get() == 1:
        output_select_btn.config(state=tk.DISABLED)
    else:
        output_select_btn.config(state=tk.NORMAL)


# 保存先選択方法（ラジオボタン）
save_option = tk.IntVar(value=1)

save_frame = tk.LabelFrame(root, text="保存方法")
save_frame.pack(fill=tk.X, padx=10, pady=5)

radio1 = tk.Radiobutton(save_frame, text="画像があるとこにフォルダ作って入れる", variable=save_option, value=1, command=update_save_button_state)
radio1.pack(anchor="w", padx=5)

radio2 = tk.Radiobutton(save_frame, text="保存先を指定する", variable=save_option, value=2, command=update_save_button_state)
radio2.pack(anchor="w", padx=5)

# 出力先選択ボタン
def select_output_folder():
    folder = filedialog.askdirectory(title="保存先フォルダを選んでね！")
    if folder:
        output_path.set(folder)

output_path = tk.StringVar()
output_select_btn = tk.Button(root, text="保存先を選ぶ", command=select_output_folder)
output_select_btn.pack(pady=5)

output_entry = tk.Entry(root, textvariable=output_path)
output_entry.pack(fill=tk.X, padx=10, pady=5)

update_save_button_state()  # 初期状態でラジオボタンの状態に応じてボタンを更新

# プログレスバー
progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=10)

def imread_unicode(path):
    # ファイルをバイナリで読み込んでデコード
    data = np.fromfile(path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img

def imwrite_unicode(path, img):
    # 拡張子を自動取得
    ext = os.path.splitext(path)[1]
    # エンコード
    result, enc = cv2.imencode(ext, img)
    if not result:
        raise IOError(f"画像のエンコード失敗: {path}")
    # Unicodeパス対応でバイナリ書き込み
    enc.tofile(path)

def run_blur():
    files = file_listbox.get(0, tk.END)
    if not files:
        messagebox.showwarning("警告", "画像を選んでください！")
        return
    if save_option.get() == 2 and not output_path.get():
        messagebox.showwarning("警告", "保存先フォルダを選んでください！")
        return

    total = len(files)
    progress["maximum"] = total
    saved_folder = ""

    for i, file_path in enumerate(files, 1):
        img = imread_unicode(file_path)
        if img is None:
            print(f"読み込み失敗: {file_path}")
            continue

        height, width = img.shape[:2]

        # 縮小率を計算（ここはお好みで調整）
        scale = 0.1  # 例えば10%サイズまで縮小

        # 縮小
        small_img = cv2.resize(img, (int(width * scale), int(height * scale)))

        # 小さい画像を思いっきりぼかす
        blurred_small = cv2.GaussianBlur(small_img, (99, 99), 0)

        # 元のサイズに拡大
        blurred = cv2.resize(blurred_small, (width, height))

        filename = os.path.basename(file_path)
        name_only = os.path.splitext(filename)[0]


        # OpenCVの画像をPILに変換
        blurred_pil = Image.fromarray(cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB))

        draw = ImageDraw.Draw(blurred_pil)
        filename = os.path.basename(file_path)
        name_only = os.path.splitext(filename)[0]

        # フォントファイル指定（.ttfパス入れてね！）
        font_path = "C:/Windows/Fonts/meiryo.ttc"  # Windowsならメイリオとか
        font_size = int(min(blurred_pil.size) / 6)
        font = ImageFont.truetype(font_path, font_size)

        # テキストサイズ計算して中央座標決定
        bbox = draw.textbbox((0, 0), name_only, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = (blurred_pil.width - text_w) / 2
        text_y = (blurred_pil.height - text_h) / 2

        # ウォーターマーク描画（半透明にするならfill=(255,255,255,128)とかもできる）
        draw.text((text_x, text_y), name_only, font=font, fill=(255,255,255))

        # PIL画像をOpenCVに戻す
        blurred = cv2.cvtColor(np.array(blurred_pil), cv2.COLOR_RGB2BGR)

        if save_option.get() == 1:
            folder = os.path.join(os.path.dirname(file_path), "boked")
            os.makedirs(folder, exist_ok=True)
            saved_folder = folder
        else:
            folder = output_path.get()
            saved_folder = folder

        filename = os.path.basename(file_path)
        filename_boked = os.path.splitext(filename)[0] + "_boked" + os.path.splitext(filename)[1]
        save_path = os.path.join(folder, filename_boked)

        imwrite_unicode(save_path, blurred)

        progress["value"] = i
        root.update_idletasks()

    messagebox.showinfo("完了", f"全部ぼけぼけ完了だよ！\n保存場所: {saved_folder}")
    os.startfile(saved_folder)




run_btn = tk.Button(root, text="ぼかす！", command=run_blur)
run_btn.pack(pady=10)

# フッター Made by 押山
footer_label = tk.Label(root, text="Made by 押山", font=("メイリオ", 9))
footer_label.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5)

# アプリ起動
root.mainloop()
