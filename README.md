# Live-action Movie Analytics Dashboard

## 1. Project Overview
**Movie Analytics Dashboard** เป็นโปรเจกต์เชิงวิเคราะห์ข้อมูล (Data Analytics) ที่นำเสนอในรูปแบบ Web Application แบบหน้าเดียว (Single Page Application) โดยมีจุดเด่นคือการออกแบบ User Interface ที่ทันสมัยด้วยสไตล์ **Apple Vision Pro UI (Glassmorphism)** ที่ใช้ความโปร่งแสง การเบลอพื้นหลัง (Backdrop-blur) และแอนิเมชันที่ลื่นไหล เพื่อให้ผู้ใช้งานได้รับประสบการณ์การวิเคราะห์ข้อมูลระดับพรีเมียม

ระบบถูกออกแบบมาเพื่อวิเคราะห์ข้อมูลเชิงลึกของภาพยนตร์คนแสดง (Live-Action) โดยเน้นไปที่ความสัมพันธ์ระหว่าง งบประมาณ (Budget), รายได้ (Revenue), และความนิยม (Popularity)

## 2. Data Sources & Attribution
ข้อมูลทั้งหมดที่ใช้ในโปรเจกต์นี้อ้างอิงจาก **Open Data** อย่างเป็นทางการ:
- **Dataset:** TMDB 5000 Movies Dataset (ดึงจาก The Movie Database - TMDB)
- **Total Records:** ผ่านกระบวนการ Data Cleaning และมีข้อมูลที่ถูกนำมาใช้ทั้งสิ้น **4,801 เรื่อง**
- **Data Constraints & Disclaimers:** 
  - ข้อมูลในส่วนของรายชื่อนักแสดง (Cast) ยังไม่มีในชุดข้อมูลพื้นฐานชุดนี้ ระบบจึงแสดงผลในรูปแบบ Empty State ("ไม่มีข้อมูลนักแสดงในชุดข้อมูลนี้") เพื่อความโปร่งใสและหลีกเลี่ยงการสร้างข้อมูลเท็จ (No Hallucination)
  - ข้อมูลทางการเงิน (Financials) ที่ต่ำกว่า $10,000 หรือเป็นค่าว่าง จะถูกจัดเป็น `Null` เพื่อไม่ให้การคำนวณสัดส่วนรายได้ผิดเพี้ยน
  - ระบบยึดหลักการนำเสนอข้อมูลอย่างตรงไปตรงมา โดยใช้คำว่า **"ส่วนต่างรายได้กับงบผลิต"** และ **"Revenue-to-Budget Ratio"** แทนคำว่า Net Profit หรือ ROI เนื่องจากเป็นรายได้จาก Box Office ไม่ใช่กำไรสุทธิทางบัญชี

## 3. System Architecture
ระบบแบ่งออกเป็น 2 ส่วนหลักๆ (Data Pipeline & Frontend):

- **Data Pipeline (Python / Pandas):**
  - `src/pipeline/download.py`: ทำหน้าที่ดาวน์โหลดชุดข้อมูล Raw Data (CSV) จาก Open Source Repository มาเก็บไว้ใน `data/raw/`
  - `src/pipeline/clean.py`: ทำ Data Transformation เช่น การกรองหนังแอนิเมชันออก, จัดการ Missing Values, คำนวณตัวแปรทางการเงินใหม่ และบันทึกเป็น `data/processed/movies_clean.json`
- **Frontend Dashboard (React / Tailwind / Recharts):**
  - ไฟล์ `index.html` เพียงไฟล์เดียว ทำหน้าที่โหลด React (UMD), Tailwind CSS (CDN), และ Recharts
  - โหลดไฟล์ `movies_clean.json` ขึ้นมาบน Client-side เพื่อการเรนเดอร์และจัดเรียงข้อมูลแบบ Interactive อย่างรวดเร็ว (ไม่ต้องมี Backend Server)

## 4. How to Run (ขั้นตอนการติดตั้งและการใช้งาน)
1. **เตรียมความพร้อม:** ตรวจสอบว่าในเครื่องมี Python ติดตั้งอยู่
2. **ติดตั้งไลบรารี:**
   ```bash
   pip install -r requirements.txt
   ```
3. **รัน Data Pipeline:** 
   เพื่อดาวน์โหลดและทำความสะอาดข้อมูล (ขั้นตอนนี้จะสร้างไฟล์ `movies_clean.json`)
   ```bash
   python src/pipeline/download.py
   ```
4. **เปิด Web Server:** 
   ใช้คำสั่งเพื่อเสิร์ฟไฟล์ HTML
   ```bash
   python -m http.server 8080 --bind 127.0.0.1
   ```
5. **เข้าใช้งาน:** เปิด Web Browser และเข้าไปที่ `http://127.0.0.1:8080`

## 5. Key Analytics Questions
Dashboard ตัวนี้ถูกออกแบบมาเพื่อช่วยตอบคำถามวิเคราะห์ทางธุรกิจ (Business Questions) เหล่านี้:
1. **Financial Insights:** งบประมาณการสร้างภาพยนตร์ (Budget) มีผลต่อสัดส่วนรายได้ (Revenue-to-Budget Ratio) หรือไม่?
2. **Popularity Analysis:** ภาพยนตร์ที่มีคะแนนรีวิวสูง (TMDB Score) จะมีความนิยมสูงตามไปด้วยเสมอไปหรือไม่ เมื่อเปรียบเทียบในหมวดหมู่เดียวกัน?
3. **Similar Movies Benchmark:** เมื่อนำภาพยนตร์ที่อยู่ในแนว (Genre) เดียวกันมาเทียบกัน เรื่องใดสามารถทำยอดความนิยมได้สูงที่สุด?
4. **Outlier Detection:** มีภาพยนตร์แนวอินดี้ฟอร์มเล็กเรื่องไหนบ้างที่งบประมาณต่ำ แต่สร้างส่วนต่างรายได้ (Revenue Diff) ได้มหาศาล?
5. **Quality vs. Financials:** ความสัมพันธ์ระหว่างระยะเวลาฉาย (Duration) และคะแนนรีวิว มีนัยสำคัญต่อความคุ้มทุนในการผลิตหรือไม่?
