# Business Requirements Document (BRD) & Data Logic Handoff
**Project:** Premium Interactive Movie Analytics Dashboard (Live-action)
**Target Audience:** Developer Team (Backend & Frontend)

---

## 1. Data Schema & Types
โครงสร้างข้อมูลหลักที่ Backend ต้องจัดเตรียมและส่งให้ Frontend ผ่าน API (1 Object = 1 Movie):

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `movie_id` | String | Primary Key |
| `title` | String | ชื่อภาพยนตร์ |
| `release_year` | Integer | ปีที่เข้าฉาย (Extract มาจาก Release Date) |
| `runtime_minutes` | Integer | ความยาว (นาที) |
| `genres` | Array[String] | แนวภาพยนตร์ |
| `overview` | String | เรื่องย่อ |
| `directors` | Array[String] | รายชื่อผู้กำกับ |
| `cast` | Array[Object] | รายชื่อนักแสดง `[{ name: "", image_url: "" }]` |
| `budget_usd` | Numeric | งบประมาณสร้าง (หากเป็น 0 หรือ Null ให้ข้ามการคำนวณ) |
| `revenue_usd` | Numeric | รายได้รวมทั่วโลก |
| `vote_average` | Numeric | คะแนนโหวต (0.0 - 10.0) |
| `vote_count` | Integer | จำนวนผู้โหวต |
| `popularity_score`| Numeric | ค่าความนิยม |
| `poster_url` | String | ลิงก์รูปภาพโปสเตอร์ |
| `backdrop_url` | String | ลิงก์รูปภาพพื้นหลัง |

---

## 2. Logic การคำนวณ (Calculation Logic)
⚠️ **กฎเหล็กทางการเงิน:** ห้ามใช้คำว่า "Net Profit", "กำไรสุทธิ" หรือ "ROI" โดยเด็ดขาด เนื่องจากข้อมูล Open Data ไม่ครอบคลุมต้นทุนแฝงและการตลาด

*   **Financial Difference (ส่วนต่างรายได้กับงบผลิต):**
    *   `Formula:` `revenue_usd - budget_usd`
    *   `UI Label:` "REVENUE - BUDGET"
*   **Revenue-to-Budget Ratio (สัดส่วนความคุ้มทุน):**
    *   `Formula:` `revenue_usd / budget_usd`
    *   `UI Label:` "REVENUE/BUDGET RATIO"
*   **Missing Data Logic:**
    *   หาก `budget_usd` หรือ `revenue_usd` เป็น Null ให้แสดงผลว่า "N/A" หรือ "ไม่มีข้อมูล"
    *   ต้องมีข้อความ Disclaimer เล็กๆ กำกับที่กรอบ Financial เสมอว่า *"อ้างอิงจากชุดข้อมูลดิบ ไม่รวมต้นทุนทางการตลาด"*

---

## 3. หน้า Home Page Components (อ้างอิง Image 2)
หน้าหลักสำหรับการค้นหาและแนะนำภาพยนตร์

1.  **Top Nav:**
    *   Search Bar สำหรับค้นหาชื่อภาพยนตร์
    *   เมนูหมวดหมู่ (Movies, TV Series, Animation, ฯลฯ)
    *   User Profile & Notification Icon
2.  **Left Sidebar:**
    *   Navigation Icons แนวตั้ง (Home, Favorite, Download, Profile, Settings)
3.  **New Trailer (Left Panel):**
    *   รายการตัวอย่างภาพยนตร์ใหม่ จัดเรียงแนวตั้ง แสดงรูป Thumbnail และปุ่ม Play
4.  **Continue Watching (Left Panel - Bottom):**
    *   ประวัติการรับชมล่าสุด (ใช้ Mock data เป็นภาพยนตร์ Live-action)
5.  **Main Featured (Hero Section):**
    *   ภาพยนตร์ Trending ขนาดใหญ่สุด
    *   แสดง Genre Tags, ชื่อเรื่อง, เรื่องย่อสั้นๆ พร้อมปุ่ม "Watch" และ "Download"
6.  **Bottom Carousel (You Might Like):**
    *   เลื่อนซ้าย-ขวา (Horizontal Scroll)
    *   เมื่อ Hover ให้ขยาย Scale การ์ดเล็กน้อย (1.03-1.05) เพื่อตอบสนองต่อผู้ใช้

---

## 4. หน้า Detail Page Components (อ้างอิง Image 1)
หน้าแสดงข้อมูลวิเคราะห์เจาะลึกของภาพยนตร์รายเรื่อง

1.  **Movie Selector / Hero Image:**
    *   ภาพโปสเตอร์แนวตั้งด้านซ้าย
    *   มี Dropdown ด้านบนสำหรับเลือกเปลี่ยนภาพยนตร์ (เมื่อเปลี่ยน ข้อมูลทั้งหน้าต้องอัปเดตทันทีแบบ Reactive)
2.  **KPI Cards (2x2 Grid):**
    *   **VOTES:** ดึงจาก `vote_count`
    *   **POPULARITY:** ดึงจาก `popularity_score`
    *   **DURATION:** ดึงจาก `runtime_minutes` + "min."
    *   **YEAR:** ดึงจาก `release_year`
3.  **Cast Panel:**
    *   แสดงรูปนักแสดงและชื่อ เรียงแนวนอน
4.  **Overview Panel:**
    *   ข้อความสรุปเรื่องย่อ (`overview`)
5.  **Financials Panel:**
    *   **BUDGET:** ดึงจาก `budget_usd` (จัดรูปแบบตัวเลขให้สวยงาม เช่น $1.2B)
    *   **REVENUE:** ดึงจาก `revenue_usd`
    *   รวมถึงค่าส่วนต่างตาม Logic ที่กำหนดไว้
6.  **Movie Score (TMDB Score):**
    *   กราฟวงแหวน (Radial Chart / Donut Chart)
    *   แสดงตัวเลข `vote_average` ตรงกลาง
7.  **Similar Movies Comparison:**
    *   กราฟแท่งแนวนอน (Horizontal Bar Chart)
    *   เปรียบเทียบคะแนน Popularity ของเรื่องปัจจุบัน กับเรื่องอื่นที่มี Genre เดียวกัน