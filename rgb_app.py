import tkinter as tk
from tkinter import messagebox, ttk
import smbus
import threading
import time
import sys

# ======================
# I2C 设备配置
# ======================
I2C_ADDR = 0x0d  # I2C设备地址
FAN_REG = 0x08    # 风扇控制寄存器
RGB_REG = {
    "select": 0x00,   # 选择灯寄存器
    "r": 0x01,        # R值寄存器
    "g": 0x02,        # G值寄存器
    "b": 0x03,        # B值寄存器
    "effect": 0x04,   # 特效模式寄存器
    "speed": 0x05,    # 特效速度寄存器
    "color": 0x06,    # 特效颜色寄存器
    "off": 0x07       # 关闭灯寄存器
}

# 预设颜色（RGB值）
PRESET_COLORS = {
    "红色": (255, 0, 0),
    "绿色": (0, 255, 0),
    "蓝色": (0, 0, 255),
    "黄色": (255, 255, 0),
    "紫色": (255, 0, 255),
    "青色": (0, 255, 255),
    "白色": (255, 255, 255),
    "关闭": (0, 0, 0)
}

# 特效模式说明
EFFECT_MODES = {
    0: "流水灯",
    1: "呼吸灯",
    2: "跑马灯",
    3: "彩虹灯",
    4: "炫彩灯"
}

# 风扇速度说明（0x00~0x09对应0%~100%）
FAN_SPEED_MAP = {
    0: "关闭 (0%)",
    1: "全速 (100%)",
    2: "20%",
    3: "30%",
    4: "40%",
    5: "50%",
    6: "60%",
    7: "70%",
    8: "80%",
    9: "90%"
}


# ======================
# 硬件控制类
# ======================
class HardwareController:
    def __init__(self):
        self.bus = smbus.SMBus(1)  # I2C总线1（树莓派默认）
        self.fan_speed = 0          # 当前风扇速度（0-9）
        self.rgb_select = 0xFF      # 操作所有灯（默认）
    
    def write_i2c(self, reg, value):
        """向I2C寄存器写入数据"""
        try:
            self.bus.write_byte_data(I2C_ADDR, reg, value)
            return True
        except Exception as e:
            messagebox.showerror("硬件错误", f"I2C通信失败: {str(e)}")
            return False
    
    # ----------------------
    # RGB灯控制
    # ----------------------
    def set_rgb_color(self, r, g, b):
        """设置RGB颜色（所有灯）"""
        self.write_i2c(RGB_REG["select"], 0xFF)  # 操作所有灯
        self.write_i2c(RGB_REG["r"], r)
        self.write_i2c(RGB_REG["g"], g)
        self.write_i2c(RGB_REG["b"], b)
    
    def set_rgb_effect(self, effect, speed, color):
        """设置RGB特效"""
        self.write_i2c(RGB_REG["effect"], effect)
        self.write_i2c(RGB_REG["speed"], speed)
        self.write_i2c(RGB_REG["color"], color)
    
    def turn_off_rgb(self):
        """关闭所有RGB灯"""
        self.write_i2c(RGB_REG["off"], 0x00)
    
    # ----------------------
    # 风扇控制
    # ----------------------
    def set_fan_speed(self, speed):
        """设置风扇速度（0-9）"""
        if 0 <= speed <= 9:
            self.fan_speed = speed
            return self.write_i2c(FAN_REG, speed)
        return False
    
    # ----------------------
    # CPU温度获取
    # ----------------------
    def get_cpu_temperature(self):
        """获取CPU温度（℃）"""
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = float(f.read()) / 1000.0
                return round(temp, 1)
        except Exception:
            return -1.0


# ======================
# 界面类
# ======================
class ControlInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("智能设备控制中心")
        self.hardware = HardwareController()
        
        # 自动调节线程标志
        self.auto_thread_running = False
        
        # 创建界面组件
        self.create_widgets()
        self.update_status_loop()  # 启动状态更新循环
    
    # ----------------------
    # 界面组件创建
    # ----------------------
    def create_widgets(self):
        # 框架分组
        self.frame_rgb = ttk.LabelFrame(self.root, text="RGB灯控制")
        self.frame_fan = ttk.LabelFrame(self.root, text="风扇控制")
        self.frame_auto = ttk.LabelFrame(self.root, text="自动调节（CPU温度）")
        self.frame_status = ttk.LabelFrame(self.root, text="实时状态")
        
        # ----------------------
        # RGB灯控制区
        # ----------------------
        # 预设颜色按钮
        ttk.Label(self.frame_rgb, text="预设颜色:").grid(row=0, column=0, padx=5, pady=5)
        self.preset_btn = ttk.Combobox(self.frame_rgb, values=list(PRESET_COLORS.keys()))
        self.preset_btn.set("选择预设")
        self.preset_btn.bind("<<ComboboxSelected>>", self.apply_preset_color)
        self.preset_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # 自定义颜色输入
        ttk.Label(self.frame_rgb, text="R (0-255):").grid(row=1, column=0, padx=5, pady=2)
        self.entry_r = ttk.Entry(self.frame_rgb, width=8, validate="key",
                                 validatecommand=(self.root.register(self.validate_number), "%P"))
        self.entry_r.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(self.frame_rgb, text="G (0-255):").grid(row=2, column=0, padx=5, pady=2)
        self.entry_g = ttk.Entry(self.frame_rgb, width=8, validate="key",
                                 validatecommand=(self.root.register(self.validate_number), "%P"))
        self.entry_g.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(self.frame_rgb, text="B (0-255):").grid(row=3, column=0, padx=5, pady=2)
        self.entry_b = ttk.Entry(self.frame_rgb, width=8, validate="key",
                                 validatecommand=(self.root.register(self.validate_number), "%P"))
        self.entry_b.grid(row=3, column=1, padx=5, pady=2)
        
        self.btn_set_color = ttk.Button(self.frame_rgb, text="应用颜色", command=self.apply_custom_color)
        self.btn_set_color.grid(row=4, column=0, columnspan=2, pady=5)
        
        # 特效控制
        ttk.Label(self.frame_rgb, text="特效模式:").grid(row=5, column=0, padx=5, pady=2)
        self.effect_combobox = ttk.Combobox(self.frame_rgb, values=list(EFFECT_MODES.values()))
        self.effect_combobox.set("选择模式")
        self.effect_combobox.grid(row=5, column=1, padx=5, pady=2)
        
        ttk.Label(self.frame_rgb, text="速度 (1-3):").grid(row=6, column=0, padx=5, pady=2)
        self.entry_speed = ttk.Entry(self.frame_rgb, width=8, validate="key",
                                     validatecommand=(self.root.register(self.validate_speed), "%P"))
        self.entry_speed.grid(row=6, column=1, padx=5, pady=2)
        
        ttk.Label(self.frame_rgb, text="颜色 (0-6):").grid(row=7, column=0, padx=5, pady=2)
        self.color_combobox = ttk.Combobox(self.frame_rgb, values=["红", "绿", "蓝", "黄", "紫", "青", "白"])
        self.color_combobox.set("选择颜色")
        self.color_combobox.grid(row=7, column=1, padx=5, pady=2)
        
        self.btn_set_effect = ttk.Button(self.frame_rgb, text="启动特效", command=self.apply_effect)
        self.btn_set_effect.grid(row=8, column=0, columnspan=2, pady=5)
        
        self.btn_off_rgb = ttk.Button(self.frame_rgb, text="关闭所有灯", command=self.hardware.turn_off_rgb,
                                      style="Warning.TButton")
        self.btn_off_rgb.grid(row=9, column=0, columnspan=2, pady=5)
        
        # ----------------------
        # 风扇控制区
        # ----------------------
        ttk.Label(self.frame_fan, text="手动调节:").grid(row=0, column=0, padx=5, pady=5)
        self.fan_scale = ttk.Scale(self.frame_fan, from_=0, to=9, orient=tk.HORIZONTAL, length=200)
        self.fan_scale.set(0)  # 默认关闭
        self.fan_scale.bind("<ButtonRelease-1>", self.update_fan_scale)
        self.fan_scale.grid(row=0, column=1, padx=5, pady=5)
        
        self.lbl_fan_status = ttk.Label(self.frame_fan, text="风扇状态: 关闭")
        self.lbl_fan_status.grid(row=1, column=0, columnspan=2, pady=5)
        
        # ----------------------
        # 自动调节区
        # ----------------------
        ttk.Label(self.frame_auto, text="检测间隔 (秒):").grid(row=0, column=0, padx=5, pady=2)
        self.entry_interval = ttk.Entry(self.frame_auto, width=8, validate="key",
                                        validatecommand=(self.root.register(self.validate_number), "%P"))
        self.entry_interval.grid(row=0, column=1, padx=5, pady=2)
        self.entry_interval.insert(0, "5")  # 默认5秒
        
        ttk.Label(self.frame_auto, text="低温阈值 (℃):").grid(row=1, column=0, padx=5, pady=2)
        self.entry_low_temp = ttk.Entry(self.frame_auto, width=8, validate="key",
                                        validatecommand=(self.root.register(self.validate_number), "%P"))
        self.entry_low_temp.grid(row=1, column=1, padx=5, pady=2)
        self.entry_low_temp.insert(0, "35")  # 默认35℃
        
        ttk.Label(self.frame_auto, text="高温阈值 (℃):").grid(row=2, column=0, padx=5, pady=2)
        self.entry_high_temp = ttk.Entry(self.frame_auto, width=8, validate="key",
                                         validatecommand=(self.root.register(self.validate_number), "%P"))
        self.entry_high_temp.grid(row=2, column=1, padx=5, pady=2)
        self.entry_high_temp.insert(0, "50")  # 默认50℃
        
        self.btn_auto_start = ttk.Button(self.frame_auto, text="启动自动调节", command=self.start_auto_adjust,
                                         style="Success.TButton")
        self.btn_auto_stop = ttk.Button(self.frame_auto, text="停止自动调节", command=self.stop_auto_adjust,
                                        style="Warning.TButton")
        self.btn_auto_start.grid(row=3, column=0, pady=5)
        self.btn_auto_stop.grid(row=3, column=1, pady=5)
        
        # ----------------------
        # 状态显示区
        # ----------------------
        self.lbl_temp = ttk.Label(self.frame_status, text="CPU温度: --℃")
        self.lbl_temp.pack(pady=5)
        
        self.lbl_last_op = ttk.Label(self.frame_status, text="最后操作: 无")
        self.lbl_last_op.pack(pady=2)
        
        # ----------------------
        # 布局管理
        # ----------------------
        self.frame_rgb.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_fan.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.frame_auto.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_status.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # 配置行高列宽自适应
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # 样式设置
        style = ttk.Style()
        style.configure("Warning.TButton", foreground="red")
        style.configure("Success.TButton", foreground="green")
    
    # ----------------------
    # 输入验证函数
    # ----------------------
    def validate_number(self, value):
        """验证输入是否为0-255的整数"""
        return value.isdigit() or value == ""
    
    def validate_speed(self, value):
        """验证输入是否为1-3的整数"""
        return value.isdigit() and (0 < int(value) <= 3) or value == ""
    
    # ----------------------
    # 功能函数
    # ----------------------
    def apply_preset_color(self, event):
        """应用预设颜色"""
        color_name = self.preset_btn.get()
        r, g, b = PRESET_COLORS[color_name]
        self.entry_r.delete(0, tk.END)
        self.entry_g.delete(0, tk.END)
        self.entry_b.delete(0, tk.END)
        self.entry_r.insert(0, r)
        self.entry_g.insert(0, g)
        self.entry_b.insert(0, b)
        self.apply_custom_color()
    
    def apply_custom_color(self):
        """应用自定义RGB颜色"""
        try:
            r = int(self.entry_r.get()) if self.entry_r.get() else 0
            g = int(self.entry_g.get()) if self.entry_g.get() else 0
            b = int(self.entry_b.get()) if self.entry_b.get() else 0
            self.hardware.set_rgb_color(r, g, b)
            self.update_last_operation(f"设置颜色: R={r}, G={g}, B={b}")
        except Exception:
            messagebox.showerror("输入错误", "请输入有效的0-255数值！")
    
    def apply_effect(self):
        """应用RGB特效"""
        try:
            effect = list(EFFECT_MODES.keys())[list(EFFECT_MODES.values()).index(self.effect_combobox.get())]
            speed = int(self.entry_speed.get()) if self.entry_speed.get() else 2  # 默认中速
            color_idx = self.color_combobox.current()  # 0-6对应预设颜色顺序
            self.hardware.set_rgb_effect(effect, speed, color_idx)
            self.update_last_operation(f"启动特效: {EFFECT_MODES[effect]}，速度{speed}，颜色{color_idx}")
        except Exception:
            messagebox.showerror("参数错误", "请选择有效的特效参数！")
    
    def update_fan_scale(self, event):
        """通过滑动条调节风扇速度"""
        speed = int(self.fan_scale.get())
        self.hardware.set_fan_speed(speed)
        self.lbl_fan_status.config(text=f"风扇状态: {FAN_SPEED_MAP[speed]}")
        self.update_last_operation(f"设置风扇速度: {FAN_SPEED_MAP[speed]}")
    
    def start_auto_adjust(self):
        """启动自动调节（CPU温度控制）"""
        if not self.auto_thread_running:
            self.auto_thread_running = True
            interval = int(self.entry_interval.get())
            low_temp = int(self.entry_low_temp.get())
            high_temp = int(self.entry_high_temp.get())
            threading.Thread(target=self.auto_adjust_loop, args=(interval, low_temp, high_temp), daemon=True).start()
            self.update_last_operation("自动调节已启动")
    
    def stop_auto_adjust(self):
        """停止自动调节"""
        self.auto_thread_running = False
        self.update_last_operation("自动调节已停止")
    
    def auto_adjust_loop(self, interval, low_temp, high_temp):
        """自动调节核心逻辑（在后台线程运行）"""
        while self.auto_thread_running:
            temp = self.hardware.get_cpu_temperature()
            if temp == -1.0:
                time.sleep(interval)
                continue
            
            # 更新温度显示
            self.root.after(0, lambda: self.lbl_temp.config(text=f"CPU温度: {temp}℃"))
            
            # 温度分段控制
            if temp < low_temp:
                # 低温：风扇关闭，灯蓝色
                self.hardware.set_fan_speed(0)
                self.hardware.set_rgb_color(0, 0, 255)
                status = f"低温({temp}℃): 风扇关闭，灯蓝色"
            elif temp < high_temp:
                # 中温：风扇50%，灯黄色
                self.hardware.set_fan_speed(5)
                self.hardware.set_rgb_color(255, 255, 0)
                status = f"中温({temp}℃): 风扇50%，灯黄色"
            else:
                # 高温：风扇全速，灯红色
                self.hardware.set_fan_speed(9)
                self.hardware.set_rgb_color(255, 0, 0)
                status = f"高温({temp}℃): 风扇全速，灯红色"
            
            self.root.after(0, lambda: self.update_last_operation(status))
            time.sleep(interval)
    
    def update_status_loop(self):
        """定时更新界面状态（非阻塞）"""
        # 更新风扇状态
        self.lbl_fan_status.config(text=f"风扇状态: {FAN_SPEED_MAP[self.hardware.fan_speed]}")
        # 递归调用实现循环
        self.root.after(1000, self.update_status_loop)
    
    def update_last_operation(self, message):
        """更新最后操作提示"""
        self.lbl_last_op.config(text=f"最后操作: {message}")
        self.root.update()


# ======================
# 主程序入口
# ======================
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x500")  # 窗口大小
    app = ControlInterface(root)
    
    # 程序退出时清理
    def on_exit():
        app.hardware.turn_off_rgb()  # 关闭所有灯
        app.hardware.set_fan_speed(0)  # 关闭风扇
        root.destroy()
        sys.exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_exit)
    root.mainloop()
