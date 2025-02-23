# Sử dụng image Python chính thức làm base
FROM python:3.9-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file requirements.txt và cài đặt các dependency
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Expose cổng 5000 (mặc định của Flask)
EXPOSE 5000

# Thiết lập biến môi trường cho Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Chạy ứng dụng
CMD ["flask", "run"]
