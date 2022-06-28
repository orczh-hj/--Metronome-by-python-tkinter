# --Metronome-by-python-tkinter
在github上没找到合适的python节拍器，于是自已熬夜写了一个。
使用python-tkinter写的节拍器GUI，bpm20-800，节拍数1-32，可以调节强音、次强、弱音、无音四种节拍，也可以根据需要自行修改。

# 运行效果如下：
metronome_4.py是主文件，直接运行程序即可
![tmp6CA0](https://user-images.githubusercontent.com/88028971/175807789-e01276a0-196f-4d78-8d66-553e2cd0a552.png)

# 使用方法：
使用鼠标滚轮、‘+’控件、‘-’控件可以改变节拍数；

使用鼠标拖动滑块、鼠标滚轮、‘+’控件、‘-’控件可以改变bpm；

点击方块可以改变节拍声音；

点击‘开始’程序开始播放节拍；

点击空格切换：开始-暂停；

点击键盘上的esc键退出程序；

Ctrl+Shift+K，调出变速节拍对话框，可以设置变速节拍；

建议：点击结束后再关闭程序

# 更新日志
metronome_0 最初版本

metronome_1 新增节拍时间、节拍数显示，增加反馈颜色变化，优化界面颜色

metronome_2 新增点击空格切换 开始-结束；少数bug修复

metronome_3 取消外边框，新增通过鼠标拖动

metronome_4 新增变速节拍，代码优化
