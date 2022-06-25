"""
功能：建立节拍器-pygame+tkinter对象
时间：2022年6月22日14:51:40
作者：陈子含
"""


from pygame import mixer, time
import tkinter as tk
import tkinter.font as tkFont
from threading import Timer, Thread
from time import sleep


WIDTH = 600
HEIGHT = 400
cx = WIDTH // 2
cy = HEIGHT // 2
side = 10





class Metro:
    def __init__(self):
        mixer.init()
        self.win = tk.Tk()
        self.win.geometry(f'{WIDTH}x{HEIGHT}')
        self.win.resizable(False, False)
        self.win.config(bg='#F8F8F8')
        self.win.title('节拍器')
        self.win.iconbitmap('images/icon.ico')
        self.win.protocol('WM_DELETE_WINDOW', self.close)

        self.is_start = False
        self.min_bpm = 20
        self.max_bpm = 480
        self.beats_count = 4
        self.rects = []
        self.current_beat = 0
        self.clock = time.Clock()
        "主界面控件"
        self.bpm = tk.IntVar()
        self.bpm.set(100)
        self.scale = tk.Scale(self.win, variable=self.bpm, from_=self.min_bpm, to=self.max_bpm,
                              length=int(WIDTH*0.618), orient='horizontal', showvalue=False, command=self.bpm_change)
        self.scale.bind('<MouseWheel>', self.bpm_change)
        self.start = tk.Button(self.win, text='   开始   ',
                               activebackground='#72AC51',
                               activeforeground='#FFFFFF',
                               font=('微软雅黑', 10),
                               command=self.switch)
        self.up = tk.Button(self.win, font=('Consolas', 10), text='+', command=self.bpm_up)
        self.down = tk.Button(self.win, font=('Consolas', 10), text='-', command=self.bpm_down)
        self.b_up = tk.Button(self.win, font=('Consolas', 10), text='+', command=self.beats_up)
        self.b_down = tk.Button(self.win, font=('Consolas', 10), text='-', command=self.beats_down)
        self.canvas = tk.Canvas(self.win, bg='#F8F8F8', width=560, height=60, bd=0, relief='flat')
        self.canvas.bind('<Button-1>', self.border_change)
        self.canvas.config(highlightthickness=0)
        self.text_bpm = tk.Label(self.win, text=f'{self.bpm.get()}BPM',
                                 font=('Consolas', 20), relief='flat', bg='#F8F8F8', bd=0, width=10, height=1)
        self.text_beats = tk.Label(self.win, text=f'{self.beats_count}',
                                 font=('Consolas', 15), relief='flat', bg='#F8F8F8', bd=0)
        self.text_beats.bind('<MouseWheel>', self.beats_change)
        "主界面布局"
        self.place(self.b_down, 0.45, 0.1)
        self.place(self.b_up, 0.55, 0.1)
        self.place(self.text_beats, 0.5, 0.1)
        self.place(self.canvas, 0.5, 0.25)
        self.place(self.scale, 0.5, 0.4)
        self.place(self.down, 0.1, 0.4)
        self.place(self.up, 0.9, 0.4)
        self.place(self.text_bpm, 0.5, 0.6)
        self.place(self.start, 0.5, 0.8)
        "其他"
        self.beats_reset()

    def main(self):
        self.win.mainloop()

    def switch(self):
        """
        改变开始-结束状态
        """
        self.is_start = 1 - self.is_start
        self.start['text'] = ('   结束   ' if self.is_start else '   开始   ')
        if self.is_start:
            self.current_beat = 0
            self.win.after(0, self.metro_start)

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
        obj.place(x=WIDTH*ix-w/2, y=HEIGHT*iy-h/2)

    def timer(self):
        """
        控制时间稳定的threading.Timer
        """
        t = Timer(60 / self.bpm.get(), self.metro_start)
        t.start()

    def metro_start(self):
        """
        每一拍执行一次
        """
        if self.is_start:
            self.next_beat()
            self.win.after(ms=0, func=self.timer)

    def bpm_change(self, event):
        """
        通过鼠标滚轮或滑块改变bpm
        :param event: 滑块或滚轮事件
        """
        if type(event) == str:
            self.bpm.set(event)
        elif event.delta > 0:
            self.bpm.set(self.bpm.get() + 1)
        elif event.delta < 0:
            self.bpm.set(self.bpm.get() - 1)
        self.bpm_reset()

    def bpm_up(self):
        if self.bpm.get() < self.max_bpm:
            self.bpm.set(self.bpm.get() + 1)
            self.bpm_reset()

    def bpm_down(self):
        if self.bpm.get() > self.min_bpm:
            self.bpm.set(self.bpm.get() - 1)
            self.bpm_reset()

    def bpm_reset(self):
        """
        更改bpm后的重置操作
        """
        self.text_bpm['text'] = f'{self.bpm.get()}BPM'
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
            rect = self.canvas.create_rectangle(*r, fill='orange', width=0)
            self.rects.append(rect)
        self.current_beat = 0
        self.text_beats['text'] = f'{self.beats_count}'

    def next_beat(self):
        """
        播放下一拍音频，变化颜色，并进行下一拍的其他操作
        """
        id = self.current_beat % self.beats_count
        tag = self.rects[id]
        border = self.canvas.coords(tag)
        delta = border[3] - border[1]
        drum = None if delta == 0 else (1 if delta == 40 else (2 if delta == 30 else 3))
        music = [None, 'max.mp3', 'middle.mp3', 'min.mp3']
        t1 = Thread(target=self.color_change, args=(tag,), daemon=True)
        t2 = Thread(target=self.music_play, args=(music, drum), daemon=True)
        t1.start()
        t2.start()
        # self.clock.tick(0)
        # print(f'current_bpm:{self.clock.get_fps()*60}')
        self.current_beat += 1

    def color_change(self, tag):
        self.canvas.itemconfig(tag, fill='red')
        sleep(30 / self.bpm.get())
        self.canvas.itemconfig(tag, fill='orange')

    def music_play(self, music, drum):
        if drum:
            mixer.music.set_volume(1)
            mixer.music.load('sound/' + music[drum])
            mixer.music.play()

    def get_rects(self):
        """
        计算方块在canvas中的坐标位置
        :return: 方块在canvas中的坐标位置：（x1, y1, x2, y2）
        """
        h = 40
        n = self.beats_count
        w1 = (-0.3061 * n ** 2 + 19.5918 * n + 246.5306) / (1.618 * n - 0.618)
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
                delta = 0
            elif delta == 30:
                delta = 40
            elif delta == 15:
                delta = 30
            else:
                delta = 15
            border[1] = border[3] - delta
            self.canvas.coords(tag, *border)

    def close(self):
        """
        停止程序
        """
        if self.is_start:
            self.switch()
        self.win.quit()


m = Metro()
m.main()
