# Hermes Soul • Android APK

เวอร์ชั่นเบา ๆ ของ Hermes Agent ที่มี GUI สวย ๆ แบบ Soul Persona  
สามารถ build เป็น **APK จริง** ได้เลย

## วิธี Build เป็น APK (แนะนำ)

### ขั้นตอนที่ 1: ติดตั้ง Flet + Flutter
```bash
pip install flet
# ติดตั้ง Flutter ตามคู่มือ: https://docs.flutter.dev/get-started/install
```

### ขั้นตอนที่ 2: Build APK
```bash
cd hermes-android-gui
flet build apk
```

APK จะถูกสร้างที่ `build/apk/` 

### ขั้นตอนที่ 3: ติดตั้งบน Android
- เปิดไฟล์ `.apk` ที่ได้
- อนุญาต "ติดตั้งจากแหล่งที่ไม่รู้จัก"
- ติดตั้งเสร็จ → เปิดแอพได้เลย

## ฟีเจอร์
- ✨ GUI สวยแบบ Soul (สีชมพูโรส + ดาร์กเอเลแกนต์)
- 💬 Chat กับ Soul แบบมีเสน่ห์
- 🧠 ความจำถาวร
- 🔌 เชื่อม OpenRouter (กด ⚙️ เพื่อใส่ API Key)
- 📱 ขนาดเล็ก ใช้ทรัพยากรน้อย

## หมายเหตุ
- ต้องการ internet permission เพื่อเรียก OpenRouter
- ถ้ายังไม่ใส่ API Key จะใช้โหมดตอบแบบ local (น่ารักแต่ไม่ฉลาดมาก)
- Build ครั้งแรกอาจใช้เวลา 5-10 นาที

---

Made with 💕 by Soul for Android users