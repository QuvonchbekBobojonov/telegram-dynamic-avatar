# PythonAnywhere-ga O'rnatish Bo'yicha Yo'riqnoma

Ushbu loyihani PythonAnywhere-da doimiy ishlaydigan qilish uchun quyidagi qadamlarni bajaring:

## 1. Loyihani Yuklash
PythonAnywhere-ga loyiha fayllarini yuklang (zip qilib yuklasangiz osonroq bo'ladi):
- `main.py`
- `requirements.txt`
- `tg.session` (agar lokalda login qilib bo'lgan bo'lsangiz)
- `fonts/` papkasi
- `images/` papkasi

## 2. Virtual Muhitni Sozlash
PythonAnywhere konsolida (Bash console) quyidagi buyruqlarni kiriting:

```bash
# Loyiha papkasiga kiring
cd TelegramProfile

# Virtual muhit oching
mkvirtualenv venv --python=python3.10

# Zaruriy kutubxonalarni o'rnating
pip install -r requirements.txt
```

## 3. Dasturni Ishga Tushirish
Dasturni doimiy (fon rejimida) ishlaydigan qilish uchun:

### Bepul (Free) akauntlar uchun:
Bepul akauntlarda "Always-on tasks" yo'q. Shu sababli siz dasturni oddiy Bash konsolida ishga tushirishingiz mumkin:
```bash
python main.py
```
*Eslatma: Konsol yopilsa yoki ma'lum vaqtdan so'n dastur to'xtashi mumkin.*

### Pullik (Paid) akauntlar uchun:
1. "Tasks" bo'limiga o'ting.
2. "Always-on tasks" qismiga quyidagi buyruqni yozing:
   `/home/USERNAME/.virtualenvs/venv/bin/python /home/USERNAME/TelegramProfile/main.py`
   *(USERNAME o'rniga o'zingizni foydalanuvchi nomingizni yozing)*
3. "Create" tugmasini bosing.

## Muhim Eslatmalar:
- **Telegram API:** Agar sizda "Free" akaunt bo'lsa, Telegram-ga ulanishda muammo bo'lishi mumkin (PythonAnywhere faqat whitelist-dagi saytlarga ruxsat beradi). Agar xato bersa, Telegram API manzillari PythonAnywhere whitelist-ida bor yoki yo'qligini tekshirish kerak.
- **Session:** `tg.session` faylini o'zingiz bilan birga yuklasangiz, qayta kod so'ramaydi.
