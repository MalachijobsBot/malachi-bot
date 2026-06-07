import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")
CHANNEL_DISPLAY_NAME = "Malachi Freelancer"

JOB_TITLE, JOB_TYPE, LOCATION, SALARY, DEADLINE, DESCRIPTION, COMPANY_NAME, JOBS_COUNT, APPLY_LINK, CONFIRM = range(10)

JOB_TYPES = ["On-site - Permanent (Full-time)", "On-site - Contract", "On-site - Part-time", "Remote - Full-time", "Remote - Freelance", "Hybrid - Full-time"]
SALARY_TYPES = ["Monthly", "Negotiable", "Fixed", "Hourly", "Commission"]

def build_job_message(data):
    lines = []
    lines.append(f"📋 *Job Title:* {data.get('title', '—')}")
    lines.append("")
    lines.append(f"*Job Type:* {data.get('job_type', '—')}")
    lines.append("")
    lines.append(f"*Work Location:* {data.get('location', '—')}")
    lines.append("")
    lines.append(f"*Salary/Compensation:* {data.get('salary', '—')}")
    lines.append("")
    lines.append(f"*Deadline:* {data.get('deadline', '—')}")
    lines.append("")
    lines.append("*Description:*")
    lines.append(data.get('description', '—'))
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")
    company = data.get('company', '')
    if company:
        lines.append(f"*{company}*")
        lines.append("✅ _Verified Company_")
        jobs_count = data.get('jobs_count', '')
        if jobs_count:
            lines.append(f"{jobs_count} Jobs Posted")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append(f"From: @malachifreelancer | #MalachiFreelancer")
    return "\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👋 Welcome to *{CHANNEL_DISPLAY_NAME} Bot*!\n\nUse /postjob to post a job.\nUse /help for all commands.", parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("*📌 Commands:*\n\n/postjob — Post a new job\n/cancel — Cancel\n/help — This message", parse_mode="Markdown")

async def postjob_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("✍️ *Step 1/9 — Job Title*\n\nEnter the job title:\n\nType /cancel to stop.", parse_mode="Markdown")
    return JOB_TITLE

async def get_job_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['title'] = update.message.text.strip()
    keyboard = [[InlineKeyboardButton(jt, callback_data=f"jt_{i}")] for i, jt in enumerate(JOB_TYPES)]
    await update.message.reply_text("📌 *Step 2/9 — Job Type*\n\nSelect the job type:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return JOB_TYPE

async def get_job_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_")[1])
    context.user_data['job_type'] = JOB_TYPES[idx]
    await query.edit_message_text(f"✅ Job Type: *{JOB_TYPES[idx]}*\n\n📍 *Step 3/9 — Work Location*\n\nEnter the work location:", parse_mode="Markdown")
    return LOCATION

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['location'] = update.message.text.strip()
    keyboard = [[InlineKeyboardButton(s, callback_data=f"sal_{i}")] for i, s in enumerate(SALARY_TYPES)]
    await update.message.reply_text("💰 *Step 4/9 — Salary*\n\nSelect salary type:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return SALARY

async def get_salary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_")[1])
    context.user_data['salary'] = SALARY_TYPES[idx]
    await query.edit_message_text(f"✅ Salary: *{SALARY_TYPES[idx]}*\n\n📅 *Step 5/9 — Deadline*\n\nEnter the deadline:\n_Example: June 30, 2026_", parse_mode="Markdown")
    return DEADLINE

async def get_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['deadline'] = update.message.text.strip()
    await update.message.reply_text("📝 *Step 6/9 — Description*\n\nEnter the job description:", parse_mode="Markdown")
    return DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text.strip()
    await update.message.reply_text("🏢 *Step 7/9 — Company Name*\n\nEnter the company name:", parse_mode="Markdown")
    return COMPANY_NAME

async def get_company_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['company'] = update.message.text.strip()
    await update.message.reply_text("🔢 *Step 8/9 — Jobs Count*\n\nHow many jobs has this company posted?\n_Type 0 to skip._", parse_mode="Markdown")
    return JOBS_COUNT

async def get_jobs_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    context.user_data['jobs_count'] = val if val != "0" else ""
    await update.message.reply_text("🔗 *Step 9/9 — Apply Link*\n\nEnter the application link:\n_Type 'none' to skip._", parse_mode="Markdown")
    return APPLY_LINK

async def get_apply_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    context.user_data['apply_link'] = "" if val.lower() == "none" else val
    preview = build_job_message(context.user_data)
    keyboard = [[InlineKeyboardButton("✅ Post to Channel", callback_data="confirm_yes"), InlineKeyboardButton("❌ Cancel", callback_data="confirm_no")]]
    await update.message.reply_text(f"👁 *Preview:*\n\n{preview}\n\n_Ready to post?_", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRM

async def confirm_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "confirm_no":
        await query.edit_message_text("❌ Cancelled. Use /postjob to start again.")
        return ConversationHandler.END
    data = context.user_data
    message_text = build_job_message(data)
    buttons = []
    if data.get('apply_link'):
        buttons.append([InlineKeyboardButton("📋 View Details / ዝርዝሩን ይመልከቱ", url=data['apply_link'])])
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=message_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons) if buttons else None)
        await query.edit_message_text("🎉 *Job posted successfully!*\n\nUse /postjob to post another.", parse_mode="Markdown")
    except Exception as e:
        await query.edit_message_text(f"❌ *Failed to post.*\n\nError: `{e}`", parse_mode="Markdown")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled. Use /postjob to start again.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("postjob", postjob_start)],
        states={
            JOB_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_job_title)],
            JOB_TYPE: [CallbackQueryHandler(get_job_type, pattern=r"^jt_\d+$")],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_location)],
            SALARY: [CallbackQueryHandler(get_salary, pattern=r"^sal_\d+$")],
            DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_deadline)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            COMPANY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company_name)],
            JOBS_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_jobs_count)],
            APPLY_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_apply_link)],
            CONFIRM: [CallbackQueryHandler(confirm_post, pattern=r"^confirm_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(conv_handler)
    print("🤖 Malachi Freelancer Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
