# 每日自动打卡

这个仓库包含一个零依赖的 Python 脚本和 GitHub Actions 工作流，用于每天自动执行学生日常打卡。

## 文件

- `scripts/checkin.py`：登录、检查今日状态、必要时提交“在校”打卡
- `.github/workflows/daily-checkin.yml`：每天北京时间 `09:00` 自动执行，也支持手动触发


