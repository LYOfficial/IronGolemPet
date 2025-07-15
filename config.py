# 外观设置
GOLEM_WIDTH = 80
GOLEM_HEIGHT = 120

# 颜色配置
COLORS = {
    'pumpkin': (255, 165, 0),        # 南瓜橙色
    'pumpkin_border': (139, 69, 19), # 南瓜边框棕色
    'iron': (169, 169, 169),         # 铁块灰色
    'iron_border': (105, 105, 105),  # 铁块边框深灰
    'face': (139, 69, 19),           # 脸部特征棕色
    'glow': (255, 255, 0, 100),      # 移动时的光效
}

# 动画设置
ANIMATION = {
    'move_interval': 5000,        # 自动移动间隔(毫秒)
    'move_duration_min': 1500,    # 移动动画最短时间
    'move_duration_max': 3000,    # 移动动画最长时间
    'bounce_duration': 200,       # 跳跃动画时间
    'bounce_height': 20,          # 跳跃高度
}

# 尺寸配置
SIZES = {
    'pumpkin': 25,
    'body': 30,
    'arm': 20,
    'leg': 20,
}
