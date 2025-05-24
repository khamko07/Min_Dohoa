import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản Lý Công Việc Cá Nhân")
        self.root.geometry("1000x800")
        
        # Khởi tạo biến
        self.tasks = []
        self.current_theme = "light"
        
        # Tạo style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Tạo main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.setup_ui()
        self.load_tasks()
        
    def setup_ui(self):
        # Task input frame
        input_frame = ttk.LabelFrame(self.main_container, text="Thêm Công Việc Mới")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Title
        ttk.Label(input_frame, text="Tiêu đề:").grid(row=0, column=0, padx=5, pady=5)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Description
        ttk.Label(input_frame, text="Mô tả:").grid(row=1, column=0, padx=5, pady=5)
        self.desc_entry = ttk.Entry(input_frame, width=30)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Priority
        ttk.Label(input_frame, text="Mức độ ưu tiên:").grid(row=2, column=0, padx=5, pady=5)
        self.priority_var = tk.StringVar(value="Trung bình")
        priority_combo = ttk.Combobox(input_frame, textvariable=self.priority_var)
        priority_combo['values'] = ('Cao', 'Trung bình', 'Thấp')
        priority_combo.grid(row=2, column=1, padx=5, pady=5)
        
        # Add button
        add_btn = ttk.Button(input_frame, text="Thêm công việc", command=self.add_task)
        add_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Search and Filter frame
        search_frame = ttk.LabelFrame(self.main_container, text="Tìm kiếm và Lọc")
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Search
        ttk.Label(search_frame, text="Tìm kiếm:").grid(row=0, column=0, padx=5, pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_tasks)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Filter by status
        ttk.Label(search_frame, text="Lọc theo trạng thái:").grid(row=0, column=2, padx=5, pady=5)
        self.status_filter_var = tk.StringVar(value="Tất cả")
        status_filter_combo = ttk.Combobox(search_frame, textvariable=self.status_filter_var)
        status_filter_combo['values'] = ('Tất cả', 'Chưa làm', 'Đang làm', 'Đã hoàn thành')
        status_filter_combo.grid(row=0, column=3, padx=5, pady=5)
        status_filter_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_tasks())
        
        # Filter by priority
        ttk.Label(search_frame, text="Lọc theo ưu tiên:").grid(row=0, column=4, padx=5, pady=5)
        self.priority_filter_var = tk.StringVar(value="Tất cả")
        priority_filter_combo = ttk.Combobox(search_frame, textvariable=self.priority_filter_var)
        priority_filter_combo['values'] = ('Tất cả', 'Cao', 'Trung bình', 'Thấp')
        priority_filter_combo.grid(row=0, column=5, padx=5, pady=5)
        priority_filter_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_tasks())
        
        # Task list
        list_frame = ttk.LabelFrame(self.main_container, text="Danh Sách Công Việc")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Treeview
        columns = ('status', 'title', 'description', 'priority')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Define headings
        self.tree.heading('status', text='Trạng thái')
        self.tree.heading('title', text='Tiêu đề')
        self.tree.heading('description', text='Mô tả')
        self.tree.heading('priority', text='Ưu tiên')
        
        # Define columns
        self.tree.column('status', width=100)
        self.tree.column('title', width=200)
        self.tree.column('description', width=300)
        self.tree.column('priority', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click event for status toggle
        self.tree.bind('<Double-1>', self.toggle_task_status)
        
        # Add buttons for edit and delete
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        edit_btn = ttk.Button(btn_frame, text="Sửa", command=self.edit_task)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(btn_frame, text="Xóa", command=self.delete_task)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar frame
        progress_frame = ttk.LabelFrame(self.main_container, text="Tiến Độ Công Việc")
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                          maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
    def add_task(self):
        title = self.title_entry.get()
        description = self.desc_entry.get()
        priority = self.priority_var.get()
        
        if not title:
            messagebox.showerror("Lỗi", "Vui lòng nhập tiêu đề công việc!")
            return
            
        task = {
            'title': title,
            'description': description,
            'priority': priority,
            'status': 'Chưa làm',
            'date': datetime.now().strftime("%Y-%m-%d")
        }
        
        self.tasks.append(task)
        self.update_task_list()
        self.save_tasks()
        
        # Clear entries
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        
    def update_task_list(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add tasks to treeview
        for task in self.tasks:
            status_text = self.get_status_text(task['status'])
            self.tree.insert('', tk.END, values=(
                status_text,
                task['title'],
                task['description'],
                task['priority']
            ))
            
        # Update progress bar
        completed = sum(1 for task in self.tasks if task['status'] == 'Đã hoàn thành')
        total = len(self.tasks)
        if total > 0:
            progress = (completed / total) * 100
            self.progress_var.set(progress)
            
    def get_status_text(self, status):
        if status == 'Chưa làm':
            return '⬜ Chưa làm'
        elif status == 'Đang làm':
            return '🔄 Đang làm'
        else:
            return '✅ Đã hoàn thành'
            
    def toggle_task_status(self, event):
        # Get the clicked item
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
            
        # Get the column clicked
        column = self.tree.identify_column(event.x)
        if column != '#1':  # Only toggle if clicking the status column
            return
            
        # Get task index
        index = self.tree.index(item)
        task = self.tasks[index]
        
        # Toggle status
        if task['status'] == 'Chưa làm':
            task['status'] = 'Đang làm'
        elif task['status'] == 'Đang làm':
            task['status'] = 'Đã hoàn thành'
        else:
            task['status'] = 'Chưa làm'
            
        self.update_task_list()
        self.save_tasks()
            
    def filter_tasks(self, *args):
        search_text = self.search_var.get().lower()
        status_filter = self.status_filter_var.get()
        priority_filter = self.priority_filter_var.get()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Filter and add tasks
        for task in self.tasks:
            # Check search text
            if search_text and search_text not in task['title'].lower() and search_text not in task['description'].lower():
                continue
                
            # Check status filter
            if status_filter != 'Tất cả' and task['status'] != status_filter:
                continue
                
            # Check priority filter
            if priority_filter != 'Tất cả' and task['priority'] != priority_filter:
                continue
                
            status_text = self.get_status_text(task['status'])
            self.tree.insert('', tk.END, values=(
                status_text,
                task['title'],
                task['description'],
                task['priority']
            ))
            
    def edit_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn công việc cần sửa!")
            return
            
        # Get task index
        index = self.tree.index(selected_item[0])
        task = self.tasks[index]
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Sửa Công Việc")
        edit_window.geometry("400x300")
        
        # Add entry fields
        ttk.Label(edit_window, text="Tiêu đề:").pack(padx=5, pady=5)
        title_entry = ttk.Entry(edit_window, width=30)
        title_entry.insert(0, task['title'])
        title_entry.pack(padx=5, pady=5)
        
        ttk.Label(edit_window, text="Mô tả:").pack(padx=5, pady=5)
        desc_entry = ttk.Entry(edit_window, width=30)
        desc_entry.insert(0, task['description'])
        desc_entry.pack(padx=5, pady=5)
        
        ttk.Label(edit_window, text="Mức độ ưu tiên:").pack(padx=5, pady=5)
        priority_var = tk.StringVar(value=task['priority'])
        priority_combo = ttk.Combobox(edit_window, textvariable=priority_var)
        priority_combo['values'] = ('Cao', 'Trung bình', 'Thấp')
        priority_combo.pack(padx=5, pady=5)
        
        def save_changes():
            task['title'] = title_entry.get()
            task['description'] = desc_entry.get()
            task['priority'] = priority_var.get()
            self.update_task_list()
            self.save_tasks()
            edit_window.destroy()
            
        ttk.Button(edit_window, text="Lưu thay đổi", command=save_changes).pack(pady=10)
        
    def delete_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn công việc cần xóa!")
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa công việc này?"):
            index = self.tree.index(selected_item[0])
            del self.tasks[index]
            self.update_task_list()
            self.save_tasks()
            
    def save_tasks(self):
        with open('tasks.json', 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=4)
            
    def load_tasks(self):
        try:
            with open('tasks.json', 'r', encoding='utf-8') as f:
                self.tasks = json.load(f)
                self.update_task_list()
        except FileNotFoundError:
            self.tasks = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
