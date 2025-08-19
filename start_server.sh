#!/bin/bash
nohup ./start.sh > app.log 2>&1 &
echo "服务已在后台启动，PID: $!"
echo "查看日志: tail -f app.log"
echo "停止服务: kill $!"