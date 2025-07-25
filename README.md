# IronGolemPet

> 铁傀儡开凿机，但是桌宠。

![GitHub Repo stars](https://img.shields.io/github/stars/LYOfficial/IronGolemPet?style=flat&logo=github)
![GitHub forks](https://img.shields.io/github/forks/LYOfficial/IronGolemPet?style=flat&logo=github)
![Bitbucket open issues](https://img.shields.io/bitbucket/issues/LYOfficial/IronGolemPet?style=flat&logo=github)
![Bitbucket open pull requests](https://img.shields.io/bitbucket/pr-raw/LYOfficial/IronGolemPet?style=flat&logo=github)

喜欢的话欢迎点个 Star，也欢迎一起 Pr 整点新东西！

<img width="474" height="318" alt="image" src="https://github.com/user-attachments/assets/70fd368a-ced5-41fb-9897-64802b859ba0" />


## 功能特性

- 🎃 **Minecraft风格设计**: 采用 Minecraft 原版方块材质。
- 🦵 **四种动画模式**: 提供四种不同的动画模式，每种都有独特的变化效果
- 🔄 **模式切换**: 右键菜单可以切换不同的动画模式
- 🖱️ **可拖拽**: 可以用鼠标拖拽桌宠到任意位置。
- 🎯 **点击控制**: 点击桌宠会跳跃并切换动画的开始/停止状态。
- ⏰ **整点报时**: 可设置整点自动跳跃提醒。
- ⏲️ **倒计时功能**: 可设置1-60分钟的倒计时，时间到后连续跳跃直到点击。
- 🚀 **开机自启动**: 可设置程序开机自动启动。

## 安装和运行

### 方法1: 直接执行 可执行文件（Windows）
双击 `IronGolemPet.exe` 文件即可启动桌宠。

### 方法2: 命令行运行
```bash
# 安装依赖
pip install -r requirements.txt

# 运行桌宠
python iron_golem.py
```

## 设置选项

### 整点报时
- 启用后，每到整点（如1:00、2:00等）桌宠会自动跳跃一次

### 倒计时提醒  
- 可设置1-60分钟的倒计时
- 时间到达后桌宠会连续跳跃
- 点击桌宠一次即可停止跳跃并重新开始倒计时
- 适合番茄工作法或休息提醒

### 开机自启动
- 启用后程序会随Windows系统启动
- 方便日常使用

## 系统要求

- Python 3.6+
- PyQt5
- Windows/Linux/macOS（开机自启动功能仅支持Windows）
