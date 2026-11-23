# Hermes Soul • Android APK

เวอร์ชันเบา ๆ ของ Hermes Agent ที่มี GUI สวย ๆ แบบ Soul Persona
สามารถ build เป็น **APK จริง** ได้เลย

## วิธี Build เป็น APK (แนะนำ)

GitHub Actions สร้าง APK ให้อัตโนมัติทุกครั้งที่ push ไปที่ `master`
ดูที่แท็บ Actions แล้วดาวน์โหลด artifact `hermes-soul-apk`

### Build เองบนเครื่อง

```bash
pip install "flet>=1.0.4"
flet build apk --yes
```

APK จะอยู่ที่ `build/apk/`

## ฟีเจอร์

- UI สไตล์ ChatGPT (ฟองมืด ดาร์โทน)
- เลือกโมเดลได้จาก dropdown ด้านบน
- Tool calling (get time, save/get memory)
- Chat กับ Soul
- ความจำถาวร
- เชื่อม OpenRouter (API Key)
- ขนาดเล็ก ใช้ทรัพยากรน้อย

## หมายเหตุ

- ต้องใส่ API Key จาก openrouter.ai
- ถ้าไม่ได้ใส่จะตอบแบบ local ง่ายๆ
- Build ครั้งแรกอาจใช้เวลา 10-20 นาที

---

Made with love by Soul for Android users
