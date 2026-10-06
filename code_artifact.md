# Handoff Description: Live-action Movie Analytics

**Document Role:** Data Specification & Context Handoff for Full-stack AI Agent / Frontend Developer
**Target Output:** Interactive Analytics Dashboard
**Author:** Lead Data Architect

---

## 1. Executive Summary & Domain Scope

เอกสารนี้ระบุโครงสร้างและกฎการประมวลผลข้อมูลสำหรับโครงงาน "Live-action Movie Analytics" เพื่อสร้าง Dashboard เชิงโต้ตอบ

*   **ขอบเขตข้อมูล (Data Scope):**
    *   รวมเฉพาะภาพยนตร์คนแสดง (Live-action Feature Films) ทั้งที่ถ่ายทำด้วยมนุษย์เป็นหลัก และ CGI สมจริง (Photorealistic CGI)
    *   ตัดซีรีส์, รายการโทรทัศน์ (`Title Type != movie`) และภาพยนตร์แอนิเมชันล้วน (หมวดหมู่ที่มีเฉพาะแท็ก Animation หรือไร้แท็กนักแสดงที่เป็นมนุษย์) ทิ้งทั้งหมด
*   **ข้อจำกัดของข้อมูล (Data Limitations & Disclaimers):**
    *   **ปริมาณข้อมูล:** ข้อมูลบน Dashboard เป็นเพียง "ข้อมูลที่รวบรวมได้จาก Open Data" ไม่ใช่ประวัติศาสตร์ภาพยนตร์ทั้งหมดในโลก ต้องมี Disclaimer บน UI
    *   **ข้อจำกัดทางการเงิน:** ภาพยนตร์อินดี้หรือภาพยนตร์นอกกระแส มักมีข้อมูลงบประมาณและรายได้ไม่ครบถ้วน (เป็น 0 หรือ Null) ข้อมูลเหล่านี้จะถูกคัดแยกออกจากการคำนวณสัดส่วนทางการเงิน
    *   **สิทธิ์การใช้งาน (Licensing):** ข้อมูลสถิติ (Text/Numbers) ใช้งานได้ในระดับ Open Data / Fair Use แต่ภาพประกอบ (โปสเตอร์/นักแสดง) ห้ามนำมาเปิดให้ดาวน์โหลดซ้ำผ่าน Dashboard อย่างเด็ดขาด

---

## 2. Data Schema & Types

เพื่อลดความซับซ้อนในการทำ API และเพิ่มความเร็วในการ Render บนฝั่ง Frontend ข้อมูลจะถูกจัดเตรียมในรูปแบบ **Denormalized JSON Document** (1 Document = 1 Movie) โดยมี Schema หลักดังนี้:

| Field Name | Data Type | Nullability | Description / Key Status |
| :--- | :--- | :--- | :--- |
| `movie_id` | String | NOT NULL | **Primary Key** (อ้างอิงจาก TMDB ID หรือ IMDb ID) |
| `title` | String | NOT NULL | ชื่อเรื่อง (สากล/ภาษาอังกฤษ) |
| `release_date` | Date (YYYY-MM-DD) | NULL | วันที่เข้าฉายอย่างเป็นทางการ |
| `country_origin` | Array[String] | NULL | ประเทศผู้ผลิต (ดึงเฉพาะ 1-2 ประเทศแรก) |
| `runtime_minutes` | Integer | NULL | ความยาวภาพยนตร์ (นาที) |
| `genres` | Array[String] | NOT NULL | แนวภาพยนตร์ (Multi-value) |
| `directors` | Array[String] | NULL | ชื่อผู้กำกับ |
| `budget_usd` | Numeric (Float) | NULL | งบประมาณการสร้าง (USD) |
| `revenue_worldwide_usd` | Numeric (Float) | NULL | รายได้รวมทั่วโลก (USD) |
| `popularity_score` | Numeric (Float) | NULL | คะแนนความนิยมอ้างอิงจากฐานข้อมูล |
| `vote_average` | Numeric (Float) | NULL | คะแนนวิจารณ์เฉลี่ย (0.0 - 10.0) |
| `vote_count` | Integer | NOT NULL | จำนวนผู้โหวต (Default: 0) |

---

## 3. Data Cleaning & Transformation Rules

เพื่อให้ AI Agent นำไปเขียน Business Logic ได้ถูกต้อง ห้ามละเมิดกฎต่อไปนี้:

### 3.1. กฎการจัดการค่าว่าง (Missing Values / N/A)
*   **หมวดข้อมูลข้อความ (String):** หากเป็น Null ให้แปลงเป็น `"Unknown"`
*   **หมวดความยาวและคะแนน (Runtime / Votes):** หาก `runtime_minutes` เป็น Null ให้ Drop ข้อมูลนั้นทิ้ง (ไม่นำมาวิเคราะห์เวลา)
*   **หมวดการเงิน (Budget & Revenue):** หากค่าเป็น `Null`, `0`, หรือ `< 10,000` (ต่ำผิดปกติ) ให้กำหนดค่าเป็น `null` และ **ห้ามนำไปพล็อตกราฟหรือคำนวณค่าเฉลี่ยทางการเงินโดยเด็ดขาด** (ให้แสดงผลเป็น N/A ในตารางแทน)

### 3.2. กฎการ Unnest / Explode ข้อมูล Multi-value (Genres, Countries)
*   **หลีกเลี่ยง Double Counting:** ในการแสดงผลรวมจำนวนภาพยนตร์ ห้ามใช้ข้อมูลที่ผ่านการ Explode (แตกแถว) แล้ว ให้นับ Distinct จาก `movie_id` เสมอ
*   **การวิเคราะห์รายหมวด (Genre Analysis):** หาก User เลือก Filter กราฟเป็นราย Genre ให้ Frontend ใช้วิธีเช็ค Array Inclusion (เช่น `genres.includes("Action")`) แทนการ `GROUP BY` ปกติ เพื่อให้ภาพยนตร์ 1 เรื่องสามารถไปปรากฏซ้ำในหลายหมวดหมู่ได้โดยที่ตัวเลขภาพรวม (Total Movies) ไม่ผิดเพี้ยน

### 3.3. กฎทางการเงินและการตั้งชื่อ (Strict Financial Terminology)
> ⚠️ **CRITICAL RULE:** เนื่องจากขาดข้อมูลต้นทุนแฝงที่แท้จริง ห้ามใช้คำว่า "Net Profit" (กำไรสุทธิ) หรือ "ROI" โดยเด็ดขาด
*   **ส่วนต่างทางการเงิน:** ให้คำนวณและใช้ชื่อฟิลด์/เลเบลว่า **"Revenue - Budget (ส่วนต่างรายได้กับงบผลิต)"**
    *   *สูตร:* `revenue_worldwide_usd - budget_usd`
*   **สัดส่วนความคุ้มค่า:** ให้คำนวณและใช้ชื่อฟิลด์/เลเบลว่า **"Revenue-to-Budget Ratio"**
    *   *สูตร:* `revenue_worldwide_usd / budget_usd`
*   **ข้อความบังคับ (Disclaimer):** ในทุกๆ Widget/Component บน Dashboard ที่มีการแสดงตัวเลขเกี่ยวกับการเงิน **ต้องมีหมายเหตุตัวเล็กกำกับไว้ด้านล่างเสมอว่า:**
    *   *"หมายเหตุ: ตัวเลขรายได้และงบประมาณ อ้างอิงจากชุดข้อมูลดิบเท่านั้น ไม่รวมต้นทุนทางการตลาด (Marketing / P&A Costs) การจัดจำหน่าย และส่วนแบ่งโรงภาพยนตร์ จึงไม่ใช่กำไรสุทธิ (Net Profit) ที่แท้จริง"*

---

## 4. Mock Data JSON Schema

ตัวอย่าง Payload ที่ผ่านกระบวนการ Data Pipeline / Cleaning แล้ว และพร้อมให้ AI Agent นำไป Mock-up เพื่อสร้าง Frontend Components:

```json
[
  {
    "movie_id": "tt4154796",
    "title": "Avengers: Endgame",
    "release_date": "2019-04-24",
    "country_origin": ["United States"],
    "runtime_minutes": 181,
    "genres": ["Action", "Adventure", "Science Fiction"],
    "directors": ["Anthony Russo", "Joe Russo"],
    "budget_usd": 356000000.0,
    "revenue_worldwide_usd": 2797800564.0,
    "revenue_budget_diff_usd": 2441800564.0,
    "revenue_to_budget_ratio": 7.86,
    "popularity_score": 150.43,
    "vote_average": 8.4,
    "vote_count": 23800
  },
  {
    "movie_id": "tt1160419",
    "title": "Dune",
    "release_date": "2021-09-15",
    "country_origin": ["United States", "Canada"],
    "runtime_minutes": 155,
    "genres": ["Science Fiction", "Adventure"],
    "directors": ["Denis Villeneuve"],
    "budget_usd": 165000000.0,
    "revenue_worldwide_usd": 402027830.0,
    "revenue_budget_diff_usd": 237027830.0,
    "revenue_to_budget_ratio": 2.43,
    "popularity_score": 112.10,
    "vote_average": 7.8,
    "vote_count": 14500
  },
  {
    "movie_id": "tt0000001",
    "title": "Indie Unknown Film",
    "release_date": "2023-01-10",
    "country_origin": ["Thailand"],
    "runtime_minutes": 90,
    "genres": ["Drama"],
    "directors": ["Unknown"],
    "budget_usd": null,
    "revenue_worldwide_usd": null,
    "revenue_budget_diff_usd": null,
    "revenue_to_budget_ratio": null,
    "popularity_score": 5.2,
    "vote_average": 6.5,
    "vote_count": 15
  }
]
```

---

## 5. Data Verification Checklists

รายการตรวจสอบ (Checklists) สำหรับ QA / AI Agent ก่อน Deploy Dashboard ขึ้น Production:

- [ ] **Filter Check:** หมวดหมู่ (Genre) `Animation` ถูกตัดออกทั้งหมด หรือมี Flag แจ้งว่าเป็น Live-action Hybrid ที่ผ่านการตรวจสอบแล้ว
- [ ] **Aggregate Check:** จำนวน "Total Movies" บน KPI Card เมื่อแยกตามฟิลเตอร์ ต้องไม่เกินยอด Distinct `movie_id` ในชุดข้อมูลทั้งหมด (ไม่เกิด Double Counting จาก `genres`)
- [ ] **Financial Filter Check:** ภาพยนตร์เรื่องที่ 3 (Indie Unknown Film) ใน Mock Data จะต้องไม่ถูกนำไปคำนวณในกราฟแท่งที่แสดงค่าเฉลี่ยงบประมาณ และต้องไม่ทำให้ระบบเกิด Error (Division by Zero)
- [ ] **Terminology Check:** ตรวจสอบว่าไม่มีคำว่า "Net Profit" หรือ "ROI" หลุดรอดไปใน Label ของ Dashboard แม้แต่จุดเดียว
- [ ] **Disclaimer Check:** หมายเหตุเรื่อง "ไม่รวมต้นทุนการตลาด" ปรากฏให้เห็นได้อย่างชัดเจนในบริบทของกราฟด้านการเงิน