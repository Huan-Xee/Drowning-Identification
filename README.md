# Drowning-Identification

A drowning identification system based on yolov5 (基于yolov5溺水识别系统)【本科毕业设计】

使用了**esp32-cam**连接onenet上**传数据流**，通过python访问云平台获取数据流进行识别，尝试将代码部署在**树莓派**上实现边缘计算

==hardware文件夹==里面存储了**硬件代码**

==software文件夹==里面存储来**软件代码**

---

~~使用**http**协议连接上传数据流到云平台~~，但是该方式`延迟高`、容易`丢失数据流`，所以我换成了**mqtt**协议实现数据的上传，明显解决了延迟和丢失数据的问题。
