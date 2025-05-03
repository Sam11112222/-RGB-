#!/bin/bash
# 获取当前用户的主目录
user_home=$(eval echo ~$USER)
# 进入用户主目录
cd "$user_home"
# 运行python脚本
python3 rgb_app.py
