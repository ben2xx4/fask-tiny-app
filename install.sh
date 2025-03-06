#!/bin/bash
# Tạo và kích hoạt virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài đặt các gói cần thiết
pip install -r requirements.txt

# Khởi tạo DB
python -c "from app import db, app; app.app_context().push(); db.create_all()"

echo "Cài đặt hoàn tất. Để chạy server: "
echo "  source venv/bin/activate"
echo "  python app.py"
