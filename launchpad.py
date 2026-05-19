#!/usr/bin/env python3
"""
启动器：提供一个简单的 GUI，点击 "启动" 后会在后台启动 `App.py`，并在服务可用时自动打开浏览器指向 http://{local_ip}:5000

功能：
- 显示本地 IP 和访问地址
- 启动/停止后台服务器进程
- 等待服务就绪并自动在默认浏览器打开页面

注意：在 Windows 上会为后台进程打开新控制台窗口以便查看日志。
"""

import os
import sys
import socket
import time
import threading
import subprocess
import webbrowser
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
try:
	import tkinter as tk
	from tkinter import messagebox
except Exception:
	# 如果没有 tkinter，向用户说明
	raise


# 获取本地IP地址（与 App.py 中的方法一致）
def get_local_ip():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8', 80))
		ip = s.getsockname()[0]
		s.close()
		return ip
	except Exception:
		return '127.0.0.1'


class LauncherGUI:
	def __init__(self, root):
		self.root = root
		self.root.title('WirelessDrop 启动器')
		self.proc = None
		self.app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'App.py')

		# UI 元素
		self.ip = get_local_ip()
		self.url = f'http://{self.ip}:5000'

		frm = tk.Frame(root, padx=12, pady=12)
		frm.pack()

		tk.Label(frm, text='WirelessDrop 启动器', font=('Segoe UI', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,8))
		tk.Label(frm, text=f'本地 IP: {self.ip}').grid(row=1, column=0, sticky='w')
		tk.Label(frm, text=f'访问地址:').grid(row=2, column=0, sticky='w')
		self.url_label = tk.Label(frm, text=self.url, fg='blue', cursor='hand2')
		self.url_label.grid(row=2, column=1, sticky='w')
		self.url_label.bind('<Button-1>', lambda e: webbrowser.open(self.url))

		self.status_var = tk.StringVar(value='状态: 未启动')
		tk.Label(frm, textvariable=self.status_var).grid(row=3, column=0, columnspan=2, pady=(8,0))

		btn_frame = tk.Frame(frm)
		btn_frame.grid(row=4, column=0, columnspan=2, pady=(12,0))

		self.start_btn = tk.Button(btn_frame, text='启动', width=12, command=self.on_start)
		self.start_btn.pack(side='left', padx=6)
		self.stop_btn = tk.Button(btn_frame, text='停止', width=12, state='disabled', command=self.on_stop)
		self.stop_btn.pack(side='left', padx=6)
		self.open_btn = tk.Button(btn_frame, text='打开浏览器', width=12, command=lambda: webbrowser.open(self.url))
		self.open_btn.pack(side='left', padx=6)

		# 关闭时确保子进程被清理
		self.root.protocol('WM_DELETE_WINDOW', self.on_close)

	def on_start(self):
		if self.proc and self.proc.poll() is None:
			messagebox.showinfo('提示', '服务已在运行')
			return

		if not os.path.exists(self.app_path):
			messagebox.showerror('错误', f'找不到 {self.app_path}')
			return

		# 启动后台进程
		cmd = [sys.executable, self.app_path]
		logfile = os.path.join(os.path.dirname(self.app_path), 'launchpad.log')
		f = open(logfile, 'a', encoding='utf-8')

		creationflags = 0
		if os.name == 'nt':
			# 在 Windows 上打开新控制台以便查看输出（可选）
			try:
				creationflags = subprocess.CREATE_NEW_CONSOLE
			except Exception:
				creationflags = 0

		try:
			self.proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=os.path.dirname(self.app_path), creationflags=creationflags)
		except TypeError:
			# 某些 Python 解释器（或平台）可能不接受 creationflags 参数
			self.proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=os.path.dirname(self.app_path))

		self.start_btn.config(state='disabled')
		self.stop_btn.config(state='normal')
		self.status_var.set('状态: 启动中... 正在等待服务就绪')

		# 在后台线程中等待服务可访问
		threading.Thread(target=self._wait_and_open, daemon=True).start()

	def _wait_and_open(self, timeout=20.0):
		start = time.time()
		while time.time() - start < timeout:
			try:
				resp = urlopen(self.url, timeout=1)
				# 如果请求成功，打开浏览器并更新状态
				webbrowser.open(self.url)
				self.status_var.set('状态: 运行中 (已打开浏览器)')
				return
			except (URLError, HTTPError, OSError):
				time.sleep(0.5)

		# 超时：仍然尝试打开浏览器并提示用户
		webbrowser.open(self.url)
		self.status_var.set('状态: 运行中 (等待超时，已尝试打开浏览器)')

	def on_stop(self):
		if not self.proc:
			return
		if self.proc.poll() is None:
			try:
				# 先尝试优雅结束
				self.proc.terminate()
				# 等待短时间
				try:
					self.proc.wait(timeout=3)
				except Exception:
					self.proc.kill()
			except Exception as e:
				print('停止进程时出错:', e)

		self.start_btn.config(state='normal')
		self.stop_btn.config(state='disabled')
		self.status_var.set('状态: 已停止')

	def on_close(self):
		if self.proc and self.proc.poll() is None:
			if messagebox.askyesno('确认', '服务仍在运行，关闭启动器将停止服务。确定要关闭吗？'):
				try:
					self.proc.terminate()
				except Exception:
					pass
			else:
				return
		self.root.destroy()


def main():
	root = tk.Tk()
	LauncherGUI(root)
	root.mainloop()


if __name__ == '__main__':
	main()


