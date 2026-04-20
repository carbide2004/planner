# Daily Planner

每30分钟强制弹窗提醒的自律工具。

## 安装

```bash
pip install pystray Pillow
```

## 启动

```bash
python main.py
```

## 打包成 exe（可选）

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile main.py
```

打包完成后 exe 在 `dist/main.exe`，可以重命名为 `DailyPlanner.exe`。

## 使用说明

- **开机自启**：勾选右下角「开机自启」即自动写入注册表
- **每日计划**：每天第一次启动自动弹出计划填写窗口，每行一个任务
- **勾选完成**：点击任务行任意位置即可切换完成/未完成
- **编辑计划**：点击右上角「✎ 编辑」随时修改，已完成状态会保留
- **关闭窗口**：点 × 只是最小化到任务栏（安装 pystray 后进系统托盘），提醒仍然运行
- **退出程序**：系统托盘图标右键 → 退出

## 文件结构

```
planner/
├── main.py        # 主程序
├── storage.py     # JSON 数据读写
├── autostart.py   # 注册表开机自启
├── requirements.txt
└── data/
    └── today.json # 当日计划（自动生成）
```
