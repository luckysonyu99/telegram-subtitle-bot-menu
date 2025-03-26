# Telegram 字幕机器人

这是一个 Telegram 机器人，可以：
- 接收视频文件
- 使用 Whisper 模型生成字幕
- 将字幕烧录到视频中
- 支持多种语言

## 功能特点

- 支持多种视频格式
- 实时字幕生成
- 多语言支持
- Docker 容器化部署
- 交互式菜单界面

## 安装说明

1. 克隆仓库：
```bash
git clone https://github.com/luckysonyu99/telegram-subtitle-bot-menu.git
cd telegram-subtitle-bot-menu
```

2. 配置环境变量：
- 复制 `.env.example` 为 `.env`
- 在 `.env` 文件中设置你的 Telegram Bot Token

3. 下载 Whisper 模型：
```bash
mkdir -p whisper_cache
# 下载 tiny 模型（约 72MB）
wget https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt -O whisper_cache/tiny.pt
```

4. 使用 Docker 运行：
```bash
docker-compose up -d
```

## 使用方法

1. 在 Telegram 中搜索你的机器人
2. 发送 `/start` 命令开始使用
3. 按照菜单提示操作：
   - 发送视频文件
   - 选择字幕语言
   - 等待处理完成

## 注意事项

- 首次运行时会自动下载 Whisper 模型
- 视频处理可能需要一些时间，请耐心等待
- 建议使用较小的视频文件进行测试

## 许可证

MIT License 