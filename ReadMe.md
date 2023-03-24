# 基于物体识别的机械臂工业分拣

### 安装
安装VREP(现更名为CoppeliaSim)

在https://www.coppeliarobotics.com/downloads 下载最新的edu版本

如果是windows系统,请将`programming\remoteApiBindings\lib\lib\Windows\64Bit`文件夹下的`remoteApi.dll`,以及`programming\remoteApiBindings\python\python`下的`vrepConst.py`和`vrep.py`或`sim.py`复制到project的`/vrep`文件夹中

### 运行
1. 修改路径

- 修改`collect_data/main.py`中的路径

- 修改`demo/demo.py`中的路径

- 修改`vrep/shell.py`中的路径

2. 运行`shell.py`

3. 运行`demo/demo.py`或`collect_data/main.py`
