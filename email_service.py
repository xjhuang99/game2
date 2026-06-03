import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


def _smtp_configured() -> bool:
    return bool(
        os.getenv("SMTP_USER", "").strip()
        and os.getenv("SMTP_PASSWORD", "").strip()
    )


def send_verification_email(to_email: str, verify_url: str) -> tuple[bool, str]:
    """Send registration verification via Gmail SMTP. Returns (ok, message)."""
    if not _smtp_configured():
        return False, "SMTP not configured (set SMTP_USER and SMTP_PASSWORD in .env)."

    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    from_addr = os.getenv("SMTP_FROM", user).strip()
    app_name = os.getenv("APP_NAME", "ACTR Lab — AI Games")

    subject = f"[{app_name}] 请验证您的注册邮箱"
    text_body = f"""您好，

您正在注册 {app_name} 管理员账号。

请点击以下链接完成邮箱验证（24 小时内有效）：
{verify_url}

若您未发起注册，请忽略本邮件。

— {app_name}
"""
    html_body = f"""
    <div style="font-family: Inter, sans-serif; max-width: 520px; margin: 0 auto;">
      <h2 style="color: #2563eb;">{app_name}</h2>
      <p>您好，</p>
      <p>您正在注册管理员账号。请点击下方按钮完成邮箱验证（24 小时内有效）：</p>
      <p style="text-align: center; margin: 28px 0;">
        <a href="{verify_url}"
           style="background: #2563eb; color: #fff; padding: 12px 24px;
                  border-radius: 8px; text-decoration: none; font-weight: 600;">
          验证邮箱并激活账号
        </a>
      </p>
      <p style="color: #64748b; font-size: 14px;">或复制链接到浏览器：<br>{verify_url}</p>
      <p style="color: #94a3b8; font-size: 12px;">若您未发起注册，请忽略本邮件。</p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(from_addr, [to_email], msg.as_string())
        print(f"✅ [Email] Verification sent to {to_email}")
        return True, "验证邮件已发送，请查收 Gmail 收件箱（含垃圾箱）。"
    except smtplib.SMTPAuthenticationError:
        print("❌ [Email] Gmail authentication failed.")
        return False, "邮件发送失败：请检查 Gmail 应用专用密码是否正确。"
    except Exception as e:
        print(f"❌ [Email] Send failed: {e}")
        return False, f"邮件发送失败：{e}"
