#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI界面模块
实现记账软件的用户界面
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import font as tkfont
from datetime import datetime
import json
import os

from database import db_manager
from user import User
from category import Category
from transaction import Transaction, SearchCriteria
from budget import Budget
from statistics import Statistics


class FinanceApp(tk.Tk):
    """记账软件主应用类"""

    def __init__(self):
        """初始化应用"""
        super().__init__()
        self.title("个人记账软件")
        self.geometry("1024x768")
        self.minsize(800, 600)
        
        # 设置字体
        self.font_config()
        
        # 当前用户
        self.current_user = None
        
        # 创建样式
        self.style = ttk.Style()
        self.setup_style()
        
        # 创建登录界面
        self.login_frame = None
        self.main_frame = None
        
        # 显示登录界面
        self.show_login()

    def font_config(self):
        """配置字体"""
        try:
            # 配置默认字体
            self.default_font = tkfont.nametofont("TkDefaultFont")
            self.default_font.configure(size=10)
            
            # 配置文本字体
            self.text_font = tkfont.nametofont("TkTextFont")
            self.text_font.configure(size=10)
            
            # 尝试配置消息字体，如果不存在则跳过
            try:
                self.message_font = tkfont.nametofont("TkMessageFont")
                self.message_font.configure(size=10)
            except tk.TclError:
                # TkMessageFont在某些系统中可能不存在
                pass
        except Exception as e:
            # 如果字体配置失败，继续运行程序
            print(f"字体配置失败: {e}")

    def setup_style(self):
        """设置样式"""
        self.style.configure(
            "TButton",
            padding=(10, 5),
            font=('Microsoft YaHei', 10)
        )
        self.style.configure(
            "TLabel",
            font=('Microsoft YaHei', 10),
            padding=(5, 2)
        )
        self.style.configure(
            "TEntry",
            padding=(5, 2),
            font=('Microsoft YaHei', 10)
        )
        self.style.configure(
            "TCombobox",
            padding=(5, 2),
            font=('Microsoft YaHei', 10)
        )
        self.style.configure(
            "Header.TLabel",
            font=('Microsoft YaHei', 16, 'bold'),
            padding=(10, 5)
        )

    def show_login(self):
        """显示登录界面"""
        # 销毁现有界面
        if hasattr(self, 'main_frame') and self.main_frame:
            self.main_frame.destroy()
        
        # 创建登录框架
        self.login_frame = tk.Frame(self)
        self.login_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # 标题
        header = ttk.Label(self.login_frame, text="个人记账软件", style="Header.TLabel")
        header.pack(pady=20)
        
        # 登录表单框架
        form_frame = ttk.Frame(self.login_frame)
        form_frame.pack(pady=20)
        
        # 用户名
        ttk.Label(form_frame, text="用户名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # 密码
        ttk.Label(form_frame, text="密码:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(self.login_frame)
        button_frame.pack(pady=20)
        
        # 登录按钮
        login_btn = ttk.Button(button_frame, text="登录", command=self.handle_login)
        login_btn.pack(side=tk.LEFT, padx=10)
        
        # 注册按钮
        register_btn = ttk.Button(button_frame, text="注册", command=self.handle_register)
        register_btn.pack(side=tk.LEFT, padx=10)
        
        # 退出按钮
        exit_btn = ttk.Button(button_frame, text="退出", command=self.quit)
        exit_btn.pack(side=tk.LEFT, padx=10)

    def handle_login(self):
        """处理登录"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return
        
        user = User(username=username, password=password)
        if user.login():
            self.current_user = user
            self.show_main_interface()
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")

    def handle_register(self):
        """处理注册"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return
        
        # 获取预算
        budget_str = simpledialog.askstring("设置预算", "请输入月度预算（可选）:", parent=self)
        try:
            budget = float(budget_str) if budget_str else 0
        except ValueError:
            budget = 0
        
        user = User(username=username, password=password, monthly_budget=budget)
        if user.register():
            messagebox.showinfo("注册成功", "注册成功，请登录")
        else:
            messagebox.showerror("注册失败", "用户名已存在")

    def show_main_interface(self):
        """显示主界面"""
        # 销毁登录界面
        if self.login_frame:
            self.login_frame.destroy()
        
        # 创建主框架
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主界面布局
        self.create_main_layout()

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="导出数据", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.handle_logout)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 功能菜单
        function_menu = tk.Menu(menubar, tearoff=0)
        function_menu.add_command(label="添加记账", command=self.show_add_transaction)
        function_menu.add_command(label="预算设置", command=self.show_budget_setting)
        function_menu.add_command(label="分类管理", command=self.show_category_management)
        menubar.add_cascade(label="功能", menu=function_menu)
        
        # 统计菜单
        stats_menu = tk.Menu(menubar, tearoff=0)
        stats_menu.add_command(label="日统计", command=lambda: self.show_statistics('daily'))
        stats_menu.add_command(label="月统计", command=lambda: self.show_statistics('monthly'))
        stats_menu.add_command(label="年统计", command=lambda: self.show_statistics('yearly'))
        menubar.add_cascade(label="统计", menu=stats_menu)
        
        # 搜索菜单
        search_menu = tk.Menu(menubar, tearoff=0)
        search_menu.add_command(label="搜索记录", command=self.show_search)
        menubar.add_cascade(label="搜索", menu=search_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        # 设置菜单栏
        self.config(menu=menubar)

    def create_main_layout(self):
        """创建主界面布局"""
        # 顶部状态栏
        status_frame = ttk.Frame(self.main_frame, padding=10)
        status_frame.pack(fill=tk.X)
        
        ttk.Label(status_frame, text=f"欢迎回来，{self.current_user.username}").pack(side=tk.LEFT)
        
        # 检查本月预算
        current_month = datetime.now().strftime('%Y-%m')
        budget = Budget(user_id=self.current_user.user_id, month=current_month)
        budget.update_spent()
        
        budget_str = f"本月预算: ¥{budget.amount:.2f} | 已花费: ¥{budget.spent:.2f} | 剩余: ¥{budget.get_remaining():.2f}"
        if budget.is_overspent():
            budget_str += " (已超支)"
        
        budget_label = ttk.Label(status_frame, text=budget_str, font=('Microsoft YaHei', 10, 'bold'))
        budget_label.pack(side=tk.RIGHT)
        
        # 主内容区域
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧按钮面板
        left_frame = ttk.Frame(content_frame, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 快捷功能按钮
        ttk.Button(left_frame, text="快速记账", command=self.show_add_transaction, width=20).pack(pady=10)
        ttk.Button(left_frame, text="本月统计", command=lambda: self.show_statistics('monthly'), width=20).pack(pady=10)
        ttk.Button(left_frame, text="预算管理", command=self.show_budget_setting, width=20).pack(pady=10)
        ttk.Button(left_frame, text="分类管理", command=self.show_category_management, width=20).pack(pady=10)
        ttk.Button(left_frame, text="搜索记录", command=self.show_search, width=20).pack(pady=10)
        ttk.Button(left_frame, text="导出数据", command=self.export_data, width=20).pack(pady=10)
        
        # 右侧内容区域
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 显示最近交易记录
        self.show_recent_transactions(right_frame)

    def show_recent_transactions(self, parent_frame):
        """显示最近交易记录"""
        # 清除现有内容
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # 标题
        ttk.Label(parent_frame, text="最近交易记录", style="Header.TLabel").pack(fill=tk.X, pady=10)
        
        # 创建表格
        columns = ("date", "amount", "type", "category", "note")
        tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
        
        # 设置列标题
        tree.heading("date", text="日期时间")
        tree.heading("amount", text="金额")
        tree.heading("type", text="类型")
        tree.heading("category", text="分类")
        tree.heading("note", text="备注")
        
        # 设置列宽
        tree.column("date", width=150)
        tree.column("amount", width=100, anchor=tk.E)
        tree.column("type", width=80)
        tree.column("category", width=100)
        tree.column("note", width=200)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        # 布局
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 获取最近的20条交易记录
        transactions = Transaction.get_transactions_by_user(
            user_id=self.current_user.user_id
        )[:20]
        
        # 填充数据
        for trans in transactions:
            # 获取分类名称
            category = Category.get_category_by_id(trans.category_id)
            category_name = category.name if category else "未知"
            
            # 设置金额颜色
            amount_str = f"¥{trans.amount:.2f}"
            
            tree.insert("", tk.END, values=(
                trans.date,
                amount_str,
                trans.type,
                category_name,
                trans.note or ""
            ))
            
        # 保存tree引用，用于后续刷新
        self.transaction_tree = tree
        
    def refresh_transaction_list(self):
        """刷新交易记录列表"""
        if hasattr(self, 'transaction_tree'):
            # 清空现有数据
            for item in self.transaction_tree.get_children():
                self.transaction_tree.delete(item)
            
            # 获取最新的交易记录
            transactions = Transaction.get_transactions_by_user(
                user_id=self.current_user.user_id
            )[:20]
            
            # 重新填充数据
            for trans in transactions:
                # 获取分类名称
                category = Category.get_category_by_id(trans.category_id)
                category_name = category.name if category else "未知"
                
                # 设置金额
                amount_str = f"¥{trans.amount:.2f}"
                
                self.transaction_tree.insert("", tk.END, values=(
                    trans.date,
                    amount_str,
                    trans.type,
                    category_name,
                    trans.note or ""
                ))

    def show_add_transaction(self):
        """显示添加交易记录界面"""
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("添加记账")
        dialog.geometry("600x400")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # 表单框架
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 类型选择
        ttk.Label(form_frame, text="类型:").grid(row=0, column=0, sticky=tk.W, pady=10)
        trans_type = tk.StringVar(value="支出")
        ttk.Radiobutton(form_frame, text="支出", variable=trans_type, value="支出").grid(row=0, column=1, sticky=tk.W, pady=10)
        ttk.Radiobutton(form_frame, text="收入", variable=trans_type, value="收入").grid(row=0, column=2, sticky=tk.W, pady=10)
        
        # 金额
        ttk.Label(form_frame, text="金额:").grid(row=1, column=0, sticky=tk.W, pady=10)
        amount_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=amount_var, width=30).grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=10)
        
        # 分类
        ttk.Label(form_frame, text="分类:").grid(row=2, column=0, sticky=tk.W, pady=10)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=category_var, width=28, state="readonly")
        category_combo.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=10)
        
        # 日期时间
        ttk.Label(form_frame, text="日期时间:").grid(row=3, column=0, sticky=tk.W, pady=10)
        date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        ttk.Entry(form_frame, textvariable=date_var, width=30).grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=10)
        
        # 备注
        ttk.Label(form_frame, text="备注:").grid(row=4, column=0, sticky=tk.NW, pady=10)
        note_text = tk.Text(form_frame, width=40, height=5)
        note_text.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill=tk.X)
        
        def update_categories(*args):
            """更新分类列表"""
            current_type = trans_type.get()
            category_type = "支出类" if current_type == "支出" else "收入类"
            categories = Category.get_all_categories(
                user_id=self.current_user.user_id,
                type=category_type
            )
            
            category_names = []
            self.category_map = {}
            for cat in categories:
                # 使用固定宽度的格式确保分类名称对齐
                # 假设图标和分隔符共占用4个字符宽度
                display_name = f"{cat.icon:<2} {cat.name}" if cat.icon else f"    {cat.name}"
                category_names.append(display_name)
                self.category_map[display_name] = cat.category_id
            
            category_combo['values'] = category_names
            if category_names:
                category_combo.current(0)
        
        # 绑定类型变化事件
        trans_type.trace_add("write", update_categories)
        
        # 初始化分类
        update_categories()
        
        def save_transaction():
            """保存交易记录"""
            # 验证金额
            try:
                amount = float(amount_var.get())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("错误", "请输入有效的金额")
                return
            
            # 获取分类ID
            category_name = category_var.get()
            if not category_name:
                messagebox.showerror("错误", "请选择分类")
                return
            category_id = self.category_map.get(category_name)
            
            # 获取数据
            type_val = trans_type.get()
            date_val = date_var.get()
            note_val = note_text.get("1.0", tk.END).strip()
            
            # 创建交易记录
            transaction = Transaction(
                amount=amount,
                type=type_val,
                category_id=category_id,
                date=date_val,
                note=note_val,
                user_id=self.current_user.user_id
            )
            
            if transaction.add_transaction():
                messagebox.showinfo("成功", "记账成功")
                
                # 检查是否超支
                if type_val == "支出":
                    budget = Budget(
                        user_id=self.current_user.user_id,
                        month=date_val[:7]
                    )
                    if budget.is_overspent():
                        messagebox.showwarning("超支提醒", "本月已超支！")
                
                dialog.destroy()
                # 只刷新交易记录区域，而不是整个主界面
                self.refresh_transaction_list()
            else:
                messagebox.showerror("错误", "记账失败")
        
        # 保存按钮
        save_btn = ttk.Button(button_frame, text="保存", command=save_transaction)
        save_btn.pack(side=tk.RIGHT, padx=10)
        
        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=10)

    def show_budget_setting(self):
        """显示预算设置界面"""
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("预算设置")
        dialog.geometry("600x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 默认月度预算设置
        default_frame = ttk.LabelFrame(main_frame, text="默认月度预算", padding=10)
        default_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(default_frame, text="默认预算金额:").grid(row=0, column=0, sticky=tk.W, pady=10)
        default_budget_var = tk.StringVar(value=str(self.current_user.monthly_budget))
        ttk.Entry(default_frame, textvariable=default_budget_var, width=20).grid(row=0, column=1, sticky=tk.W, pady=10)
        
        # 本月预算设置
        current_month = datetime.now().strftime('%Y-%m')
        current_frame = ttk.LabelFrame(main_frame, text=f"{current_month} 预算", padding=10)
        current_frame.pack(fill=tk.X, pady=10)
        
        # 获取本月预算
        current_budget = Budget(user_id=self.current_user.user_id, month=current_month)
        current_budget.update_spent()
        
        ttk.Label(current_frame, text="本月预算:").grid(row=0, column=0, sticky=tk.W, pady=5)
        month_budget_var = tk.StringVar(value=str(current_budget.amount))
        ttk.Entry(current_frame, textvariable=month_budget_var, width=20).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(current_frame, text="已花费:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(current_frame, text=f"¥{current_budget.spent:.2f}").grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(current_frame, text="剩余预算:").grid(row=2, column=0, sticky=tk.W, pady=5)
        remaining = current_budget.get_remaining()
        remaining_text = f"¥{remaining:.2f}"
        if remaining < 0:
            remaining_text += " (超支)"
        ttk.Label(current_frame, text=remaining_text).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill=tk.X)
        
        def save_budget():
            """保存预算设置"""
            try:
                # 保存默认预算
                default_budget = float(default_budget_var.get())
                if default_budget < 0:
                    raise ValueError
                self.current_user.set_budget(default_budget)
                
                # 保存本月预算
                month_budget = float(month_budget_var.get())
                if month_budget < 0:
                    raise ValueError
                current_budget.amount = month_budget
                current_budget.save()
                
                messagebox.showinfo("成功", "预算设置成功")
                dialog.destroy()
                # 刷新主界面
                self.create_main_layout()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的金额")
        
        # 保存按钮
        save_btn = ttk.Button(button_frame, text="保存", command=save_budget)
        save_btn.pack(side=tk.RIGHT, padx=10)
        
        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=10)

    def show_category_management(self):
        """显示分类管理界面"""
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("分类管理")
        dialog.geometry("700x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 分类类型选择
        type_frame = ttk.Frame(main_frame)
        type_frame.pack(fill=tk.X, pady=10)
        
        category_type = tk.StringVar(value="支出类")
        ttk.Radiobutton(type_frame, text="支出分类", variable=category_type, value="支出类").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(type_frame, text="收入分类", variable=category_type, value="收入类").pack(side=tk.LEFT, padx=20)
        
        # 分类列表
        columns = ("name", "icon", "is_custom")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        tree.heading("name", text="分类名称")
        tree.heading("icon", text="图标")
        tree.heading("is_custom", text="类型")
        
        tree.column("name", width=200)
        tree.column("icon", width=100)
        tree.column("is_custom", width=100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        # 布局
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill=tk.X)
        
        def update_category_list():
            """更新分类列表"""
            # 清空现有数据
            for item in tree.get_children():
                tree.delete(item)
            
            # 获取分类
            categories = Category.get_all_categories(
                user_id=self.current_user.user_id,
                type=category_type.get()
            )
            
            # 填充数据
            for cat in categories:
                type_text = "自定义" if cat.is_custom else "预设"
                tree.insert("", tk.END, values=(
                    cat.name,
                    cat.icon or "",
                    type_text
                ), tags=(cat.category_id, cat.is_custom))
        
        def add_category():
            """添加自定义分类"""
            name = simpledialog.askstring("添加分类", "请输入分类名称:", parent=dialog)
            if not name:
                return
            
            icon = simpledialog.askstring("添加图标", "请输入图标（可选）:", parent=dialog)
            
            category = Category(
                name=name,
                type=category_type.get(),
                icon=icon,
                user_id=self.current_user.user_id
            )
            
            if category.add_custom_category():
                messagebox.showinfo("成功", "分类添加成功")
                update_category_list()
            else:
                messagebox.showerror("错误", "分类添加失败")
        
        def delete_category():
            """删除分类"""
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("提示", "请选择要删除的分类")
                return
            
            item = selected[0]
            category_id = tree.item(item, "tags")[0]
            is_custom = tree.item(item, "tags")[1]
            
            if not is_custom:
                messagebox.showwarning("提示", "预设分类不能删除")
                return
            
            if messagebox.askyesno("确认", "确定要删除这个分类吗？"):
                category = Category(category_id=category_id, user_id=self.current_user.user_id)
                if category.delete():
                    messagebox.showinfo("成功", "分类删除成功")
                    update_category_list()
                else:
                    messagebox.showerror("错误", "该分类下有交易记录，不能删除")
        
        # 绑定类型变化事件
        category_type.trace_add("write", lambda *args: update_category_list())
        
        # 添加和删除按钮
        add_btn = ttk.Button(button_frame, text="添加分类", command=add_category)
        add_btn.pack(side=tk.RIGHT, padx=10)
        
        delete_btn = ttk.Button(button_frame, text="删除分类", command=delete_category)
        delete_btn.pack(side=tk.RIGHT, padx=10)
        
        # 关闭按钮
        close_btn = ttk.Button(button_frame, text="关闭", command=dialog.destroy)
        close_btn.pack(side=tk.RIGHT, padx=10)
        
        # 初始化列表
        update_category_list()

    def show_statistics(self, stats_type='monthly'):
        """显示统计界面"""
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title(f"{stats_type}统计")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 时间选择
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill=tk.X, pady=10)
        
        if stats_type == 'daily':
            ttk.Label(time_frame, text="选择日期:").pack(side=tk.LEFT, padx=10)
            date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
            ttk.Entry(time_frame, textvariable=date_var, width=20).pack(side=tk.LEFT, padx=10)
        elif stats_type == 'monthly':
            ttk.Label(time_frame, text="选择月份:").pack(side=tk.LEFT, padx=10)
            date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m'))
            ttk.Entry(time_frame, textvariable=date_var, width=20).pack(side=tk.LEFT, padx=10)
        else:
            ttk.Label(time_frame, text="选择年份:").pack(side=tk.LEFT, padx=10)
            date_var = tk.StringVar(value=datetime.now().strftime('%Y'))
            ttk.Entry(time_frame, textvariable=date_var, width=20).pack(side=tk.LEFT, padx=10)
        
        # 刷新按钮
        ttk.Button(time_frame, text="刷新", command=lambda: show_stats()).pack(side=tk.LEFT, padx=10)
        
        # 统计结果显示
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        def show_stats():
            """显示统计结果"""
            # 清除现有内容
            for widget in result_frame.winfo_children():
                widget.destroy()
            
            # 创建统计对象
            stats = Statistics(user_id=self.current_user.user_id)
            
            # 获取统计数据
            if stats_type == 'daily':
                result = stats.calculate_daily_stats(date_var.get())
            elif stats_type == 'monthly':
                result = stats.calculate_monthly_stats(date_var.get())
            else:
                result = stats.calculate_yearly_stats(date_var.get())
            
            if not result:
                ttk.Label(result_frame, text="暂无数据").pack(pady=50)
                return
            
            # 显示总览
            overview_frame = ttk.LabelFrame(result_frame, text="收支总览", padding=10)
            overview_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(overview_frame, text=f"总收入: ¥{result['total_income']:.2f}", font=('Microsoft YaHei', 12, 'bold')).pack(side=tk.LEFT, padx=30, pady=10)
            ttk.Label(overview_frame, text=f"总支出: ¥{result['total_expense']:.2f}", font=('Microsoft YaHei', 12, 'bold')).pack(side=tk.LEFT, padx=30, pady=10)
            ttk.Label(overview_frame, text=f"结余: ¥{result['balance']:.2f}", font=('Microsoft YaHei', 12, 'bold')).pack(side=tk.LEFT, padx=30, pady=10)
            
            # 分类统计
            category_frame = ttk.LabelFrame(result_frame, text="分类统计", padding=10)
            category_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # 支出分类
            expense_frame = ttk.LabelFrame(category_frame, text="支出分类", padding=10)
            expense_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=5, pady=5)
            
            # 创建表格
            expense_columns = ("category", "amount", "percentage")
            expense_tree = ttk.Treeview(expense_frame, columns=expense_columns, show="headings")
            
            expense_tree.heading("category", text="分类")
            expense_tree.heading("amount", text="金额")
            expense_tree.heading("percentage", text="占比")
            
            expense_tree.column("category", width=100)
            expense_tree.column("amount", width=100, anchor=tk.E)
            expense_tree.column("percentage", width=80, anchor=tk.CENTER)
            
            # 滚动条
            expense_scrollbar = ttk.Scrollbar(expense_frame, orient=tk.VERTICAL, command=expense_tree.yview)
            expense_tree.configure(yscroll=expense_scrollbar.set)
            
            expense_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            expense_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 收入分类
            income_frame = ttk.LabelFrame(category_frame, text="收入分类", padding=10)
            income_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=5, pady=5)
            
            # 创建表格
            income_columns = ("category", "amount", "percentage")
            income_tree = ttk.Treeview(income_frame, columns=income_columns, show="headings")
            
            income_tree.heading("category", text="分类")
            income_tree.heading("amount", text="金额")
            income_tree.heading("percentage", text="占比")
            
            income_tree.column("category", width=100)
            income_tree.column("amount", width=100, anchor=tk.E)
            income_tree.column("percentage", width=80, anchor=tk.CENTER)
            
            # 滚动条
            income_scrollbar = ttk.Scrollbar(income_frame, orient=tk.VERTICAL, command=income_tree.yview)
            income_tree.configure(yscroll=income_scrollbar.set)
            
            income_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            income_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 填充数据
            # 支出数据
            total_expense = result['total_expense']
            for item in result['category_stats']['expense']:
                percentage = (item['amount'] / total_expense * 100) if total_expense > 0 else 0
                display_name = f"{item['icon']} {item['name']}" if item['icon'] else item['name']
                expense_tree.insert("", tk.END, values=(
                    display_name,
                    f"¥{item['amount']:.2f}",
                    f"{percentage:.1f}%"
                ))
            
            # 收入数据
            total_income = result['total_income']
            for item in result['category_stats']['income']:
                percentage = (item['amount'] / total_income * 100) if total_income > 0 else 0
                display_name = f"{item['icon']} {item['name']}" if item['icon'] else item['name']
                income_tree.insert("", tk.END, values=(
                    display_name,
                    f"¥{item['amount']:.2f}",
                    f"{percentage:.1f}%"
                ))
        
        # 显示统计
        show_stats()
        
        # 关闭按钮
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="关闭", command=dialog.destroy).pack(side=tk.RIGHT, padx=10)

    def show_search(self):
        """显示搜索界面"""
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("搜索记录")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # 搜索条件框架
        search_frame = ttk.LabelFrame(dialog, text="搜索条件", padding=20)
        search_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # 开始日期
        ttk.Label(search_frame, text="开始日期:").grid(row=0, column=0, sticky=tk.W, pady=10, padx=10)
        start_date_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=start_date_var, width=20).grid(row=0, column=1, sticky=tk.W, pady=10)
        
        # 结束日期
        ttk.Label(search_frame, text="结束日期:").grid(row=0, column=2, sticky=tk.W, pady=10, padx=10)
        end_date_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=end_date_var, width=20).grid(row=0, column=3, sticky=tk.W, pady=10)
        
        # 交易类型
        ttk.Label(search_frame, text="交易类型:").grid(row=1, column=0, sticky=tk.W, pady=10, padx=10)
        type_var = tk.StringVar(value="全部")
        type_combo = ttk.Combobox(search_frame, textvariable=type_var, values=["全部", "收入", "支出"], width=18, state="readonly")
        type_combo.grid(row=1, column=1, sticky=tk.W, pady=10)
        
        # 金额范围
        ttk.Label(search_frame, text="最小金额:").grid(row=1, column=2, sticky=tk.W, pady=10, padx=10)
        min_amount_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=min_amount_var, width=20).grid(row=1, column=3, sticky=tk.W, pady=10)
        
        ttk.Label(search_frame, text="最大金额:").grid(row=2, column=0, sticky=tk.W, pady=10, padx=10)
        max_amount_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=max_amount_var, width=20).grid(row=2, column=1, sticky=tk.W, pady=10)
        
        # 搜索按钮
        ttk.Button(search_frame, text="搜索", command=lambda: perform_search()).grid(row=2, column=3, pady=10, padx=10)
        
        # 结果显示框架
        result_frame = ttk.Frame(dialog)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # 创建表格
        columns = ("date", "amount", "type", "category", "note")
        tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        
        tree.heading("date", text="日期时间")
        tree.heading("amount", text="金额")
        tree.heading("type", text="类型")
        tree.heading("category", text="分类")
        tree.heading("note", text="备注")
        
        tree.column("date", width=150)
        tree.column("amount", width=100, anchor=tk.E)
        tree.column("type", width=80)
        tree.column("category", width=100)
        tree.column("note", width=200)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮框架
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill=tk.X)
        
        def perform_search():
            """执行搜索"""
            # 清空现有数据
            for item in tree.get_children():
                tree.delete(item)
            
            # 获取搜索条件
            start_date = start_date_var.get()
            end_date = end_date_var.get()
            trans_type = None if type_var.get() == "全部" else type_var.get()
            
            # 解析金额
            try:
                min_amount = float(min_amount_var.get()) if min_amount_var.get() else None
            except ValueError:
                messagebox.showerror("错误", "最小金额格式错误")
                return
            
            try:
                max_amount = float(max_amount_var.get()) if max_amount_var.get() else None
            except ValueError:
                messagebox.showerror("错误", "最大金额格式错误")
                return
            
            # 构建搜索条件
            criteria = SearchCriteria(
                start_date=start_date,
                end_date=end_date,
                min_amount=min_amount,
                max_amount=max_amount
            )
            
            # 执行搜索
            transactions = Transaction.get_transactions_by_user(
                user_id=self.current_user.user_id,
                start_date=start_date,
                end_date=end_date,
                transaction_type=trans_type,
                min_amount=min_amount,
                max_amount=max_amount
            )
            
            # 填充结果
            for trans in transactions:
                # 获取分类名称
                category = Category.get_category_by_id(trans.category_id)
                category_name = category.name if category else "未知"
                
                tree.insert("", tk.END, values=(
                    trans.date,
                    f"¥{trans.amount:.2f}",
                    trans.type,
                    category_name,
                    trans.note or ""
                ))
        
        # 关闭按钮
        ttk.Button(button_frame, text="关闭", command=dialog.destroy).pack(side=tk.RIGHT, padx=10)

    def export_data(self):
        """导出数据"""
        try:
            # 获取所有交易记录
            transactions = Transaction.get_transactions_by_user(user_id=self.current_user.user_id)
            
            # 获取所有预算
            budgets = Budget.get_all_budgets(user_id=self.current_user.user_id)
            
            # 整理数据
            export_data = {
                'user': {
                    'username': self.current_user.username,
                    'monthly_budget': self.current_user.monthly_budget
                },
                'transactions': [],
                'budgets': []
            }
            
            # 添加交易记录
            for trans in transactions:
                category = Category.get_category_by_id(trans.category_id)
                export_data['transactions'].append({
                    'id': trans.transaction_id,
                    'date': trans.date,
                    'amount': trans.amount,
                    'type': trans.type,
                    'category': category.name if category else "未知",
                    'note': trans.note
                })
            
            # 添加预算
            for budget in budgets:
                export_data['budgets'].append({
                    'month': budget.month,
                    'amount': budget.amount,
                    'spent': budget.spent
                })
            
            # 生成文件名
            filename = f"finance_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(os.getcwd(), filename)
            
            # 保存数据
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", f"数据已导出至: {filepath}")
        except Exception as e:
            messagebox.showerror("错误", f"导出数据失败: {str(e)}")

    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于",
            "个人记账软件 v1.0\n\n"
            "功能特性:\n"
            "- 个人记账管理\n"
            "- 预算设置与超支提醒\n"
            "- 收支统计分析\n"
            "- 分类管理\n"
            "- 数据导出\n\n"
            "© 2025 个人记账软件"
        )

    def handle_logout(self):
        """处理退出登录"""
        if messagebox.askyesno("确认", "确定要退出登录吗？"):
            self.current_user = None
            self.show_login()


if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()