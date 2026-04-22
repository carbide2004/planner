# Daily Planner

每间隔一定时间强制弹窗提醒的自律规划工具。

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
pyinstaller --noconsole --onefile -i planner.ico --add-data "planner.ico;." main.py
```

打包完成后 exe 在 `dist/main.exe`，可以重命名为 `DailyPlanner.exe`。

## 使用说明

- **开机自启**：勾选右下角「开机自启」即自动写入注册表
- **每日计划**：每天第一次启动自动弹出计划填写窗口，每行一个任务
- **任务顺延**：昨日未完成的任务会自动结转顺延到今天
- **勾选完成**：点击任务行任意位置即可切换完成/未完成
- **编辑计划**：点击右上角「✎ 编辑」随时修改，已完成状态会保留
- **历史总结**：点击右上角「📊 总结」可以查看最近一周任务完成情况的折线图
- **主题切换**：点击右上角「🌙/☀️」图标可以切换亮/暗色主题
- **关闭窗口**：点 × 只是最小化到任务栏（安装 pystray 后进系统托盘），提醒仍然运行
- **退出程序**：系统托盘图标右键 → 退出

## 文件结构

```
planner/
├── main.py        # 主程序
├── storage.py     # JSON 数据读写
├── autostart.py   # 注册表开机自启
├── planner.ico    # 图标
├── single_instance.py # 单例模式
├── requirements.txt
└── data/
    └── <datetime>.json # 当日计划（自动生成）
```
