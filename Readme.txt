ขั้นตอนการใช้งาน
1. docker compose up --build
2. container pdf-converter จะปิดตัวลงไปก่อนเพราะ ollama-server ยังไม่ได้ pull & run model
3. ถ้า ollama-server pull & run model เสร็จแล้วให้ start pdf-converter container ใหม่อีกครั้ง (docker start pdf-converter)
4. ถ้า pdf-converter ทำงานเสร็จแล้ว copy ไฟล์ txt (docker cp pdf-converter:/app/doc_text ./doc_text)
5. เมื่อ ssh เข้าไปใช้ docker บน server มหาลัย ต้อง copy doc_text ออกมาเครื่อง local อีกที (scp user@192.168.1.10:/home/user/doc_text/file.txt ./doc_text/
