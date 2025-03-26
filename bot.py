import os
import whisper
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, MenuButton, MenuButtonCommands
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, CommandHandler, ContextTypes
import json
from datetime import datetime
import glob
import shutil

# 配置文件路径
CONFIG_FILE = "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "model_size": "tiny",
    "language": "zh",
    "max_video_duration": 1800,
    "output_format": "srt",
    "enable_timestamp": True,
    "font_size": 16,
    "font_color": "white",
    "background_color": "black"
}

# 加载配置
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG

# 保存配置
def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# 检查模型下载状态
def check_model_status():
    model_path = os.path.expanduser("~/.cache/whisper")
    model_files = glob.glob(os.path.join(model_path, "*.pt"))
    if not model_files:
        return False, "模型未下载"
    
    # 检查模型文件大小
    total_size = sum(os.path.getsize(f) for f in model_files)
    if total_size < 100 * 1024 * 1024:  # 小于100MB认为未完全下载
        return False, "模型正在下载中"
    
    return True, "模型已就绪"

# 检查视频处理状态
def check_video_status():
    video_dir = "videos"
    if not os.path.exists(video_dir):
        return "无视频处理"
    
    # 检查临时文件
    temp_files = glob.glob(os.path.join(video_dir, "*.wav"))
    if temp_files:
        return "正在处理音频"
    
    # 检查输出文件
    output_files = glob.glob(os.path.join(video_dir, "*.srt"))
    if output_files:
        return "字幕生成完成"
    
    return "无视频处理"

# 获取系统状态
def get_system_status():
    # 检查磁盘空间
    total, used, free = shutil.disk_usage("/")
    disk_status = f"磁盘空间: 总{total//(2**30)}GB, 已用{used//(2**30)}GB, 剩余{free//(2**30)}GB"
    
    # 检查模型状态
    model_ready, model_status = check_model_status()
    
    # 检查视频状态
    video_status = check_video_status()
    
    return f"系统状态:\n{disk_status}\n模型状态: {model_status}\n视频状态: {video_status}"

# 初始化 Whisper 模型
config = load_config()
model = whisper.load_model(config["model_size"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    keyboard = [
        [InlineKeyboardButton("📝 当前配置", callback_data="show_config")],
        [InlineKeyboardButton("⚙️ 修改配置", callback_data="edit_config")],
        [InlineKeyboardButton("❓ 使用说明", callback_data="help")],
        [InlineKeyboardButton("📊 系统状态", callback_data="system_status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "欢迎使用字幕生成机器人！\n"
        "请选择以下选项：",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    help_text = (
        "🤖 字幕生成机器人使用说明：\n\n"
        "1. 直接发送视频文件即可生成字幕\n"
        "2. 支持的命令：\n"
        "   /start - 显示主菜单\n"
        "   /help - 显示帮助信息\n"
        "   /config - 修改配置\n"
        "   /status - 查看系统状态\n"
        "3. 支持的视频格式：MP4, AVI, MKV\n"
        "4. 最大视频时长：30分钟\n"
        "5. 默认输出格式：SRT"
    )
    await update.message.reply_text(help_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /status 命令"""
    status_text = get_system_status()
    await update.message.reply_text(status_text)

async def show_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示当前配置"""
    config = load_config()
    config_text = (
        "📝 当前配置：\n\n"
        f"模型大小：{config['model_size']}\n"
        f"语言：{config['language']}\n"
        f"最大视频时长：{config['max_video_duration']}秒\n"
        f"输出格式：{config['output_format']}\n"
        f"时间戳：{'启用' if config['enable_timestamp'] else '禁用'}\n"
        f"字体大小：{config['font_size']}\n"
        f"字体颜色：{config['font_color']}\n"
        f"背景颜色：{config['background_color']}"
    )
    keyboard = [[InlineKeyboardButton("⚙️ 修改配置", callback_data="edit_config")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(config_text, reply_markup=reply_markup)

async def setup_menu(application: Application):
    """设置机器人菜单"""
    # 设置命令菜单
    commands = [
        BotCommand("start", "开始使用机器人"),
        BotCommand("help", "显示帮助信息"),
        BotCommand("config", "查看当前配置"),
        BotCommand("status", "查看系统状态"),
        BotCommand("menu", "显示功能菜单")
    ]
    await application.bot.set_my_commands(commands)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /menu 命令"""
    keyboard = [
        [InlineKeyboardButton("🎥 视频处理", callback_data="video_process")],
        [InlineKeyboardButton("⚙️ 系统设置", callback_data="system_settings")],
        [InlineKeyboardButton("📊 状态监控", callback_data="status_monitor")],
        [InlineKeyboardButton("❓ 帮助中心", callback_data="help_center")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📱 功能菜单\n\n"
        "请选择您需要的功能：",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query
    await query.answer()

    if query.data == "show_config":
        config = load_config()
        config_text = (
            "📝 当前配置：\n\n"
            f"模型大小：{config['model_size']}\n"
            f"语言：{config['language']}\n"
            f"最大视频时长：{config['max_video_duration']}秒\n"
            f"输出格式：{config['output_format']}\n"
            f"时间戳：{'启用' if config['enable_timestamp'] else '禁用'}\n"
            f"字体大小：{config['font_size']}\n"
            f"字体颜色：{config['font_color']}\n"
            f"背景颜色：{config['background_color']}"
        )
        keyboard = [[InlineKeyboardButton("⚙️ 修改配置", callback_data="edit_config")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(config_text, reply_markup=reply_markup)

    elif query.data == "edit_config":
        keyboard = [
            [InlineKeyboardButton("模型大小", callback_data="config_model")],
            [InlineKeyboardButton("语言", callback_data="config_language")],
            [InlineKeyboardButton("最大时长", callback_data="config_duration")],
            [InlineKeyboardButton("输出格式", callback_data="config_format")],
            [InlineKeyboardButton("返回", callback_data="show_config")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            "请选择要修改的配置项：",
            reply_markup=reply_markup
        )

    elif query.data == "help":
        help_text = (
            "🤖 字幕生成机器人使用说明：\n\n"
            "1. 直接发送视频文件即可生成字幕\n"
            "2. 支持的命令：\n"
            "   /start - 显示主菜单\n"
            "   /help - 显示帮助信息\n"
            "   /config - 修改配置\n"
            "   /status - 查看系统状态\n"
            "3. 支持的视频格式：MP4, AVI, MKV\n"
            "4. 最大视频时长：30分钟\n"
            "5. 默认输出格式：SRT"
        )
        await query.message.edit_text(help_text)

    elif query.data == "system_status":
        status_text = get_system_status()
        await query.message.edit_text(status_text)

    elif query.data == "video_process":
        keyboard = [
            [InlineKeyboardButton("🎬 发送视频", callback_data="send_video")],
            [InlineKeyboardButton("📝 字幕设置", callback_data="subtitle_settings")],
            [InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            "🎥 视频处理\n\n"
            "选择操作：",
            reply_markup=reply_markup
        )

    elif query.data == "system_settings":
        keyboard = [
            [InlineKeyboardButton("⚙️ 模型设置", callback_data="model_settings")],
            [InlineKeyboardButton("🌐 语言设置", callback_data="language_settings")],
            [InlineKeyboardButton("⏱ 时长设置", callback_data="duration_settings")],
            [InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            "⚙️ 系统设置\n\n"
            "选择要修改的设置：",
            reply_markup=reply_markup
        )

    elif query.data == "status_monitor":
        status_text = get_system_status()
        keyboard = [[InlineKeyboardButton("🔄 刷新状态", callback_data="refresh_status")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(status_text, reply_markup=reply_markup)

    elif query.data == "help_center":
        help_text = (
            "❓ 帮助中心\n\n"
            "1. 视频处理\n"
            "   - 支持格式：MP4, AVI, MKV\n"
            "   - 最大时长：30分钟\n"
            "   - 输出格式：SRT\n\n"
            "2. 系统设置\n"
            "   - 模型大小：tiny/base/small/medium/large\n"
            "   - 语言选择：中文/英文\n"
            "   - 时长限制：可自定义\n\n"
            "3. 状态监控\n"
            "   - 系统资源\n"
            "   - 模型状态\n"
            "   - 处理进度"
        )
        keyboard = [[InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(help_text, reply_markup=reply_markup)

    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("🎥 视频处理", callback_data="video_process")],
            [InlineKeyboardButton("⚙️ 系统设置", callback_data="system_settings")],
            [InlineKeyboardButton("📊 状态监控", callback_data="status_monitor")],
            [InlineKeyboardButton("❓ 帮助中心", callback_data="help_center")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            "📱 功能菜单\n\n"
            "请选择您需要的功能：",
            reply_markup=reply_markup
        )

    elif query.data == "refresh_status":
        status_text = get_system_status()
        keyboard = [[InlineKeyboardButton("🔄 刷新状态", callback_data="refresh_status")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(status_text, reply_markup=reply_markup)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理视频文件"""
    try:
        # 获取视频信息
        video = update.message.video
        if video.duration > config["max_video_duration"]:
            await update.message.reply_text(
                f"❌ 视频时长超过限制（{config['max_video_duration']}秒）"
            )
            return

        # 发送处理中消息
        processing_msg = await update.message.reply_text("⏳ 正在处理视频，请稍候...")

        # 下载视频
        video_file = await video.get_file()
        video_path = f"videos/input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        await video_file.download_to_drive(video_path)

        # 提取音频
        audio_path = video_path.replace(".mp4", ".wav")
        os.system(f"ffmpeg -i {video_path} -vn -ar 16000 -ac 1 {audio_path}")

        # 生成字幕
        result = model.transcribe(audio_path, language=config["language"])
        
        # 生成字幕文件
        output_path = video_path.replace(".mp4", f".{config['output_format']}")
        with open(output_path, "w", encoding="utf-8") as f:
            for seg in result['segments']:
                if config["enable_timestamp"]:
                    f.write(f"{seg['id']}\n{seg['start']} --> {seg['end']}\n{seg['text']}\n\n")
                else:
                    f.write(f"{seg['text']}\n")

        # 发送字幕文件
        await update.message.reply_document(
            document=open(output_path, "rb"),
            filename=f"subtitle.{config['output_format']}"
        )

        # 清理临时文件
        os.remove(video_path)
        os.remove(audio_path)
        os.remove(output_path)

        await processing_msg.edit_text("✅ 字幕生成完成！")

    except Exception as e:
        await update.message.reply_text(f"❌ 处理失败：{str(e)}")

def main():
    """主函数"""
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    # 添加处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("config", show_config))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))

    # 设置菜单
    app.job_queue.run_once(setup_menu, 0)

    # 启动机器人
    app.run_polling()

if __name__ == "__main__":
    main()