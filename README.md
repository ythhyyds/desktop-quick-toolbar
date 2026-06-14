# 桌面快捷工具栏 (Desktop Quick Toolbar)

一个轻量级的 Windows 桌面快捷工具栏，支持边缘吸附、自动隐藏、拖拽添加等功能。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 功能特点

- 🎯 **边缘吸附** - 自动吸附到屏幕四边，支持左/右/上/下四个方向
- 👻 **自动隐藏** - 鼠标离开自动隐藏，悬停边缘自动展开
- 📁 **快捷文件夹** - 添加常用文件夹，一键打开
- ⚙️ **快捷软件** - 添加常用软件，快速启动
- 🔗 **网页书签** - 添加网页链接，一键打开
- 📂 **文件夹展开** - 点击展开查看文件夹内容，双击打开文件
- 🎨 **拖拽添加** - 拖拽文件/文件夹到分类，自动添加
- 📂 **分类管理** - 自定义分类，灵活管理

## 📸 截图

![工具栏截图](screenshots/toolbar.png)

## 🚀 快速开始

### 环境要求

- Windows 10/11
- Python 3.8+
- PyQt5

### 安装依赖

```bash
pip install PyQt5
```

### 运行

双击 `启动.bat` 或命令行运行：

```bash
python main.py
```

## 📖 使用说明

### 基本操作

| 操作 | 说明 |
|------|------|
| 鼠标移到屏幕边缘 | 工具栏自动滑出 |
| 鼠标移开 | 工具栏自动隐藏 |
| 右键点击 | 打开菜单，添加/编辑项目 |
| 拖拽文件到分类 | 自动添加到该分类 |
| 点击 ▶ 展开 | 查看文件夹内容 |
| 双击文件 | 打开文件 |

### 添加快捷项

1. 右键点击空白处 → 选择「添加快捷项」
2. 选择类型（文件夹/软件/网页）
3. 输入名称和路径，或点击「浏览」选择
4. 点击「确定」

### 管理分类

右键点击 → 「管理分类」→ 添加/删除/重命名分类

### 切换位置

右键点击 → 「位置」→ 选择左边/右边/顶部/底部

## ⚙️ 配置文件

配置保存在 `config/toolbar.json`：

```json
{
  "position": "left",
  "categories": ["常用", "工作", "工具"],
  "items": {
    "常用": [
      {"type": "文件夹", "name": "桌面", "path": "C:\\Users\\...\\Desktop"}
    ]
  }
}
```

## 🛠️ 技术栈

- **Python 3** - 编程语言
- **PyQt5** - GUI 框架
- **Qt.FramelessWindowHint** - 无边框窗口
- **Qt.WindowStaysOnTopHint** - 置顶显示

## 📝 开发计划

- [ ] 支持图标自定义
- [ ] 支持搜索功能
- [ ] 支持主题切换
- [ ] 支持快捷键唤起
- [ ] 支持多屏显示

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[MIT License](LICENSE)

## 👤 作者

- GitHub: [@ythhyyds](https://github.com/ythhyyds)

---

⭐ 如果这个项目对你有帮助，欢迎 Star！