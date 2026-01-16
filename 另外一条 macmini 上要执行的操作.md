### 当前 Mac（已配置完成）

- 每次登录自动同步
- 每天 8:00、12:00、18:00、22:00 自动同步
- 手动同步：
    
    ```bash
    cd ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/second_brain/obsidian/project/apple_to_goolge
    ./run_sync.sh
    ```
    

### 另一台 Mac mini

等 iCloud 同步完成后，运行：

```bash
bash ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/second_brain/obsidian/project/apple_to_goolge/install_on_new_mac.sh
```

### 查看日志

```bash
cat ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/second_brain/obsidian/project/apple_to_goolge/sync.log
```

### 管理命令

```bash
# 停止服务
launchctl unload ~/Library/LaunchAgents/com.zhaolei.calendar-sync.plist

# 启动服务
launchctl load ~/Library/LaunchAgents/com.zhaolei.calendar-sync.plist

# 立即手动触发一次
launchctl start com.zhaolei.calendar-sync
```

接下来我要做什么?

一切都已配置完成！你现在不需要做任何事情了。

## 当前状态

|项目|状态|
|---|---|
|同步脚本|✅ 已测试成功，同步了 5 个事件|
|开机自启动|✅ 已配置，每次登录自动运行|
|定时同步|✅ 每天 8:00、12:00、18:00、22:00|

---

## 你可以做的可选操作

### 1. 在另一台 Mac mini 上安装

等 iCloud 同步完成后，在另一台 Mac 上运行：

```bash
bash ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/second_brain/obsidian/project/apple_to_goolge/install_on_new_mac.sh
```

### 2. 验证 Google Calendar

打开 [https://calendar.google.com](https://calendar.google.com/) 确认事件已同步过去。

### 3. 手动触发同步（任何时候想同步时）

```bash
launchctl start com.zhaolei.calendar-sync
```

---

就这些！以后 iCloud 日历有任何增删改，都会自动同步到 Google Calendar。