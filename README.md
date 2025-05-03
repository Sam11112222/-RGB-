RGB灯与风扇智能控制中心（树莓派版）

通过图形界面实时控制RGB灯颜色和风扇转速，支持根据CPU温度自动调节，适用于树莓派的轻量级- 硬件管理系统。

 项目功能
1. RGB灯控制
• 自定义RGB颜色（0-255数值输入或预设颜色快速选择）
• 多种灯光特效（流水灯、呼吸灯、跑马灯等）
• 一键关闭所有灯光
2. 风扇控制
• 手动调节转速（0-9档位，对应0%-100%）
• 滑动条直观操作，实时显示当前转速状态
3. 智能自动调节
• 根据CPU温度自动切换风扇转速和灯光颜色
• 可自定义低温/高温阈值及检测间隔

 硬件要求

组件	推荐型号	连接方式	说明
树莓派	Raspberry Pi 3B+/4B	-	支持Python 3.7+的- 任意型号
RGB灯模块	通用I2C RGB灯模块	I2C (SDA/GPIO3,- SCL/GPIO5)	I2C地址默认0x0d（- 需与代码一致）

风扇	5V直流风扇+PWM驱- 动模块	I2C（通过寄存器控- 制）	转速控制寄存器地址- 0x08（代码中定义）


 软件依赖 & 强制安装命令

一、系统依赖（通过 apt 强制安装）

sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y --force-yes python3-tk python3-smbus

◦ python3-tk：Tkinter 图形界面库（系统级依赖）
◦ python3-smbus：I2C 通信库（用于硬件控制）

二、Python 库（无额外依赖，均为内置或系统包）


本项目无需通过

安装额外 Python 库，核心功能依赖树莓派系统自带的 tkinter 和 smbus。


 安装步骤
将三个文件打包下载下来后
把ru_rgb_app.sh文件移动到/home目录下
把rgb_app.py移动到/home/你设置的用户名 目录下
最后将rgb_app.desktop移动到桌面上即可

• 确保RGB灯和风扇通过I2C正确连接树莓派
• 启用I2C功能：sudo raspi-confg → Interface Options → 启用 I2C

 使用方法1:
1. 启动程序
在终端下cd到用户文件夹下（/home/你设置的用户名）

python3 rgb_app.py

3. 图形界面操作

RGB灯控制
◦ 预设颜色：通过下拉菜单快速选择红/绿/蓝等常用颜色
◦ 自定义颜色：输入R/G/B数值（0-255），点击“应用颜色”实时生效
◦ 灯光特效：选择特效模式、速度和颜色，点击“启动特效”体验动态效果
◦ 关闭灯光：点击“关闭所有灯”快速熄灭所有RGB灯

风扇控制
◦ 手动调节：拖动滑动条（0-9）设置风扇转速，实时显示当前转速百分比（如“风扇状态: 50%”）
◦ 自动调节：
1. 设置温度检测间隔（默认5秒）、低温阈值（默认35℃)、高温阈值（默认50℃)
2. 点击“启动自动调节”，系统会根据CPU温度自动调整：
◦ 低温（< 低温阈值）：风扇关闭，灯光蓝色
◦ 中温（低温~高温阈值）：风扇50%，灯光黄色
◦ 高温(≥ 高温阈值）：风扇全速，灯光红色

方法2:
双击桌面上的rgb app快捷方式，选择左边第一个按钮，即可打开

 故障排除
1. I2C设备未识别
◦ 检查硬件连接是否松动，重启树莓派
◦ 使用 sudo i2cdetect -y 1 确认RGB灯地址（0x0d） 存

2. 依赖安装错误
◦ 若 apt-get 提示依赖冲突，使用强制安装（风险提示：可能破坏系统）：

sudo apt-get install -y --allow-downgrades --allow-remove-essential --allow--
change-held-packages python3-tk python3-smbus

3. 自动调节失效
◦ 检查CPU温度路径是否正确（树莓派默认路径为/sys/class/thermal/thermal_zone0/temp）
◦ 确保输入的温度阈值合理（低温阈值 < 高温阈值）

 贡献与反馈
1. 提交问题：在GitHub仓库创建新Issue，描述问题细节和复现步骤
2. 提交PR：点击仓库页面的 Fork 按钮，修改后提交Pull Request
3. 联系方式：通过GitHub私信与作者沟通,邮箱为18157376382@163.com或sam12166507@gmail.com

 许可证
本项目采用 MIT许可证，允许自由使用、修改和分发，但需保留原作者声明。

 强制安装说明（重要）
◦ --force-yes 或类似参数可能会覆盖系统文件，仅在明确知道风险时使用
◦ 推荐通过 raspi-confg 确保I2C和系统环境正确配置
◦ 若遇系统异常，可通过 sudo apt-get install --reinstall python3-tk python3-smbus 修复
以上内容聚焦核心功能，明确了强制安装系统依赖的命令，并保留了 GitHub 用户名和项目链接，适- 合发布到你的仓库中。
