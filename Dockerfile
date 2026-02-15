# Python-ning yengil versiyasidan foydalanamiz
FROM python:3.10-slim

# Ishchi katalogni belgilaymiz
WORKDIR /app

# Tizim paketlarini yangilaymiz va Pillow uchun kerakli kutubxonalarni o'rnatamiz
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Kerakli fayllarni nusxalaymiz
COPY requirements.txt .

# Kutubxonalarni o'rnatamiz
RUN pip install --no-cache-dir -r requirements.txt

# Loyihaning barcha fayllarini nusxalaymiz
COPY . .

# Dasturni ishga tushiramiz
CMD ["python", "main.py"]
