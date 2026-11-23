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

## ฟีเจอร์

- UI สไตล์ ChatGPT
- เลือกโมเดลได้
- **Web Search** (OpenRouter server tool)
- Tool calling (time, memory)
- ความจำถาวร
- เชื่อม OpenRouter

## หมายเหตุ

- Web search ใช้ครดิต OpenRouter (มีค่าใช้จ่าย)
- ต้องใส่ API Key
- Build ครั้งแรกอาจใช้เวลา 10-20 นาที

---

Made with love by Soul
