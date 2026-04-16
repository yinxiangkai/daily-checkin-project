# 每日自动打卡

这个仓库包含一个零依赖的 Python 脚本和 GitHub Actions 工作流，用于每天自动执行学生日常打卡。

## 文件

- `scripts/checkin.py`：探测登录方式、检查今日状态、必要时提交“在校”打卡
- `.github/workflows/daily-checkin.yml`：每天北京时间 `09:00` 自动执行，也支持手动触发

## 默认配置

当前脚本已经内置了默认值，不配置 GitHub Secrets 也能运行：

```python
DEFAULT_BASE_URL = "http://121.40.111.236:3033/api"
DEFAULT_TIMEZONE = "Asia/Shanghai"
DEFAULT_TIMEOUT = 30
DEFAULT_STUDENT_NO = "202337057"
DEFAULT_NAME = "殷祥凯"
DEFAULT_PASSWORD = "殷祥凯"
```

## 登录方式

脚本会先调用 `/auth/check-role` 自动判断账号类型：

- 学生账号：使用 `学号 + 姓名`
- 非学生账号：使用 `学号/工号 + 密码`

## 可选环境变量

如果你之后想覆盖默认值，可以设置：

- `CHECKIN_BASE_URL`
- `CHECKIN_STUDENT_NO`
- `CHECKIN_NAME`
- `CHECKIN_PASSWORD`
- `CHECKIN_TIMEZONE`
