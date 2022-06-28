"""
功能：建立节拍器-tkinter对象，变速+和弦训练
时间：2022年6月26日21:35:15
作者：陈子含
"""
from pygame import mixer
import tkinter as tk
from tkinter import messagebox
from threading import Timer, Thread
from time import sleep
from datetime import datetime

WIDTH,  HEIGHT= 600, 400
MIN_BPM, MAX_BPM = 20, 800


def music_play(music, drum):
    if drum:
        mixer.music.set_volume(1)
        mixer.music.load('sound/' + music[drum])
        mixer.music.play()



class Metro:
    def __init__(self):
        """初始化"""
        self.WIDTH, self.HEIGHT = 600, 400
        "主窗口设置"
        self.win = tk.Tk()
        self.win.geometry(f'{WIDTH}x{HEIGHT}')
        self.win.resizable(False, False)
        self.win.config(bg='#F8F8F8')
        self.win.title('节拍器')
        self.win.protocol('WM_DELETE_WINDOW', self.close)
        self.win.overrideredirect(1)  # 去除窗口边框
        self.win.wm_attributes("-alpha", 0.9)  # 透明度(0.0~1.0)
        self.win.wm_attributes("-toolwindow", True)  # 置为工具窗口(没有最大最小按钮)
        self.win.wm_attributes("-topmost", True)  # 永远处于顶层
        self.win.bind('<space>', self.switch)
        self.win.bind('<Escape>', self.close)
        self.win.bind('<Double-Button-1>', self.close)
        self.win.bind("<ButtonPress-1>", self.StartMove)
        self.win.bind("<ButtonRelease-1>", self.StopMove)
        self.win.bind("<B1-Motion>", self.OnMotion)
        self.win.bind('<Control-Shift-K>', self.top_win)
        "其他"
        self.x, self.y = None, None
        mixer.init()
        self.is_start = False
        self.is_moving = False
        self.min_bpm, self.max_bpm = MIN_BPM, MAX_BPM
        self.beats_count = 4
        self.rects = []
        self.current_beat = 0
        self.start_time = None
        self.speed = [0, 0]
        self.variable_speed = None
        "主界面控件"
        self.bpm = tk.IntVar()
        self.bpm.set(100)
        self.scale = tk.Scale(self.win, variable=self.bpm, from_=self.min_bpm, to=self.max_bpm,
                              length=int(WIDTH*0.7), orient='horizontal', showvalue=False, command=self.bpm_change,
                              troughcolor='#DDDDDD', activebackground='#72AC51', borderwidth=0, relief='flat')
        self.scale.bind('<MouseWheel>', self.bpm_change)
        self.start = tk.Button(self.win, text='   开始   ', font=('微软雅黑', 14, 'bold'), command=self.switch)
        self.up = tk.Button(self.win, font=('Consolas', 10), text='+', command=self.bpm_up, padx=4, pady=0)
        self.down = tk.Button(self.win, font=('Consolas', 10), text='-', command=self.bpm_down, padx=4, pady=0)
        self.b_up = tk.Button(self.win, font=('Consolas', 10), text='+', command=self.beats_up, padx=4, pady=0)
        self.b_down = tk.Button(self.win, font=('Consolas', 10), text='-', command=self.beats_down, padx=4, pady=0)
        self.canvas = tk.Canvas(self.win, bg='#F8F8F8', width=560, height=60, bd=0, relief='flat')
        self.canvas.bind('<Button-1>', self.border_change)
        self.canvas.config(highlightthickness=0)
        self.text_bpm = tk.Label(self.win, text=f'{self.bpm.get()} BPM',
                                 font=('Consolas', 20), relief='flat', bg='#F8F8F8', bd=0, width=15, height=1)
        self.text_beats = tk.Label(self.win, text=f'{self.beats_count}',
                                 font=('Consolas', 15), relief='flat', bg='#F8F8F8', bd=0, width=2)
        self.text_beats.bind('<MouseWheel>', self.beats_change)
        self.text_time = tk.Label(self.win, text='', relief='flat', bg='#F8F8F8', bd=0,
                                  font=('Consolas', 15), width=15)
        self.buttons = [self.start, self.up, self.down, self.b_down, self.b_up]
        [b.bind('<Enter>', self.feedback) for b in self.buttons]
        [b.bind('<Leave>', self.feedback) for b in self.buttons]
        "主界面布局"
        self.place(self.b_down, 0.45, 0.1)
        self.place(self.b_up, 0.55, 0.1)
        self.place(self.text_beats, 0.5, 0.1)
        self.place(self.canvas, 0.5, 0.25)
        self.place(self.scale, 0.5, 0.4)
        self.place(self.down, 0.1, 0.4)
        self.place(self.up, 0.9, 0.4)
        self.place(self.text_bpm, 0.5, 0.57)
        self.place(self.start, 0.5, 0.74)
        self.place(self.text_time, 0.5, 0.9)
        "其他"
        self.beats_reset()

    def main(self):
        self.win.mainloop()

    def top_win(self, event):
        if self.is_start:
            self.switch()
        out = VariableSpeed(self.win)
        self.win.wait_window(out)
        out = out.text
        if out:
            self.variable_speed = out
            self.bpm.set(out[0])
            self.bpm_reset()
            self.switch()
            self.var_speed()

    def var_speed(self):
        if self.is_start:
            t = Timer(self.variable_speed[1], self.var_speed)
            t.start()
            self.bpm_up(self.variable_speed[2])

    def switch(self, event=None):
        """
        改变开始-结束状态
        """
        self.is_start = 1 - self.is_start
        self.start['text'] = ('   结束   ' if self.is_start else '   开始   ')
        if self.is_start:
            self.current_beat = 0
            self.win.after(0, self.metro_start)
            self.start_time = datetime.now()
        else:
            self.text_time['text'] = ''

    def StartMove(self, event):
        self.speed = [0, 0]
        self.x = event.x
        self.y = event.y

    def StopMove(self, event=None):
        if self.speed[0] or self.speed[1]:
            self.is_out()
            self.win.geometry("+%s+%s" % (self.win.winfo_x() + self.speed[0], self.win.winfo_y() + self.speed[1]))
            self.win.update()
            self.speed *= 1
            self.win.after(10, self.StopMove)
            if self.speed[0] > 3:
                self.speed[0] -= 1
            if self.speed[1] > 3:
                self.speed[1] -= 1

    def is_out(self):
        x1, y1 = self.win.winfo_x(), self.win.winfo_y()
        x2, y2 = x1 + WIDTH, y1 + HEIGHT
        if (x1 <= 0) and (self.speed[0] < 0):
            self.speed[0] = abs(self.speed[0])
        elif (x2 >= self.win.winfo_screenwidth()) and (self.speed[0] > 0):
            self.speed[0] = -abs(self.speed[0])
        if (y1 <= 0) and (self.speed[1] < 0):
            self.speed[1] = abs(self.speed[1])
        elif (y2 >= self.win.winfo_screenheight()) and (self.speed[1] > 0):
            self.speed[1] = -abs(self.speed[1])

    def OnMotion(self, event):
        if event.widget == self.win:
            deltax = event.x - self.x
            deltay = event.y - self.y
            self.win.geometry("+%s+%s" % (self.win.winfo_x() + deltax, self.win.winfo_y() + deltay))
            self.speed = [deltax, deltay]
            self.win.update()

    def feedback(self, event):
        if event.type == '7':
            if event.widget['text'] == '   结束   ':
                event.widget['bg'] = '#DB4437'
            else:
                event.widget['bg'] = '#72AC51'
            event.widget['fg'] = '#FFFFFF'
        else:
            event.widget['bg'] = '#F8F8F8'
            event.widget['fg'] = '#000000'

    def metro_start(self):
        """
        每一拍执行一次
        """
        if self.is_start:
            t1 = Timer(60 / self.bpm.get(), self.metro_start)
            t1.start()
            self.next_beat()

    def place(self, obj, ix, iy):
        """
        安放控件
        :param obj: 控件对象
        :param ix: 相对x位置：0-1，0最左侧，1最右侧
        :param iy: 相对y位置：0-1，0最上侧，1最下侧
        :return:
        """
        w = obj.winfo_reqwidth()
        h = obj.winfo_reqheight()
        obj.place(x=self.WIDTH * ix - w / 2, y=self.HEIGHT * iy - h / 2)

    def bpm_change(self, event):
        """
        通过鼠标滚轮或滑块改变bpm
        :param event: 滑块或滚轮事件
        """
        if isinstance(event, str):
            self.bpm.set(event)
            self.bpm_reset()
        elif event.delta > 0:
            self.bpm_up()
        elif event.delta < 0:
            self.bpm_down()

    def bpm_up(self, num=1):
        if self.bpm.get() < self.max_bpm:
            self.bpm.set(self.bpm.get() + num)
            self.bpm_reset()

    def bpm_down(self, num=1):
        if self.bpm.get() > self.min_bpm:
            self.bpm.set(self.bpm.get() - num)
            self.bpm_reset()

    def bpm_reset(self):
        """
        更改bpm后的重置操作
        """
        self.text_bpm['text'] = f'{self.bpm.get()} BPM'
        self.scale.focus_displayof()

    def beats_up(self):
        """
        通过点击'+'减小节拍数
        """
        if self.beats_count < 32:
            self.beats_count += 1
            self.beats_reset()

    def beats_down(self):
        """
        通过点击'-'减小节拍数
        """
        if self.beats_count > 1:
            self.beats_count -= 1
            self.beats_reset()

    def beats_change(self, event):
        """通过鼠标滚轮改变节拍数"""
        if event.delta > 0:
            self.beats_up()
        else:
            self.beats_down()

    def beats_reset(self):
        """
        更改节拍数的重置操作
        """
        rects = self.get_rects()
        [self.canvas.delete(r) for r in self.rects]
        self.rects = []
        for r in rects:
            rect = self.canvas.create_rectangle(*r, fill='#CCCCCC', width=0)
            self.rects.append(rect)
        self.text_beats['text'] = f'{self.beats_count}'

    def next_beat(self):
        """
        播放下一拍音频，变化颜色，并进行下一拍的其他操作
        """
        id_ = self.current_beat % self.beats_count
        tag = self.rects[id_]
        border = self.canvas.coords(tag)
        delta = border[3] - border[1]
        drum = None if delta == 0 else (1 if delta == 40 else (2 if delta == 30 else 3))
        music = [None, 'max.mp3', 'middle.mp3', 'min.mp3']
        t1 = Thread(target=self.color_change, args=(tag,), daemon=True)
        t2 = Thread(target=music_play, args=(music, drum), daemon=True)
        t3 = Thread(target=self.output_info, daemon=True)
        t1.start()
        t2.start()
        t3.start()
        self.current_beat += 1

    def color_change(self, tag):
        self.canvas.itemconfig(tag, fill='#72AC51')
        sleep(30 / self.bpm.get())
        self.canvas.itemconfig(tag, fill='#CCCCCC')

    def get_rects(self):
        """
        计算方块在canvas中的坐标位置
        :return: 所有方块在canvas中的坐标位置列表：[（x1, y1, x2, y2）]
        """
        h = 40
        n = self.beats_count
        w1 = (-0.3061 * n ** 2 + 19.5918 * n + 246.5306) / (1.618 * n - 0.618)
        if n == 1:
            w1 = 120
        w2 = w1 * 0.618
        w = n * w1 + (n - 1) * w2
        centerx = eval(self.canvas['width'])/2
        ws = [(-w/2, -w/2+w1)]
        for i in range(n - 1):
            temp = (ws[-1][0] + w1 + w2, ws[-1][1] + w1 + w2)
            ws.append(temp)
        rects = [(r[0] + centerx, 10, r[1] + centerx, 50) for r in ws]
        return rects

    def border_change(self, event):
        """
        点击方块，改变方块形状，同时改变节拍声音
        :param event: 鼠标在canvas控件中的位置
        """
        tag = self.canvas.find_closest(event.x, event.y)[0]
        border = self.canvas.coords(tag)
        delta = border[3] - border[1]
        if ((border[0] < event.x < border[2]) and (border[1] < event.y < border[3])) or delta == 0:
            if delta == 40:
                delta = 30
            elif delta == 30:
                delta = 15
            elif delta == 15:
                delta = 0
            else:
                delta = 40
            border[1] = border[3] - delta
            self.canvas.coords(tag, *border)

    def output_info(self):
        """
        打印时间和节拍数信息
        """
        t = datetime.now()
        s = str(t - self.start_time).split(':')
        s[-3] = '{:0>2}'.format(int(s[-3]))
        s[-2] = '{:0>2}'.format(int(s[-2]))
        s[-1] = '{:0>2}'.format(int(eval(s[-1])))
        s = s[-3:]
        s = ':'.join(s)
        self.text_time['text'] = f'{s}  {self.current_beat + 1}'

    def close(self, event=None):
        """
        停止程序
        """
        if event:
            if event.type == '4' and event.widget != self.win:
                return
        if self.is_start:
            self.switch()
        self.win.quit()


class VariableSpeed(tk.Toplevel):
    def __init__(self, win):
        super().__init__()
        self.win = win
        self.geometry('320x197')
        self.resizable(False, False)
        self.title('变速控制')
        self.wm_attributes('-topmost', True)
        self.text = None
        "变量"
        self.WIDTH, self.HEIGHT = 320, 197
        self.min_bpm, self.max_bpm = MIN_BPM, MAX_BPM
        "控件"
        self.t1 = tk.StringVar(master=self)
        self.t2 = tk.StringVar(master=self)
        self.t3 = tk.StringVar(master=self)
        self.l1 = tk.Label(self, text='初始速度：', width=9, font=('微软雅黑', 14))
        self.l2 = tk.Label(self, text='每', width=2, font=('微软雅黑', 14))
        self.l3 = tk.Label(self, text='秒      变化', width=8, font=('微软雅黑', 14))
        self.l4 = tk.Label(self, text='bpm', width=3, font=('Consolas', 14))
        self.e1 = tk.Entry(self, textvariable=self.t1, width=27)
        self.e2 = tk.Entry(self, textvariable=self.t2, width=8)
        self.e3 = tk.Entry(self, textvariable=self.t3, width=8)
        self.b1 = tk.Button(self, text='开始', font=('微软雅黑', 14), command=self.ok)
        self.b2 = tk.Button(self, text='取消', font=('微软雅黑', 14), command=self.no)
        "布局"
        self.place(self.l1, 0.18, 0.1)      # 初始速度：
        self.place(self.e1, 0.65, 0.1)
        self.place(self.l2, 0.06, 0.45)     # 每
        self.place(self.e2, 0.21, 0.45)
        self.place(self.l3, 0.47, 0.45)     # 秒变化
        self.place(self.e3, 0.75, 0.45)
        self.place(self.l4, 0.93, 0.45)     # bpm
        self.place(self.b1, 0.2, 0.8)       # 开始
        self.place(self.b2, 0.8, 0.8)       # 取消

    def ok(self):
        text = [self.t1.get(), self.t2.get(), self.t3.get()]

        try:
            text = [eval(i) for i in text]
            if text[0] > self.max_bpm or text[0] < self.min_bpm or text[1] <= 0:
                raise ValueError
        except Exception as e:
            messagebox.showerror('错误', '输入有误，请检查！')
            self.focus()
            self.t1.set('')
            self.t2.set('')
            self.t3.set('')
            self.text = None
            return
        self.text = text
        self.destroy()

    def no(self):
        self.text = None
        self.destroy()

    def place(self, obj, ix, iy):
        """
        安放控件
        :param obj: 控件对象
        :param ix: 相对x位置：0-1，0最左侧，1最右侧
        :param iy: 相对y位置：0-1，0最上侧，1最下侧
        :return:
        """
        w = obj.winfo_reqwidth()
        h = obj.winfo_reqheight()
        obj.place(x=self.WIDTH * ix - w / 2, y=self.HEIGHT * iy - h / 2)














m = Metro()
m.main()
