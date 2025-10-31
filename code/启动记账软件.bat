@echo off
REM 个人记账软件启动脚本
REM 双击此文件运行程序

echo 正在启动个人记账软件...
python main.py
if %errorlevel% neq 0 (
    echo 程序运行出错！
    echo 请确保已安装Python 3.6或更高版本
    pause
)