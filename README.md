# Timer-and-App-Limiter
一个简单的学习用计时器与应用限制软件

## 配置设置
在```data/config.json```中修改数值即可
学习与休息时间的单位为min
提示音频需移入```data```文件夹中,然后复制文件名到```json```的```tone```字段中

## 禁用软件的设置方法
1. 将需要禁用的软件与任务管理器打开
2. 运行```appLimiter.py```脚本
3. 将任务管理器下对应软件的PID键入脚本运行窗口 使用```,```进行分割
4. 将脚本的运行结果复制到```json```的```apps```字段中
5. 运行主程序 测试效果
---
第2、3、4步也可替换成直接在任务管理器的详细信息页面复制应用进程名称到apps字段中

## 打包方法
使用```pyinstaller```生成文件夹式的无终端窗口应用
```
pyinstaller --onedir --uac-admin --windowed --noconfirm --add-data="data/*;data" --add-data="ui/*;ui" --clean main.py
```
配置设置方法同上文所述 文件在```dist/_internal```文件夹内 软件为```dist/main.exe```
