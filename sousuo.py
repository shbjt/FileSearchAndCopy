import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re


class FileSearchAndCopy:
    def __init__(self, root):
        self.root = root
        self.root.title("文件批量搜索与复制工具")
        self.root.geometry("700x500")

        # 变量初始化
        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.file_list_path = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # 源文件夹选择
        ttk.Label(self.root, text="源文件夹:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.source_folder, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="浏览", command=self.select_source_folder).grid(row=0, column=2, padx=5, pady=5)

        # 目标文件夹选择
        ttk.Label(self.root, text="目标文件夹:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.dest_folder, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="浏览", command=self.select_dest_folder).grid(row=1, column=2, padx=5, pady=5)

        # 文件列表选择
        ttk.Label(self.root, text="文件名列表文件:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.file_list_path, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="浏览", command=self.select_file_list).grid(row=2, column=2, padx=5, pady=5)
        ttk.Label(self.root, text="(TXT文件，每行一个或多个文件名)").grid(row=3, column=1, padx=5, pady=0, sticky="w")

        # 搜索选项
        self.search_option = tk.StringVar(value="exact")
        ttk.Label(self.root, text="匹配模式:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(self.root, text="精确匹配", variable=self.search_option, value="exact").grid(row=4, column=1,
                                                                                                     padx=5, pady=5,
                                                                                                     sticky="w")
        ttk.Radiobutton(self.root, text="包含匹配", variable=self.search_option, value="contains").grid(row=4, column=2,
                                                                                                        padx=5, pady=5,
                                                                                                        sticky="w")

        # 进度条
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.grid(row=5, column=0, columnspan=3, padx=5, pady=10, sticky="ew")

        # 按钮
        ttk.Button(self.root, text="开始搜索并复制", command=self.start_process).grid(row=6, column=1, padx=5, pady=10)

        # 结果文本框
        ttk.Label(self.root, text="操作结果:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        self.result_text = tk.Text(self.root, height=15, width=80)
        self.result_text.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # 配置网格权重
        self.root.grid_rowconfigure(8, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def select_source_folder(self):
        folder = filedialog.askdirectory(title="选择源文件夹")
        if folder:
            self.source_folder.set(folder)

    def select_dest_folder(self):
        folder = filedialog.askdirectory(title="选择目标文件夹")
        if folder:
            self.dest_folder.set(folder)

    def select_file_list(self):
        file_path = filedialog.askopenfilename(
            title="选择文件名列表文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.file_list_path.set(file_path)

    def parse_file_list(self):
        file_list_path = self.file_list_path.get()
        if not file_list_path:
            messagebox.showerror("错误", "请先选择文件名列表文件")
            return []

        if not os.path.exists(file_list_path):
            messagebox.showerror("错误", "文件名列表文件不存在")
            return []

        try:
            with open(file_list_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 使用正则表达式提取所有可能的文件名（数字序列，可能有点号和扩展名）
            pattern = r'\b\d{8,15}(?:\.\w+)?\b'
            file_names = re.findall(pattern, content)

            # 去重并返回
            return list(set(file_names))
        except Exception as e:
            messagebox.showerror("错误", f"读取文件列表时出错: {str(e)}")
            return []

    def search_files(self, file_names):
        source_dir = self.source_folder.get()
        search_option = self.search_option.get()

        if not source_dir:
            messagebox.showerror("错误", "请先选择源文件夹")
            return []

        if not file_names:
            messagebox.showerror("错误", "没有找到有效的文件名")
            return []

        matched_files = []

        # 遍历源文件夹
        for root_dir, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root_dir, file)

                # 根据匹配模式搜索文件
                if search_option == "exact":
                    # 精确匹配：文件名必须完全等于列表中的某个名称
                    if file in file_names:
                        matched_files.append(file_path)
                else:
                    # 包含匹配：文件名包含列表中的某个名称
                    for name in file_names:
                        if name in file:
                            matched_files.append(file_path)
                            break  # 找到一个匹配就跳出内层循环

        return matched_files

    def start_process(self):
        # 清空结果文本框
        self.result_text.delete(1.0, tk.END)

        # 解析文件名列表
        self.result_text.insert(tk.END, "正在解析文件名列表...\n")
        self.root.update()

        file_names = self.parse_file_list()
        if not file_names:
            return

        self.result_text.insert(tk.END, f"从列表中解析出 {len(file_names)} 个文件名\n")

        # 搜索文件
        self.result_text.insert(tk.END, "正在搜索文件...\n")
        self.root.update()

        matched_files = self.search_files(file_names)

        if not matched_files:
            self.result_text.insert(tk.END, "没有找到匹配的文件。\n")
            return

        self.result_text.insert(tk.END, f"找到 {len(matched_files)} 个匹配的文件。\n")
        self.result_text.insert(tk.END, "开始复制文件...\n")
        self.root.update()

        # 设置进度条
        self.progress['maximum'] = len(matched_files)
        self.progress['value'] = 0

        # 确保目标文件夹存在
        dest_dir = self.dest_folder.get()
        if not dest_dir:
            messagebox.showerror("错误", "请先选择目标文件夹")
            return

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # 复制文件
        copied_count = 0
        for i, file_path in enumerate(matched_files):
            try:
                # 保持原文件名
                filename = os.path.basename(file_path)
                dest_path = os.path.join(dest_dir, filename)

                # 处理重名文件
                counter = 1
                base, ext = os.path.splitext(filename)
                while os.path.exists(dest_path):
                    new_filename = f"{base}_{counter}{ext}"
                    dest_path = os.path.join(dest_dir, new_filename)
                    counter += 1

                shutil.copy2(file_path, dest_path)
                copied_count += 1
                self.result_text.insert(tk.END, f"已复制: {filename} -> {os.path.basename(dest_path)}\n")
            except Exception as e:
                self.result_text.insert(tk.END, f"复制失败 {os.path.basename(file_path)}: {str(e)}\n")

            # 更新进度条
            self.progress['value'] = i + 1
            self.root.update()

        self.result_text.insert(tk.END, f"\n操作完成！成功复制 {copied_count} 个文件。\n")

        # 显示未找到的文件
        found_files = [os.path.basename(path) for path in matched_files]
        not_found = [name for name in file_names if name not in found_files]

        if not_found:
            self.result_text.insert(tk.END, f"\n以下 {len(not_found)} 个文件未找到:\n")
            for name in not_found:
                self.result_text.insert(tk.END, f"{name}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchAndCopy(root)
    root.mainloop()