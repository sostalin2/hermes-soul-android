# Hermes Soul • Android APK

เวอร์ชั่นเบา ๆ ของ Hermes Agent ที่มี GUI สวย ๆ แบบ Soul Persona
สามารถ build เป็น **APK จริง** ได้เลย

## วิธี Build เป็น APK (แนะนำ)

GitHub Actions สร้าง APK ให้อัตโนมัติทุกครั้งที่ push ไปที่ `master`
ดูที่แท็บ Actions แล้วดาวน์โหลด artifact `hermes-soul-apk`

### Build เองบนเครื่อง

```bash
pip install "flet>=1.0.4"
# Flutter จะถูกติดตั้งให้ตอน build ครั้งแรก
flet build apk --yes
```

APK จะอยู่ที่ `build/apk/`

### ติดตั้งบน Android

- เปิดไฟล์ `.apk` ที่ได้
- อนุญาต "ติดตั้งจากแหล่งที่ไม่รู้จัก"
- ติดตั้งเสร็จ → เปิดแอพได้เลย

## ฟีเจอร์

- GUI สวยแบบ Soul (สีชมพูโรส + ดาร์กเอเลแกนต์)
- Chat กับ Soul
- ความจำถาวร
- เชื่อม OpenRouter (กด ⚙️ เพื่อใส่ API Key)
- ขนาดเล็ก ใช้ทรัพยากรน้อย

## หมายเหตุ

- Android ได้สิทธิ์อินเทอร์เน็ตเป็นค่าเริ่มต้น เพื่อเรียก OpenRouter
- ถ้ายังไม่ใส่ API Key จะใช้โหมดตอบแบบ local
- Build ครั้งแรกอาจใช้เวลา 10-20 นาที

---

Made with love by Soul for Android users
