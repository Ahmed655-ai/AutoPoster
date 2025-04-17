#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import asyncio
from telethon import TelegramClient, errors

# === 1) تأكد من وجود مجلّد sessions لحفظ الجلسة ===
os.makedirs('sessions', exist_ok=True)

# === 2) الصق هنا بيانات API من my.telegram.org ===
API_ID   = 26314619
API_HASH = '2a5d89e2149922c575884576e95d6ddb'

# === 3) إنشاء عميل Telethon مع تحديد ملف الجلسة ===
client = TelegramClient('sessions/session', API_ID, API_HASH)


async def main():
    # --- 4) تسجيل الدخول أو استخدام الجلسة المحفوظة ---
    await client.connect()
    if not await client.is_user_authorized():
        # 4.1) طلب رقم الهاتف وإرسال رمز التفعيل
        phone = input("أدخل رقم الهاتف بالصيغة الدولية (مثال: +9647712345678): ").strip()
        try:
            await client.send_code_request(phone)
        except errors.PhoneNumberInvalidError:
            print("⚠️ رقم الهاتف غير صالح. تأكد من إدخاله بالصيغة الدولية.")
            return
        except Exception as e:
            print(f"⚠️ خطأ أثناء إرسال رمز التفعيل: {e}")
            return

        # 4.2) إدخال رمز التفعيل وتسجيل الدخول
        code = input("أدخل رمز التفعيل الذي وصلك: ").strip()
        try:
            await client.sign_in(phone=phone, code=code)
        except errors.SessionPasswordNeededError:
            # 2FA مُفعّل
            pwd = input("أدخل كلمة المرور للتحقق بخطوتين: ").strip()
            try:
                await client.sign_in(password=pwd)
            except Exception as e:
                print(f"⚠️ كلمة المرور الثنائية غير صحيحة أو حدث خطأ: {e}")
                return
        except errors.PhoneCodeInvalidError:
            print("⚠️ رمز التفعيل غير صحيح.")
            return
        except Exception as e:
            print(f"⚠️ خطأ أثناء تسجيل الدخول: {e}")
            return

        print("✅ تمّ تسجيل الدخول بنجاح!")
    else:
        print("✅ الجلسة محفوطة بالفعل، تمّ تسجيل الدخول أوتوماتيكياً.")

    # --- 5) التحقق من قناة النشر ---
    channel_link = input("أدخل رابط القناة (أو اسم المستخدم @channel): ").strip()
    try:
        channel_entity = await client.get_entity(channel_link)
    except Exception as e:
        print(f"⚠️ لم أتمكّن من العثور على القناة أو لست عضواً بها: {e}")
        return

    # --- 6) إعداد الفاصل الزمني والنص ---
    try:
        delay = float(input("أدخل الوقت بين كل رسالة وأخرى بالثواني (مثال: 10): ").strip())
        if delay <= 0:
            raise ValueError
    except ValueError:
        print("⚠️ الرجاء إدخال رقم موجب للفاصل الزمني.")
        return

    message = input("أدخل النص المراد نشره (عربي، إنجليزي، ورموز فقط): ").strip()
    if not message:
        print("⚠️ النص لا يمكن أن يكون فارغاً.")
        return

    print(f"\n⏳ يبدأ النشر كل {delay} ثانية في القناة {channel_link}")
    print("   (اضغط Ctrl+C لإيقاف الأداة)\n")

    # --- 7) حلقة النشر المستمر ---
    try:
        while True:
            await client.send_message(entity=channel_entity, message=message)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] ✅ تم نشر الرسالة: {message}")
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف النشر بواسطتك.")
    except Exception as e:
        print(f"⚠️ حدث خطأ أثناء النشر: {e}")

    # --- 8) قطع الاتصال ---
    await client.disconnect()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())