import sys
import random
import json
import os
import winreg
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QSpinBox, QMessageBox, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, QTime
from PyQt5.QtGui import QPainter, QColor, QFont, QCursor, QPixmap, QPolygon, QIcon

def resource_path(relative_path):
    """获取资源文件的绝对路径，支持开发环境和PyInstaller打包环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包环境
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境
    return os.path.join(os.path.abspath("."), relative_path)

class IronGolem(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setupAnimations()
        self.setupLegAnimation()
        
    def initUI(self):
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 预加载tk.png图片
        self.loadBlockTexture()
        
        # 设置桌宠大小 (根据模式调整高度)
        self.golem_width = 160
        self.golem_height = 280  # 增加高度以适应模式2的四行
        self.setFixedSize(self.golem_width, self.golem_height)
        
        # 设置初始位置到屏幕右侧居中偏下
        screen = QApplication.desktop().screenGeometry()
        start_x = screen.width() - self.golem_width - 50  # 距离右边缘50像素
        start_y = screen.height() // 2 + 100  # 居中偏下
        self.move(start_x, start_y)
        
        # 拖拽相关变量
        self.dragging = False
        self.drag_position = QPoint()
        
        # 系统托盘
        self.setupSystemTray()
        
        # 动画状态
        self.is_moving = False
        self.leg_animation_running = False
        self.leg_state = 0  # 0和1之间切换
        self.animation_mode = 1  # 1-4种动画模式，默认模式1
        
        # 设置相关
        self.loadSettings()
        self.setupTimers()
        
    def setupLegAnimation(self):
        # 腿部动画定时器
        self.leg_timer = QTimer()
        self.leg_timer.timeout.connect(self.switchLegState)
        # 不自动启动，等待用户点击
        
        # 如果倒计时启用，开始倒计时
        if hasattr(self, 'settings') and self.settings["countdown_enabled"]:
            self.startCountdown()
        
    def setupAnimations(self):
        # 移动动画
        self.move_animation = QPropertyAnimation(self, b"pos")
        self.move_animation.setDuration(2000)
        self.move_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.move_animation.finished.connect(self.animationFinished)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制铁傀儡的形状
        self.drawIronGolem(painter)
        
    def drawIronGolem(self, painter):
        # 头部图片 - 使用ng.png
        pumpkin_size = 50
        pumpkin_x = (self.golem_width - pumpkin_size) // 2
        pumpkin_y = 10
        
        # 尝试加载并绘制ng.png
        try:
            ng_path = resource_path('ng.png')
            pixmap = QPixmap(ng_path)
            if not pixmap.isNull():
                # 缩放图片到指定大小
                scaled_pixmap = pixmap.scaled(pumpkin_size, pumpkin_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(pumpkin_x, pumpkin_y, scaled_pixmap)
            else:
                # 如果图片加载失败，绘制备用的南瓜头
                self.drawFallbackPumpkin(painter, pumpkin_x, pumpkin_y, pumpkin_size)
        except Exception:
            # 如果出现任何错误，绘制备用的南瓜头
            self.drawFallbackPumpkin(painter, pumpkin_x, pumpkin_y, pumpkin_size)
        
        # 根据不同模式绘制铁傀儡
        if self.animation_mode == 1:
            self.drawMode1(painter, pumpkin_y, pumpkin_size)
        elif self.animation_mode == 2:
            self.drawMode2(painter, pumpkin_y, pumpkin_size)
        elif self.animation_mode == 3:
            self.drawMode3(painter, pumpkin_y, pumpkin_size)
        elif self.animation_mode == 4:
            self.drawMode4(painter, pumpkin_y, pumpkin_size)
    
    def drawMode1(self, painter, pumpkin_y, pumpkin_size):
        """模式1：经典铁傀儡形状"""
        first_row_y = pumpkin_y + pumpkin_size + 10
        
        if self.leg_state == 0:  # 状态1: 小大小，大
            # 左臂 - 小
            left_arm_size = 36
            left_arm_x = 20
            self.drawBlock(painter, left_arm_x, first_row_y + 4, left_arm_size, is_large=False)
            
            # 身体 - 大
            body_size = 50
            body_x = (self.golem_width - body_size) // 2
            self.drawBlock(painter, body_x, first_row_y, body_size, is_large=True)
            
            # 右臂 - 小
            right_arm_size = 36
            right_arm_x = self.golem_width - right_arm_size - 20
            self.drawBlock(painter, right_arm_x, first_row_y + 4, right_arm_size, is_large=False)
            
            # 第二行腿部 - 大
            leg_size = 44
            leg_x = (self.golem_width - leg_size) // 2
            leg_y = first_row_y + body_size + 6
            self.drawBlock(painter, leg_x, leg_y, leg_size, is_large=True)
            
        else:  # 状态2: 大小大，小
            # 左臂 - 大
            left_arm_size = 50
            left_arm_x = 10
            self.drawBlock(painter, left_arm_x, first_row_y, left_arm_size, is_large=True)
            
            # 身体 - 小
            body_size = 36
            body_x = (self.golem_width - body_size) // 2
            self.drawBlock(painter, body_x, first_row_y + 4, body_size, is_large=False)
            
            # 右臂 - 大
            right_arm_size = 50
            right_arm_x = self.golem_width - right_arm_size - 10
            self.drawBlock(painter, right_arm_x, first_row_y, right_arm_size, is_large=True)
            
            # 第二行腿部 - 小
            leg_size = 30
            leg_x = (self.golem_width - leg_size) // 2
            leg_y = first_row_y + 50 + 6
            self.drawBlock(painter, leg_x, leg_y + 4, leg_size, is_large=False)
    
    def drawMode2(self, painter, pumpkin_y, pumpkin_size):
        """模式2：四行高铁傀儡"""
        first_row_y = pumpkin_y + pumpkin_size + 10
        
        if self.leg_state == 0:  # 状态1: 大空大，大，大
            # 第二行：左臂 - 大，右臂 - 大
            arm_size = 45
            left_arm_x = 15
            right_arm_x = self.golem_width - arm_size - 15
            self.drawBlock(painter, left_arm_x, first_row_y, arm_size, is_large=True)
            self.drawBlock(painter, right_arm_x, first_row_y, arm_size, is_large=True)
            
            # 第三行：身体 - 大
            body_size = 45
            body_x = (self.golem_width - body_size) // 2
            body_y = first_row_y + arm_size + 5
            self.drawBlock(painter, body_x, body_y, body_size, is_large=True)
            
            # 第四行：腿部 - 大
            leg_size = 45
            leg_x = (self.golem_width - leg_size) // 2
            leg_y = body_y + body_size + 5
            self.drawBlock(painter, leg_x, leg_y, leg_size, is_large=True)
            
        else:  # 状态2: 大南瓜大，大，大，空
            # 第一行：左臂和右臂在南瓜旁边
            arm_size = 40
            left_arm_x = 10
            right_arm_x = self.golem_width - arm_size - 10
            arm_y = pumpkin_y + 5
            self.drawBlock(painter, left_arm_x, arm_y, arm_size, is_large=True)
            self.drawBlock(painter, right_arm_x, arm_y, arm_size, is_large=True)
            
            # 第二行：身体 - 大
            body_size = 45
            body_x = (self.golem_width - body_size) // 2
            body_y = first_row_y + 5
            self.drawBlock(painter, body_x, body_y, body_size, is_large=True)
            
            # 第三行：腿部 - 大
            leg_size = 45
            leg_x = (self.golem_width - leg_size) // 2
            leg_y = body_y + body_size + 5
            self.drawBlock(painter, leg_x, leg_y, leg_size, is_large=True)
    
    def drawMode3(self, painter, pumpkin_y, pumpkin_size):
        """模式3：宽体铁傀儡"""
        first_row_y = pumpkin_y + pumpkin_size + 10
        
        if self.leg_state == 0:  # 状态1: 大大大，大
            # 第二行：左臂、身体、右臂都是大
            block_size = 40
            spacing = 5
            total_width = block_size * 3 + spacing * 2
            start_x = (self.golem_width - total_width) // 2
            
            # 左臂 - 大
            self.drawBlock(painter, start_x, first_row_y, block_size, is_large=True)
            # 身体 - 大
            self.drawBlock(painter, start_x + block_size + spacing, first_row_y, block_size, is_large=True)
            # 右臂 - 大
            self.drawBlock(painter, start_x + (block_size + spacing) * 2, first_row_y, block_size, is_large=True)
            
            # 第三行：腿部 - 大
            leg_size = 40
            leg_x = (self.golem_width - leg_size) // 2
            leg_y = first_row_y + block_size + 8
            self.drawBlock(painter, leg_x, leg_y, leg_size, is_large=True)
            
        else:  # 状态2: 大南瓜空，空大大，大
            # 第一行：南瓜左边有一个大方块
            left_block_size = 40
            left_block_x = 10
            left_block_y = pumpkin_y + 5  # 与南瓜同一行
            self.drawBlock(painter, left_block_x, left_block_y, left_block_size, is_large=True)
            
            # 第二行：左侧空，只有身体和右臂 - 大
            body_size = 40
            right_arm_size = 40
            spacing = 5
            
            # 身体位置（偏右一些，因为左侧是空的）
            body_x = (self.golem_width - body_size - right_arm_size - spacing) // 2 + 25
            self.drawBlock(painter, body_x, first_row_y, body_size, is_large=True)
            
            # 右臂位置
            right_arm_x = body_x + body_size + spacing
            self.drawBlock(painter, right_arm_x, first_row_y, right_arm_size, is_large=True)
            
            # 第三行：腿部 - 大
            leg_size = 40
            leg_x = (self.golem_width - leg_size) // 2
            leg_y = first_row_y + 40 + 8
            self.drawBlock(painter, leg_x, leg_y, leg_size, is_large=True)
    
    def drawMode4(self, painter, pumpkin_y, pumpkin_size):
        """模式4：3×3网格对齐的铁傀儡"""
        # 定义3×3网格的基础参数
        grid_size = 40  # 每个网格格子的大小
        spacing = 5     # 格子之间的间距
        
        # 计算网格的起始位置（居中）
        total_width = grid_size * 3 + spacing * 2
        start_x = (self.golem_width - total_width) // 2
        
        # 三列的X坐标
        col1_x = start_x
        col2_x = start_x + grid_size + spacing
        col3_x = start_x + (grid_size + spacing) * 2
        
        # 两行的Y坐标（南瓜下面）
        row1_y = pumpkin_y + pumpkin_size + 10  # 第二行（手臂）
        row2_y = row1_y + grid_size + spacing   # 第三行（腿部）
        
        if self.leg_state == 0:  # 状态1: 小小大，大空小
            # 第二行：左臂 - 小，身体 - 小，右臂 - 大
            # 左臂 - 小（在第一列居中）
            self.drawBlock(painter, col1_x, row1_y, grid_size, is_large=False)
            
            # 身体 - 小（在第二列居中）
            self.drawBlock(painter, col2_x, row1_y, grid_size, is_large=False)
            
            # 右臂 - 大（填满第三列）
            self.drawBlock(painter, col3_x, row1_y, grid_size, is_large=True)
            
            # 第三行：左腿 - 大，中间空，右腿 - 小
            # 左腿 - 大（填满第一列）
            self.drawBlock(painter, col1_x, row2_y, grid_size, is_large=True)
            
            # 中间空（第二列不绘制）
            
            # 右腿 - 小（在第三列居中）
            self.drawBlock(painter, col3_x, row2_y, grid_size, is_large=False)
            
        else:  # 状态2: 小小小，小空大
            # 第二行：左臂 - 小，身体 - 小，右臂 - 小
            # 左臂 - 小（在第一列居中）
            self.drawBlock(painter, col1_x, row1_y, grid_size, is_large=False)
            
            # 身体 - 小（在第二列居中）
            self.drawBlock(painter, col2_x, row1_y, grid_size, is_large=False)
            
            # 右臂 - 小（在第三列居中）
            self.drawBlock(painter, col3_x, row1_y, grid_size, is_large=False)
            
            # 第三行：左腿 - 小，中间空，右腿 - 大
            # 左腿 - 小（在第一列居中）
            self.drawBlock(painter, col1_x, row2_y, grid_size, is_large=False)
            
            # 中间空（第二列不绘制）
            
            # 右腿 - 大（填满第三列）
            self.drawBlock(painter, col3_x, row2_y, grid_size, is_large=True)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
            # 如果倒计时跳跃中，停止跳跃
            if self.countdown_finished:
                self.stopCountdownJumping()
            else:
                # 点击反馈 - 让铁傀儡"跳跃"，然后切换动画
                self.bounceAndToggle()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.dragging = False
        event.accept()
    
    def bounce(self):
        """点击时的跳跃效果"""
        original_pos = self.pos()
        bounce_pos = QPoint(original_pos.x(), original_pos.y() - 20)
        
        # 向上跳跃
        self.move_animation.setStartValue(original_pos)
        self.move_animation.setEndValue(bounce_pos)
        self.move_animation.setDuration(200)
        self.move_animation.finished.disconnect()
        self.move_animation.finished.connect(lambda: self.bounceDown(original_pos))
        self.move_animation.start()
        
    def bounceAndToggle(self):
        """跳跃并切换动画状态"""
        original_pos = self.pos()
        bounce_pos = QPoint(original_pos.x(), original_pos.y() - 20)
        
        # 向上跳跃
        self.move_animation.setStartValue(original_pos)
        self.move_animation.setEndValue(bounce_pos)
        self.move_animation.setDuration(200)
        self.move_animation.finished.disconnect()
        self.move_animation.finished.connect(lambda: self.bounceDownAndToggle(original_pos))
        self.move_animation.start()
        
    def bounceDownAndToggle(self, original_pos):
        """跳跃后下落并切换动画"""
        self.move_animation.setStartValue(self.pos())
        self.move_animation.setEndValue(original_pos)
        self.move_animation.setDuration(200)
        self.move_animation.finished.disconnect()
        self.move_animation.finished.connect(self.bounceFinishedToggle)
        self.move_animation.start()
        
    def bounceFinishedToggle(self):
        """跳跃结束后切换腿部动画"""
        self.is_moving = False
        self.toggleLegAnimation()
        self.update()
    
    def bounceDown(self, original_pos):
        """跳跃后下落"""
        self.move_animation.setStartValue(self.pos())
        self.move_animation.setEndValue(original_pos)
        self.move_animation.setDuration(200)
        self.move_animation.finished.disconnect()
        self.move_animation.finished.connect(self.animationFinished)
        self.move_animation.start()
    
    def switchLegState(self):
        """切换腿部状态"""
        self.leg_state = 1 - self.leg_state  # 在0和1之间切换
        self.update()  # 重绘界面
        
    def toggleLegAnimation(self):
        """切换腿部动画开关"""
        if self.leg_animation_running:
            # 停止动画
            self.leg_timer.stop()
            self.leg_animation_running = False
        else:
            # 开始动画
            self.leg_timer.start(500)  # 0.5秒切换一次
            self.leg_animation_running = True
        
        self.update()  # 重绘以更新特效
    
    def setupSystemTray(self):
        """设置系统托盘"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        # 设置托盘图标
        try:
            icon_path = resource_path('ng.png')
            tray_icon = QIcon(icon_path)
        except Exception:
            # 如果图标加载失败，使用默认图标
            tray_icon = QIcon()
        
        self.tray_icon = QSystemTrayIcon(tray_icon, self)
        self.tray_icon.setToolTip("铁傀儡桌宠")
        
        # 创建托盘菜单
        self.createTrayMenu()
        
        # 连接双击事件
        self.tray_icon.activated.connect(self.trayIconActivated)
        
        # 显示托盘图标
        self.tray_icon.show()
    
    def createTrayMenu(self):
        """创建托盘右键菜单"""
        tray_menu = QMenu()
        
        # 显示/隐藏桌宠
        show_action = QAction("显示桌宠", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("隐藏桌宠", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        # 动画模式选择
        mode_menu = tray_menu.addMenu("动画模式")
        
        mode1_action = QAction("模式1", self)
        mode1_action.triggered.connect(lambda: self.setAnimationMode(1))
        mode_menu.addAction(mode1_action)
        
        mode2_action = QAction("模式2", self)
        mode2_action.triggered.connect(lambda: self.setAnimationMode(2))
        mode_menu.addAction(mode2_action)
        
        mode3_action = QAction("模式3", self)
        mode3_action.triggered.connect(lambda: self.setAnimationMode(3))
        mode_menu.addAction(mode3_action)
        
        mode4_action = QAction("模式4", self)
        mode4_action.triggered.connect(lambda: self.setAnimationMode(4))
        mode_menu.addAction(mode4_action)
        
        tray_menu.addSeparator()
        
        # 设置
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.openSettings)
        tray_menu.addAction(settings_action)
        
        tray_menu.addSeparator()
        
        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quitApplication)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
    
    def trayIconActivated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
                self.raise_()
    
    def setAnimationMode(self, mode):
        """设置动画模式"""
        self.animation_mode = mode
        self.update()
    
    def quitApplication(self):
        """退出应用程序"""
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        QApplication.quit()
    
    def openSettings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def showAbout(self):
        """显示关于对话框"""
        dialog = AboutDialog(self)
        dialog.exec_()
    
    def animationFinished(self):
        """动画结束"""
        self.is_moving = False
        self.update()  # 重绘以移除移动特效
    
    def contextMenuEvent(self, event):
        """右键菜单"""
        from PyQt5.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        # 动画控制
        if self.leg_animation_running:
            toggle_action = menu.addAction("停止动画")
        else:
            toggle_action = menu.addAction("开始动画")
        toggle_action.triggered.connect(self.toggleLegAnimation)
        
        menu.addSeparator()
        
        # 模式选择
        mode_menu = menu.addMenu("切换模式")
        
        mode1_action = mode_menu.addAction("模式一")
        mode1_action.triggered.connect(lambda: self.changeMode(1))
        if self.animation_mode == 1:
            mode1_action.setCheckable(True)
            mode1_action.setChecked(True)
        
        mode2_action = mode_menu.addAction("模式二")
        mode2_action.triggered.connect(lambda: self.changeMode(2))
        if self.animation_mode == 2:
            mode2_action.setCheckable(True)
            mode2_action.setChecked(True)
        
        mode3_action = mode_menu.addAction("模式三")
        mode3_action.triggered.connect(lambda: self.changeMode(3))
        if self.animation_mode == 3:
            mode3_action.setCheckable(True)
            mode3_action.setChecked(True)
        
        mode4_action = mode_menu.addAction("模式四")
        mode4_action.triggered.connect(lambda: self.changeMode(4))
        if self.animation_mode == 4:
            mode4_action.setCheckable(True)
            mode4_action.setChecked(True)
        
        menu.addSeparator()
        
        # 设置
        settings_action = menu.addAction("设置")
        settings_action.triggered.connect(self.showSettings)
        
        # 关于
        about_action = menu.addAction("关于")
        about_action.triggered.connect(self.showAbout)
        
        menu.addSeparator()
        
        # 隐藏到托盘
        hide_action = menu.addAction("隐藏到托盘")
        hide_action.triggered.connect(self.hide)
        
        # 真正退出
        quit_action = menu.addAction("完全退出")
        quit_action.triggered.connect(self.quitApplication)
        
        menu.exec_(event.globalPos())
        
    def changeMode(self, mode):
        """切换动画模式"""
        self.animation_mode = mode
        self.leg_state = 0  # 重置状态
        self.update()  # 重绘界面
    
    def drawFallbackPumpkin(self, painter, pumpkin_x, pumpkin_y, pumpkin_size):
        """备用南瓜头绘制函数，当ng.png加载失败时使用"""
        painter.setBrush(QColor(255, 165, 0))  # 橙色
        painter.setPen(QColor(139, 69, 19))    # 深棕色边框
        painter.drawRect(pumpkin_x, pumpkin_y, pumpkin_size, pumpkin_size)
        
        # 绘制南瓜的脸 - 回到粗版风格
        painter.setBrush(QColor(139, 69, 19))
        painter.setPen(Qt.NoPen)
        
        # 眼睛 - 方形，更粗
        painter.drawRect(pumpkin_x + 10, pumpkin_y + 14, 8, 8)
        painter.drawRect(pumpkin_x + 32, pumpkin_y + 14, 8, 8)
        
        # 嘴巴 - 简单的方形，更粗
        painter.drawRect(pumpkin_x + 14, pumpkin_y + 30, 22, 8)
    
    def loadBlockTexture(self):
        """加载方块材质"""
        try:
            tk_path = resource_path('tk.png')
            self.block_texture = QPixmap(tk_path)
            if self.block_texture.isNull():
                self.block_texture = None
        except Exception:
            self.block_texture = None
    
    def drawBlock(self, painter, x, y, size, is_large=True):
        """绘制方块（使用材质或备用颜色）"""
        if self.block_texture and not self.block_texture.isNull():
            # 使用tk.png材质
            if is_large:
                # 大方块使用原始大小
                scaled_texture = self.block_texture.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            else:
                # 小方块使用85%大小
                small_size = int(size * 0.85)
                offset = (size - small_size) // 2
                scaled_texture = self.block_texture.scaled(small_size, small_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                x += offset
                y += offset
                size = small_size
            painter.drawPixmap(x, y, scaled_texture)
        else:
            # 备用方案：使用原来的灰色方块
            painter.setBrush(QColor(169, 169, 169))  # 浅灰色
            painter.setPen(QColor(105, 105, 105))    # 深灰色边框
            if not is_large:
                # 小方块调整大小和位置
                small_size = int(size * 0.85)
                offset = (size - small_size) // 2
                x += offset
                y += offset
                size = small_size
            painter.drawRect(x, y, size, size)
    
    def loadSettings(self):
        """加载设置"""
        self.settings_file = "iron_golem_settings.json"
        self.settings = {
            "hourly_chime": False,
            "countdown_enabled": False,
            "countdown_minutes": 5,
            "auto_start": False
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except Exception:
            pass
    
    def saveSettings(self):
        """保存设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def setupTimers(self):
        """设置定时器"""
        # 整点报时定时器
        self.hourly_timer = QTimer()
        self.hourly_timer.timeout.connect(self.checkHourlyChime)
        if self.settings["hourly_chime"]:
            self.hourly_timer.start(1000)  # 每秒检查一次
        
        # 倒计时定时器
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.countdownTick)
        self.countdown_remaining = 0
        self.countdown_finished = False
        
        # 倒计时跳跃定时器
        self.countdown_jump_timer = QTimer()
        self.countdown_jump_timer.timeout.connect(self.countdownJump)
        
        # 记录上次检查的小时
        self.last_hour = datetime.now().hour
    
    def checkHourlyChime(self):
        """检查整点报时"""
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_second = current_time.second
        
        # 整点时跳跃（精确到秒）
        if (current_minute == 0 and current_second == 0 and 
            current_hour != self.last_hour):
            self.bounce()
            self.last_hour = current_hour
    
    def startCountdown(self):
        """开始倒计时"""
        if self.settings["countdown_enabled"]:
            self.countdown_remaining = self.settings["countdown_minutes"] * 60  # 转换为秒
            self.countdown_finished = False
            self.countdown_timer.start(1000)  # 每秒更新
    
    def countdownTick(self):
        """倒计时计数"""
        if self.countdown_remaining > 0:
            self.countdown_remaining -= 1
        else:
            # 倒计时结束
            self.countdown_timer.stop()
            self.countdown_finished = True
            self.countdown_jump_timer.start(500)  # 每0.5秒跳跃一次
    
    def countdownJump(self):
        """倒计时结束后的跳跃"""
        if self.countdown_finished:
            self.bounce()
    
    def stopCountdownJumping(self):
        """停止倒计时跳跃"""
        if self.countdown_finished:
            self.countdown_jump_timer.stop()
            self.countdown_finished = False
            # 重新开始倒计时（如果启用的话）
            if self.settings["countdown_enabled"]:
                self.startCountdown()
    
    def setAutoStart(self, enabled):
        """设置开机自启动"""
        try:
            app_path = os.path.abspath(sys.argv[0])
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            app_name = "IronGolemPet"
            
            if enabled:
                # 添加到启动项
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
                winreg.CloseKey(key)
                return True
            else:
                # 从启动项移除
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.DeleteValue(key, app_name)
                    winreg.CloseKey(key)
                    return True
                except FileNotFoundError:
                    return True  # 如果不存在也算成功
        except Exception:
            return False
    
    def showSettings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 应用新设置
            old_hourly = self.settings["hourly_chime"]
            old_countdown = self.settings["countdown_enabled"]
            
            self.settings = dialog.getSettings()
            self.saveSettings()
            
            # 更新定时器
            if self.settings["hourly_chime"] != old_hourly:
                if self.settings["hourly_chime"]:
                    self.hourly_timer.start(1000)
                else:
                    self.hourly_timer.stop()
            
            if self.settings["countdown_enabled"] != old_countdown:
                if self.settings["countdown_enabled"]:
                    self.startCountdown()
                else:
                    self.countdown_timer.stop()
                    self.countdown_jump_timer.stop()
                    self.countdown_finished = False
            elif self.settings["countdown_enabled"]:
                # 重新开始倒计时（如果时间改变了）
                self.countdown_timer.stop()
                self.startCountdown()
    

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("关于")
        self.setFixedSize(400, 300)
        self.setWindowIcon(QIcon(resource_path('ng.png')))
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("铁傀儡桌宠")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 添加一些间距
        layout.addSpacing(20)
        
        # 简介
        intro_label = QLabel("简介：铁傀儡开凿机，但是桌宠。")
        intro_label.setAlignment(Qt.AlignCenter)
        intro_font = QFont()
        intro_font.setPointSize(12)
        intro_label.setFont(intro_font)
        layout.addWidget(intro_label)
        
        layout.addSpacing(10)
        
        # 作者
        author_label = QLabel("作者：冷域LYOfficial")
        author_label.setAlignment(Qt.AlignCenter)
        author_font = QFont()
        author_font.setPointSize(12)
        author_label.setFont(author_font)
        layout.addWidget(author_label)
        
        layout.addSpacing(10)
        
        # 开源链接
        github_label = QLabel('开源：<a href="https://github.com/LYOfficial/IronGolemPet">https://github.com/LYOfficial/IronGolemPet</a>')
        github_label.setAlignment(Qt.AlignCenter)
        github_label.setOpenExternalLinks(True)  # 允许点击链接打开浏览器
        github_font = QFont()
        github_font.setPointSize(10)
        github_label.setFont(github_font)
        layout.addWidget(github_label)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 确定按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        ok_button.setFixedSize(80, 30)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addSpacing(20)
        
        self.setLayout(layout)
    

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("设置")
        self.setFixedSize(300, 250)
        
        layout = QVBoxLayout()
        
        # 整点报时
        self.hourly_chime_cb = QCheckBox("整点报时")
        self.hourly_chime_cb.setChecked(self.parent_widget.settings["hourly_chime"])
        layout.addWidget(self.hourly_chime_cb)
        
        # 倒计时设置
        countdown_layout = QHBoxLayout()
        self.countdown_cb = QCheckBox("倒计时提醒")
        self.countdown_cb.setChecked(self.parent_widget.settings["countdown_enabled"])
        countdown_layout.addWidget(self.countdown_cb)
        
        self.countdown_spin = QSpinBox()
        self.countdown_spin.setMinimum(1)
        self.countdown_spin.setMaximum(60)
        self.countdown_spin.setValue(self.parent_widget.settings["countdown_minutes"])
        self.countdown_spin.setSuffix(" 分钟")
        countdown_layout.addWidget(self.countdown_spin)
        
        layout.addLayout(countdown_layout)
        
        # 开机自启动
        self.auto_start_cb = QCheckBox("开机自启动")
        self.auto_start_cb.setChecked(self.parent_widget.settings["auto_start"])
        layout.addWidget(self.auto_start_cb)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def accept(self):
        # 处理开机自启动设置
        auto_start_enabled = self.auto_start_cb.isChecked()
        if auto_start_enabled != self.parent_widget.settings["auto_start"]:
            success = self.parent_widget.setAutoStart(auto_start_enabled)
            if not success:
                QMessageBox.warning(self, "警告", "设置开机自启动失败，可能需要管理员权限。")
                return
        
        super().accept()
    
    def getSettings(self):
        return {
            "hourly_chime": self.hourly_chime_cb.isChecked(),
            "countdown_enabled": self.countdown_cb.isChecked(),
            "countdown_minutes": self.countdown_spin.value(),
            "auto_start": self.auto_start_cb.isChecked()
        }


class DesktopPet:
    def __init__(self):
        self.app = QApplication(sys.argv)
        # 设置应用程序图标
        try:
            icon_path = resource_path('ng.png')
            app_icon = QIcon(icon_path)
            if not app_icon.isNull():
                self.app.setWindowIcon(app_icon)
        except Exception:
            pass
        
        # 设置应用程序退出行为
        self.app.setQuitOnLastWindowClosed(False)
        
        self.golem = IronGolem()
        
    def run(self):
        # 显示桌宠
        self.golem.show()
        
        # 显示托盘提示消息
        if hasattr(self.golem, 'tray_icon') and self.golem.tray_icon.isVisible():
            self.golem.tray_icon.showMessage(
                "铁傀儡桌宠",
                "桌宠已启动！双击托盘图标可以显示/隐藏桌宠。",
                QSystemTrayIcon.Information,
                3000
            )
        
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    pet = DesktopPet()
    pet.run()
