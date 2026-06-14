# -*- coding: utf-8 -*-
"""
轻量桌面工具栏 - 美化版
- 边缘吸附，自动隐藏
- 鼠标悬停滑出
- 快捷软件/文件夹/网页
- 可编辑分类
- 拖拽添加到分类
- 文件夹可展开查看内容
"""

import sys
import os
import json
import webbrowser
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea, QMenu,
    QDialog, QLineEdit, QComboBox, QFileDialog, QListWidget,
    QListWidgetItem, QMessageBox, QGraphicsDropShadowEffect, QSizePolicy, QSlider
)
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal, QRect
from PyQt5.QtGui import QCursor, QColor, QFont

CONFIG_FILE = Path(os.path.dirname(os.path.abspath(__file__))) / "config" / "toolbar.json" if '__file__' in globals() else Path(r"C:\Users\Administrator\.openclaw\workspace\desktop-organizer\config\toolbar.json")

# 配色方案
COLORS = {
    'bg': '#f8f9fa',
    'card': '#ffffff',
    'primary': '#4a90d9',
    'primary_light': '#e8f4fd',
    'text': '#333333',
    'text_secondary': '#666666',
    'border': '#e0e0e0',
    'hover': '#f0f7ff',
    'shadow': 'rgba(0, 0, 0, 0.08)'
}

# 默认字体大小
DEFAULT_FONT_SIZE = 13


class EditDialog(QDialog):
    """编辑对话框"""
    
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.setWindowTitle("添加快捷项")
        self.setFixedSize(320, 180)
        self.item = item
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {COLORS['card']};
            }}
            QLabel {{
                color: {COLORS['text']};
                font-size: 12px;
            }}
            QLineEdit, QComboBox {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px;
                background: {COLORS['bg']};
                font-size: 12px;
            }}
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: #3a7bc8;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["文件夹", "软件", "网页"])
        layout.addWidget(QLabel("类型:"))
        layout.addWidget(self.type_combo)
        
        self.name_input = QLineEdit()
        layout.addWidget(QLabel("名称:"))
        layout.addWidget(self.name_input)
        
        self.path_input = QLineEdit()
        layout.addWidget(QLabel("路径/网址:"))
        layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.setStyleSheet(f"background: {COLORS['text_secondary']};")
        browse_btn.clicked.connect(self.browse)
        layout.addWidget(browse_btn)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(f"background: {COLORS['text_secondary']};")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        if item:
            self.name_input.setText(item['name'])
            self.path_input.setText(item['path'])
            self.type_combo.setCurrentText(item['type'])
    
    def browse(self):
        type_ = self.type_combo.currentText()
        if type_ == "文件夹":
            path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        elif type_ == "软件":
            path = QFileDialog.getOpenFileName(self, "选择程序", "", "程序 (*.exe)")[0]
        else:
            return
        if path:
            self.path_input.setText(path)
            if not self.name_input.text():
                self.name_input.setText(Path(path).name)
    
    def get_data(self):
        return {
            'type': self.type_combo.currentText(),
            'name': self.name_input.text(),
            'path': self.path_input.text()
        }


class CategoryDialog(QDialog):
    """分类编辑对话框"""
    
    def __init__(self, parent=None, categories=None):
        super().__init__(parent)
        self.setWindowTitle("管理分类")
        self.setFixedSize(280, 350)
        
        self.setStyleSheet(f"""
            QDialog {{ background: {COLORS['card']}; }}
            QLabel {{ color: {COLORS['text']}; font-size: 12px; }}
            QListWidget {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                background: {COLORS['bg']};
            }}
            QLineEdit {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px;
            }}
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        
        self.cat_list = QListWidget()
        if categories:
            for cat in categories:
                self.cat_list.addItem(cat)
        layout.addWidget(QLabel("分类列表:"))
        layout.addWidget(self.cat_list)
        
        self.input = QLineEdit()
        layout.addWidget(QLabel("新分类名:"))
        layout.addWidget(self.input)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.add_cat)
        del_btn = QPushButton("删除")
        del_btn.setStyleSheet(f"background: #e74c3c;")
        del_btn.clicked.connect(self.del_cat)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)
        
        ok_btn = QPushButton("完成")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)
    
    def add_cat(self):
        name = self.input.text().strip()
        if name:
            self.cat_list.addItem(name)
            self.input.clear()
    
    def del_cat(self):
        item = self.cat_list.currentItem()
        if item:
            self.cat_list.takeItem(self.cat_list.row(item))
    
    def get_categories(self):
        return [self.cat_list.item(i).text() for i in range(self.cat_list.count())]


class CategoryLabel(QFrame):
    """分类标签"""
    
    item_dropped = pyqtSignal(str, str)
    
    def __init__(self, text, category, font_size=DEFAULT_FONT_SIZE, parent=None):
        super().__init__(parent)
        self.category = category
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['primary_light']};
                border-radius: 6px;
                border: none;
            }}
            QFrame:hover {{
                background: #d0e8fc;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        
        self.label = QLabel(f"▼ {text}")
        self.label.setStyleSheet(f"font-size: {font_size}px; font-weight: 600; color: {COLORS['primary']};")
        layout.addWidget(self.label)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(f"""
                QFrame {{
                    background: {COLORS['primary']};
                    border-radius: 6px;
                }}
            """)
            self.label.setStyleSheet("font-size: 12px; font-weight: 600; color: white;")
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['primary_light']};
                border-radius: 6px;
            }}
            QFrame:hover {{
                background: #d0e8fc;
            }}
        """)
        self.label.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLORS['primary']};")
    
    def dropEvent(self, event):
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['primary_light']};
                border-radius: 6px;
            }}
            QFrame:hover {{
                background: #d0e8fc;
            }}
        """)
        self.label.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLORS['primary']};")
        
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            self.item_dropped.emit(path, self.category)


class FolderContentWidget(QWidget):
    """文件夹内容展示"""
    
    def __init__(self, folder_path, font_size=DEFAULT_FONT_SIZE, parent=None):
        super().__init__(parent)
        self.folder_path = folder_path
        self.font_size = font_size
        
        self.setStyleSheet(f"""
            QWidget {{
                background: transparent;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 2, 4, 2)
        layout.setSpacing(0)
        
        self.file_list = QListWidget()
        self.file_list.setFrameShape(QFrame.NoFrame)
        self.file_list.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['bg']};
                border-radius: 6px;
                border: 1px solid {COLORS['border']};
            }}
            QListWidget::item {{
                padding: 6px 10px;
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                font-size: {font_size - 1}px;
            }}
            QListWidget::item:hover {{
                background: {COLORS['primary_light']};
            }}
        """)
        # 自动调整高度，不限制
        self.file_list.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        self.file_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.file_list.itemDoubleClicked.connect(self.open_item)
        layout.addWidget(self.file_list)
        
        self.load_contents()
    
    def load_contents(self):
        self.file_list.clear()
        try:
            items = sorted(os.listdir(self.folder_path))[:30]  # 显示前30个
            for item in items:
                full_path = os.path.join(self.folder_path, item)
                if os.path.isdir(full_path):
                    icon = "📁"
                else:
                    ext = Path(item).suffix.lower()
                    if ext == '.exe':
                        icon = "⚙"
                    elif ext in ['.txt', '.md', '.doc', '.pdf', '.docx']:
                        icon = "📄"
                    elif ext in ['.jpg', '.png', '.gif', '.bmp']:
                        icon = "🖼"
                    elif ext in ['.mp4', '.avi', '.mkv']:
                        icon = "🎬"
                    elif ext in ['.mp3', '.wav', '.flac']:
                        icon = "🎵"
                    elif ext in ['.zip', '.rar', '.7z']:
                        icon = "📦"
                    else:
                        icon = "📄"
                list_item = QListWidgetItem(f"{icon} {item}")
                list_item.setData(Qt.UserRole, full_path)
                self.file_list.addItem(list_item)
        except:
            self.file_list.addItem("⚠ 无法读取")
    
    def open_item(self, item):
        path = item.data(Qt.UserRole)
        if path and os.path.exists(path):
            os.startfile(path)


class ExpandableFolderButton(QWidget):
    """可展开的文件夹按钮"""
    
    def __init__(self, name, path, font_size=DEFAULT_FONT_SIZE, parent=None):
        super().__init__(parent)
        self.path = path
        self.name = name
        self.font_size = font_size
        self.is_expanded = False
        
        self.setStyleSheet(f"""
            QWidget {{
                background: transparent;
            }}
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 按钮行
        btn_widget = QWidget()
        btn_widget.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                border-radius: 6px;
            }}
            QWidget:hover {{
                background: {COLORS['hover']};
            }}
        """)
        btn_widget.setFixedHeight(26)
        btn_row = QHBoxLayout(btn_widget)
        btn_row.setContentsMargins(2, 0, 4, 0)
        btn_row.setSpacing(0)
        
        self.expand_btn = QPushButton("▶")
        self.expand_btn.setFixedSize(18, 22)
        self.expand_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                font-size: 8px;
                color: {COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                color: {COLORS['primary']};
            }}
        """)
        self.expand_btn.clicked.connect(self.toggle_expand)
        btn_row.addWidget(self.expand_btn)
        
        self.main_btn = QPushButton(f"📁 {name}")
        self.main_btn.setToolTip(path)
        self.main_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                text-align: left;
                padding: 2px 2px;
                font-size: {font_size}px;
                color: {COLORS['text']};
            }}
            QPushButton:hover {{
                color: {COLORS['primary']};
            }}
        """)
        self.main_btn.clicked.connect(self.open_folder)
        btn_row.addWidget(self.main_btn)
        
        self.main_layout.addWidget(btn_widget)
        
        self.content_widget = None
    
    def toggle_expand(self):
        if self.is_expanded:
            self.expand_btn.setText("▶")
            if self.content_widget:
                self.content_widget.hide()
                self.content_widget.deleteLater()
                self.content_widget = None
            self.is_expanded = False
        else:
            self.expand_btn.setText("▼")
            self.content_widget = FolderContentWidget(self.path, self.font_size)
            self.main_layout.addWidget(self.content_widget)
            self.is_expanded = True
    
    def open_folder(self):
        if os.path.exists(self.path):
            os.startfile(self.path)


class QuickButton(QPushButton):
    """快捷按钮"""
    
    def __init__(self, name, path, type_, font_size=DEFAULT_FONT_SIZE, parent=None):
        super().__init__(parent)
        self.path = path
        self.type_ = type_
        
        icons = {'软件': '⚙', '网页': '🔗'}
        self.setText(f"{icons.get(type_, '📄')} {name}")
        self.setToolTip(path)
        
        self.setFixedHeight(28)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                text-align: left;
                padding: 6px 12px;
                font-size: {font_size}px;
                color: {COLORS['text']};
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: {COLORS['hover']};
                color: {COLORS['primary']};
            }}
        """)
        
        self.clicked.connect(self.open)
    
    def open(self):
        if self.type_ == '网页':
            webbrowser.open(self.path)
        elif os.path.exists(self.path):
            subprocess.Popen(self.path)
        else:
            QMessageBox.warning(self, "错误", f"路径不存在: {self.path}")


class ToolbarWidget(QWidget):
    """工具栏主窗口"""
    
    EDGE_WIDTH = 8
    SHOW_WIDTH = 240
    HIDE_DELAY = 300  # 隐藏延迟毫秒
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        self.position = 'left'
        self.font_size = DEFAULT_FONT_SIZE  # 字体大小
        self.is_hidden = True
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.do_hide)
        
        self.hover_timer = QTimer()
        self.hover_timer.timeout.connect(self.check_hover)
        self.hover_timer.start(100)
        
        self.load_config()
        self.init_ui()
        self.snap_to_edge()
    
    def load_config(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                self.font_size = self.config.get('font_size', DEFAULT_FONT_SIZE)
        else:
            self.config = {
                'position': 'left',
                'font_size': DEFAULT_FONT_SIZE,
                'categories': ['常用', '工作', '工具'],
                'items': {
                    '常用': [
                        {'type': '文件夹', 'name': '桌面', 'path': str(Path.home() / 'Desktop')},
                        {'type': '文件夹', 'name': '下载', 'path': str(Path.home() / 'Downloads')},
                    ],
                    '工作': [],
                    '工具': []
                }
            }
            self.save_config()
    
    def save_config(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def init_ui(self):
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 4)
        self.main_frame.setGraphicsEffect(shadow)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.addWidget(self.main_frame)
        
        frame_layout = QVBoxLayout(self.main_frame)
        frame_layout.setContentsMargins(12, 12, 12, 12)
        frame_layout.setSpacing(8)
        
        # 标题栏
        header = QHBoxLayout()
        title = QLabel("⚡ 快捷工具")
        title.setStyleSheet(f"font-size: {self.font_size + 1}px; font-weight: 700; color: {COLORS['text']};")
        header.addWidget(title)
        header.addStretch()
        
        # 字体大小滑块
        font_slider = QSlider(Qt.Horizontal)
        font_slider.setRange(10, 18)
        font_slider.setValue(self.font_size)
        font_slider.setFixedWidth(80)
        font_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {COLORS['bg']};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['primary']};
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }}
        """)
        font_slider.valueChanged.connect(self.change_font_size)
        header.addWidget(font_slider)
        
        self.font_label = QLabel(f"{self.font_size}")
        self.font_label.setStyleSheet(f"font-size: 11px; color: {COLORS['text_secondary']}; min-width: 20px;")
        header.addWidget(self.font_label)
        
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(28, 28)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg']};
                border: none;
                border-radius: 14px;
                font-size: 14px;
                color: {COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                background: {COLORS['primary_light']};
                color: {COLORS['primary']};
            }}
        """)
        settings_btn.clicked.connect(self.show_settings)
        header.addWidget(settings_btn)
        frame_layout.addLayout(header)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background: transparent; border: none;")
        
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(6)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self.content)
        frame_layout.addWidget(scroll)
        
        # 提示
        tip = QLabel("💡 拖拽文件到分类添加")
        tip.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        frame_layout.addWidget(tip)
        
        self.refresh_content()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def refresh_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for cat in self.config['categories']:
            cat_label = CategoryLabel(cat, cat, self.font_size)
            cat_label.item_dropped.connect(self.handle_drop)
            cat_label.setContextMenuPolicy(Qt.CustomContextMenu)
            cat_label.customContextMenuRequested.connect(lambda pos, c=cat: self.show_cat_menu(c))
            self.content_layout.addWidget(cat_label)
            
            items = self.config['items'].get(cat, [])
            for item in items:
                if item['type'] == '文件夹':
                    btn = ExpandableFolderButton(item['name'], item['path'], self.font_size)
                else:
                    btn = QuickButton(item['name'], item['path'], item['type'], self.font_size)
                
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, i=item, c=cat: self.show_item_menu(i, c))
                self.content_layout.addWidget(btn)
        
        self.content_layout.addStretch()
    
    def handle_drop(self, path, category):
        if os.path.isdir(path):
            item_type = '文件夹'
        elif os.path.isfile(path):
            if path.lower().endswith('.exe'):
                item_type = '软件'
            elif path.lower().endswith(('.url', '.website')):
                item_type = '网页'
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('URL='):
                                path = line[4:].strip()
                                break
                except:
                    pass
            else:
                item_type = '文件夹'
        else:
            return
        
        name = Path(path).name
        self.config['items'].setdefault(category, []).append({
            'type': item_type,
            'name': name,
            'path': path
        })
        self.save_config()
        self.refresh_content()
    
    def show_context_menu(self, pos):
        menu = self.create_menu()
        menu.exec_(QCursor.pos())
    
    def show_cat_menu(self, cat):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
                color: {COLORS['text']};
            }}
            QMenu::item:hover {{
                background: {COLORS['primary_light']};
            }}
        """)
        menu.addAction("➕ 添加快捷项", lambda: self.add_item_to_cat(cat))
        menu.addAction("✏️ 重命名", lambda: self.rename_cat(cat))
        menu.addAction("🗑️ 删除分类", lambda: self.delete_cat(cat))
        menu.exec_(QCursor.pos())
    
    def show_item_menu(self, item, cat):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
                color: {COLORS['text']};
            }}
            QMenu::item:hover {{
                background: {COLORS['primary_light']};
            }}
        """)
        menu.addAction("✏️ 编辑", lambda: self.edit_item(item, cat))
        menu.addAction("🗑️ 删除", lambda: self.delete_item(item, cat))
        menu.exec_(QCursor.pos())
    
    def create_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
                color: {COLORS['text']};
            }}
            QMenu::item:hover {{
                background: {COLORS['primary_light']};
            }}
            QMenu::separator {{
                height: 1px;
                background: {COLORS['border']};
                margin: 4px 8px;
            }}
        """)
        
        menu.addAction("➕ 添加快捷项", self.add_item)
        menu.addAction("📁 管理分类", self.edit_categories)
        menu.addSeparator()
        
        pos_menu = menu.addMenu("📍 位置")
        for edge in ['左边', '右边', '顶部', '底部']:
            pos_menu.addAction(edge, lambda e=edge: self.set_position(e))
        
        menu.addSeparator()
        menu.addAction("❌ 关闭工具栏", self.close)
        
        return menu
    
    def add_item(self):
        dlg = EditDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            cat = self.config['categories'][0]
            self.config['items'].setdefault(cat, []).append(data)
            self.save_config()
            self.refresh_content()
    
    def add_item_to_cat(self, cat):
        dlg = EditDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            self.config['items'].setdefault(cat, []).append(data)
            self.save_config()
            self.refresh_content()
    
    def edit_item(self, item, cat):
        dlg = EditDialog(self, item)
        if dlg.exec_() == QDialog.Accepted:
            items = self.config['items'][cat]
            idx = items.index(item)
            items[idx] = dlg.get_data()
            self.save_config()
            self.refresh_content()
    
    def delete_item(self, item, cat):
        self.config['items'][cat].remove(item)
        self.save_config()
        self.refresh_content()
    
    def edit_categories(self):
        dlg = CategoryDialog(self, self.config['categories'])
        if dlg.exec_() == QDialog.Accepted:
            new_cats = dlg.get_categories()
            new_items = {}
            for cat in new_cats:
                new_items[cat] = self.config['items'].get(cat, [])
            self.config['categories'] = new_cats
            self.config['items'] = new_items
            self.save_config()
            self.refresh_content()
    
    def rename_cat(self, cat):
        from PyQt5.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "重命名", "新名称:", text=cat)
        if ok and name:
            idx = self.config['categories'].index(cat)
            self.config['categories'][idx] = name
            self.config['items'][name] = self.config['items'].pop(cat, [])
            self.save_config()
            self.refresh_content()
    
    def delete_cat(self, cat):
        if QMessageBox.question(self, "确认", f"删除分类 '{cat}'？") == QMessageBox.Yes:
            self.config['categories'].remove(cat)
            self.config['items'].pop(cat, None)
            self.save_config()
            self.refresh_content()
    
    def change_font_size(self, size):
        """改变字体大小"""
        self.font_size = size
        self.config['font_size'] = size
        self.save_config()
        self.font_label.setText(f"{size}")
        self.refresh_content()
    
    def set_position(self, edge):
        pos_map = {'左边': 'left', '右边': 'right', '顶部': 'top', '底部': 'bottom'}
        self.position = pos_map[edge]
        self.config['position'] = self.position
        self.save_config()
        self.snap_to_edge()
    
    def show_settings(self):
        menu = self.create_menu()
        menu.exec_(QCursor.pos())
    
    def snap_to_edge(self):
        screen = QApplication.primaryScreen().geometry()
        
        if self.position == 'left':
            self.setGeometry(0, 0, self.EDGE_WIDTH, screen.height())
        elif self.position == 'right':
            self.setGeometry(screen.width() - self.EDGE_WIDTH, 0, self.EDGE_WIDTH, screen.height())
        elif self.position == 'top':
            self.setGeometry(0, 0, screen.width(), self.EDGE_WIDTH)
        else:
            self.setGeometry(0, screen.height() - self.EDGE_WIDTH, screen.width(), self.EDGE_WIDTH)
    
    def check_hover(self):
        pos = QCursor.pos()
        
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        
        if self.is_hidden:
            # 隐藏状态：检测是否在边缘触发区域
            trigger_zone = self.get_trigger_zone(screen)
            if trigger_zone.contains(pos):
                self.hide_timer.stop()
                self.slide_in()
                self.is_hidden = False
        else:
            # 展开状态：检测是否离开面板
            panel_rect = self.get_panel_rect()
            if panel_rect.contains(pos):
                # 鼠标在面板内，取消隐藏计时
                self.hide_timer.stop()
            else:
                # 鼠标离开面板，启动隐藏计时
                if not self.hide_timer.isActive():
                    self.hide_timer.start(self.HIDE_DELAY)
    
    def get_trigger_zone(self, screen):
        """获取边缘触发区域"""
        if self.position == 'left':
            return QRect(0, 0, self.EDGE_WIDTH, screen.height())
        elif self.position == 'right':
            return QRect(screen.width() - self.EDGE_WIDTH, 0, self.EDGE_WIDTH, screen.height())
        elif self.position == 'top':
            return QRect(0, 0, screen.width(), self.EDGE_WIDTH)
        else:
            return QRect(0, screen.height() - self.EDGE_WIDTH, screen.width(), self.EDGE_WIDTH)
    
    def get_panel_rect(self):
        """获取面板实际区域（用于检测鼠标是否在面板内）"""
        rect = self.main_frame.geometry()
        # 转换为全局坐标
        top_left = self.main_frame.mapToGlobal(QPoint(0, 0))
        rect.moveTo(top_left)
        return rect
    
    def do_hide(self):
        """执行隐藏"""
        pos = QCursor.pos()
        panel_rect = self.get_panel_rect()
        
        # 再次确认鼠标不在面板内
        if not panel_rect.contains(pos):
            self.slide_out()
            self.is_hidden = True
    
    def slide_in(self):
        screen = QApplication.primaryScreen().geometry()
        
        if self.position == 'left':
            self.setGeometry(0, 0, self.SHOW_WIDTH, screen.height())
        elif self.position == 'right':
            self.setGeometry(screen.width() - self.SHOW_WIDTH, 0, self.SHOW_WIDTH, screen.height())
        elif self.position == 'top':
            self.setGeometry(0, 0, screen.width(), min(450, screen.height() // 2))
        else:
            self.setGeometry(0, screen.height() - min(450, screen.height() // 2), screen.width(), min(450, screen.height() // 2))
    
    def slide_out(self):
        self.snap_to_edge()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    toolbar = ToolbarWidget()
    toolbar.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()