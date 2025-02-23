#!/bin/bash
# Nếu chưa có virtual environment thì tạo
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Kích hoạt môi trường ảo
source venv/bin/activate

# Cài đặt các package cần thiết
pip install -r requirements.txt

echo "Cài đặt hoàn tất. Bạn có thể chạy ứng dụng với lệnh: flask run"
