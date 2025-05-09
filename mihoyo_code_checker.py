import requests
import time
from datetime import datetime
import winsound
import os
from colorama import init, Fore, Style
import json
import re
import tkinter as tk
from tkinter import messagebox
from win10toast import ToastNotifier
import html
import threading

# 初始化colorama和通知器
init()
toaster = ToastNotifier()

# 用于存储已发现的兑换码
DISCOVERED_CODES = set()

def clean_html(text):
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 解码HTML实体
    text = html.unescape(text)
    return text.strip()

def show_notification_thread(title, message):
    # 在新线程中显示通知
    def show():
        # 显示系统通知
        toaster.show_toast(
            title,
            message,
            duration=5,
            threaded=True
        )
        # 显示消息框
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showinfo(title, message)
        root.destroy()
    
    # 创建并启动新线程
    thread = threading.Thread(target=show)
    thread.daemon = True  # 设置为守护线程
    thread.start()

def play_alert():
    # 只播放系统提示音
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

def get_code_status():
    url = "https://api-takumi-static.mihoyo.com/event/miyolive/refreshCode"
    params = {
        "version": "7e76f9",
        "time": "1746790480"
    }
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "origin": "https://webstatic.mihoyo.com",
        "priority": "u=1, i",
        "referer": "https://webstatic.mihoyo.com/",
        "sec-ch-ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        "x-rpc-act_id": "ea202505061542344390"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        return data.get("data", {}).get("code_list", [])
    except Exception as e:
        print(f"{Fore.RED}请求出错: {e}{Style.RESET_ALL}")
        return []

def print_status(code_list, previous_codes=None):
    if previous_codes is None:
        previous_codes = [{"title": "", "code": ""} for _ in range(3)]
    
    # 清屏
    os.system('cls' if os.name == 'nt' else 'clear')
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.CYAN}当前时间: {current_time}{Style.RESET_ALL}")
    
    has_new_code = False
    for i, (code_info, prev_info) in enumerate(zip(code_list, previous_codes), 1):
        title = clean_html(code_info.get("title", ""))
        code = code_info.get("code", "")
        prev_title = clean_html(prev_info.get("title", ""))
        prev_code = prev_info.get("code", "")
        
        if title and code:
            # 检查是否是新的兑换码
            if code not in DISCOVERED_CODES:
                has_new_code = True
                DISCOVERED_CODES.add(code)
                print(f"\n{Fore.YELLOW}{'!'*50}")
                print(f"发现新兑换码 {i}:")
                print(f"标题: {title}")
                print(f"兑换码: {code}")
                print(f"{'!'*50}{Style.RESET_ALL}\n")
                
                # 在新线程中显示通知
                show_notification_thread(
                    "发现新兑换码！",
                    f"标题: {title}\n兑换码: {code}"
                )
            print(f"{Fore.GREEN}兑换码 {i}: {title} - {code}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}兑换码 {i}: 未更新{Style.RESET_ALL}")
    
    if has_new_code:
        play_alert()
        # 保存已发现的兑换码到文件
        with open('discovered_codes.json', 'w', encoding='utf-8') as f:
            json.dump(list(DISCOVERED_CODES), f, ensure_ascii=False, indent=2)
    
    # 打印状态行（始终在底部）
    status = " | ".join([f"码{i}: {'已更新' if code_list[i-1].get('title') and code_list[i-1].get('code') else '未更新'}" for i in range(1, 4)])
    print(f"\n{Fore.YELLOW}当前状态: {status}{Style.RESET_ALL}")
    
    return code_list

def load_discovered_codes():
    try:
        if os.path.exists('discovered_codes.json'):
            with open('discovered_codes.json', 'r', encoding='utf-8') as f:
                return set(json.load(f))
    except Exception as e:
        print(f"{Fore.RED}加载历史兑换码失败: {e}{Style.RESET_ALL}")
    return set()

def main():
    global DISCOVERED_CODES
    DISCOVERED_CODES = load_discovered_codes()
    
    print(f"{Fore.GREEN}开始监控米哈游兑换码状态...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}当发现新兑换码时，将会发出声音提醒！{Style.RESET_ALL}")
    print(f"{Fore.CYAN}已记录的兑换码数量: {len(DISCOVERED_CODES)}{Style.RESET_ALL}")
    
    previous_codes = None
    try:
        while True:
            code_list = get_code_status()
            previous_codes = print_status(code_list, previous_codes)
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}程序已停止{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}发生错误: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 