# 每日自动打卡

这个仓库包含一个零依赖的 Python 脚本和 GitHub Actions 工作流，用于每天自动执行学生日常打卡。

## 文件

- `scripts/checkin.py`：登录、检查今日状态、必要时提交“在校”打卡
- `.github/workflows/daily-checkin.yml`：每天北京时间 `09:00` 自动执行，也支持手动触发

## GitHub 配置

在仓库的 `Settings -> Secrets and variables -> Actions` 中添加：

### Secrets

- `CHECKIN_STUDENT_NO`
- `CHECKIN_PASSWORD`

### Variables

- `CHECKIN_BASE_URL`
  默认值：`http://121.40.111.236:3033/api`
- `CHECKIN_TIMEZONE`
  默认值：`Asia/Shanghai`

如果不设置 Variables，工作流会自动使用默认值。

## 本地运行

```bash
export CHECKIN_BASE_URL="http://121.40.111.236:3033/api"
export CHECKIN_STUDENT_NO="你的学号或工号"
export CHECKIN_PASSWORD="你的密码"
export CHECKIN_TIMEZONE="Asia/Shanghai"
python3 scripts/checkin.py
```

## 工作流行为

- 先登录并获取 token
- 查询 `today-status`
- 如果今天已经打卡，输出 `今日已存在记录`
- 如果今天未打卡，提交 `{"status":"在校"}`
- 出现登录失败、网络错误或接口返回异常时，任务会失败并在 Actions 中标红

## 上线前建议

1. 先在 GitHub Actions 页面手动运行一次 `Daily Check-in`
2. 确认日志出现 `登录成功`
3. 确认首次执行是 `已打卡` 或 `今日已存在记录`
4. 再手动运行一次，确认不会重复提交
