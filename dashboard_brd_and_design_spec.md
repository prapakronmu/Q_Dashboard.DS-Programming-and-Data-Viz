# Dashboard_BRD_and_Design_Spec.md

เอกสารข้อกำหนดความต้องการทางธุรกิจและข้อกำหนดการออกแบบ (Business Requirements Document & Design Specification) ฉบับนี้จัดทำขึ้นโดย Lead Business Analyst และ Senior UX/UI Designer เพื่อใช้เป็นข้อกำหนดมาตรฐาน (Technical & Design Handover Spec) สำหรับส่งมอบให้ **AI Developer (Antigravity)** นำไปพัฒนาโปรแกรมโดยตรง

---

# 1. Executive Summary & Architecture Overview

## 1.1 Product Vision
ระบบ **Interactive Live-Action Movie Analytics Dashboard** ออกแบบมาเพื่อนำเสนอข้อมูลภาพยนตร์คนแสดง (Live-action) จากทั่วโลกในรูปแบบ Visual Analytics ที่ล้ำสมัย ใช้งานง่าย มีความสวยงามระดับพรีเมียม ตอบโจทย์ทั้งมิติการสตรีมมิ่งความบันเทิงและการวิเคราะห์เชิงลึก

## 1.2 Design Reference Mapping
* **Image 2 (Home Page Reference):** ใช้เป็นโครงสร้าง Layout หลักของหน้าแรก (Home Page Layout), สไตล์ของ Top Navigation, Floating Left Sidebar และโครงสร้างภาพพื้นหลังแบบ Cinematic Dynamic Background ของทั้งแอปพลิเคชัน
* **Image 1 (Movie Detail Page Reference):** ใช้เป็นโครงสร้างการจัดวางข้อมูลในหน้ารายละเอียดภาพยนตร์ (Movie Detail Page Layout) รวมไปถึงระบบ KPI Cards, Financial Metrics, Cast List, และ Analytics Charts
* **Overall Aesthetics Concept:** ผสมผสานสไตล์ **Apple Vision Pro Spatial UI** + **Premium Streaming Platform** (เช่น Apple TV+ / Netflix) + **Cinematic Data Analytics Dashboard**

---

# 2. Design Tokens & Global Visual Style

```css
/* Design Tokens Baseline */
:root {
  /* Background Overlay & Effects */
  --bg-backdrop-blur: blur(40px) saturate(70%);
  --bg-overlay-tint: rgba(10, 10, 14, 0.75);
  
  /* Glassmorphism Styling */
  --glass-bg: rgba(20, 20, 24, 0.60);
  --glass-blur: blur(24px);
  --glass-border: 1px solid rgba(255, 255, 255, 0.12);
  --glass-radius-lg: 24px;
  --glass-radius-md: 18px;
  --glass-radius-sm: 12px;
  --glass-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);

  /* Color Palette */
  --color-accent-coral: #FF6847;       /* Primary Accent (Graphs, Highlights, Active States) */
  --color-accent-hover: #FF8266;
  --color-text-primary: #FFFFFF;       /* Primary Text */
  --color-text-secondary: #9CA3AF;     /* Muted / Subtitle Text */
  --color-text-tertiary: #6B7280;      /* Disabled / Placeholder Text */
  --color-card-dark: rgba(15, 15, 18, 0.75);
  --color-status-success: #10B981;
  --color-status-warning: #F59E0B;

  /* Typography */
  --font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
```

## 2.1 Dynamic Backdrop Surface (ภาพพื้นหลังไดนามิก)
* **Behavior:** ภาพพื้นหลัง Full-Screen หลังสุด จะปรับเปลี่ยนภาพฉากหลัง (Backdrop Image) ไปตามภาพยนตร์ที่ผู้ใช้เลือก หรือตามภาพยนตร์ที่กำลังโฟกัสอยู่บนหน้าจอ
* **Shader & Filter Specification:**
  * `filter: blur(45px) saturate(60%) contrast(90%)`
  * ครอบทับด้วย Gradient Overlay: `linear-gradient(180deg, rgba(10, 10, 14, 0.60) 0%, rgba(10, 10, 14, 0.92) 100%)`
  * เมื่อมีการเปลี่ยนหนัง ให้ใช้ CSS Transition `opacity 0.8s ease-in-out` เพื่อความนุ่มนวล

## 2.2 Glassmorphism Surface Rules
* **Container Cards:** ใช้พื้นหลังสีเทาดำโปร่งแสง `rgba(20, 20, 24, 0.60)` ร่วมกับ `backdrop-filter: blur(18px - 30px)`
* **Borders:** เส้นขอบบางเด่นชัด `1px solid rgba(255, 255, 255, 0.12)` หรือ Gradient Border ขาวบาง
* **Corner Radius:** มุมโค้งขนาด `18px` สำหรับ Card ย่อย และ `24px` สำหรับ Panel ใหญ่

---

# 3. Structural Layout & Component Specifications

แอปพลิเคชันแบ่งออกเป็น 2 หน้าหลัก (Two-Page Navigation Architecture):

```
[ Layout Frame ]
  ├── Left Sidebar (Global Floating Dock)
  ├── Main Viewport
  │     ├── [ Router: / (Home Page) ]
  │     │     ├── Top Nav Bar
  │     │     ├── Hero Featured Movie Section
  │     │     ├── Left Panel: New Trailers & Continue Watching
  │     │     └── Bottom Section: "You Might Like" Carousel
  │     └── [ Router: /movie/[id] (Movie Detail Analytics) ]
  │           ├── Top Bar: Movie Selector Dropdown
  │           ├── Left Column: Poster + 2x2 KPI Cards
  │           ├── Center Column: Cast Grid + Overview + Similar Movies Chart
  │           └── Right Column: Financials Card + TMDB Donut Score Chart
```

---

## 3.1 Global Shared Components

### A. Floating Left Sidebar (Global Navigation)
* **Position:** Fixed ด้านซ้ายมือของหน้าจอ ลอยเหนือพื้นหลัง (`z-index: 100`)
* **Visual:** แถบแนวตั้งทรงแคปซูล (Pill Shape) กระจกฝ้า `backdrop-filter: blur(20px)`
* **Icons List:** 
  1. `Home` (Link to `/`)
  2. `Favorites` (Bookmark Icon)
  3. `Downloads` / `Saved` (Tray Icon)
  4. `Analytics / Detail` (Link to `/movie/[id]`)
  5. `Settings` (Gear Icon)
* **Micro-interaction:** เมื่อ Hover ไอคอนจะสว่างขึ้นเป็นสีขาวพร้อมเรืองแสงอ่อนๆ (Glow)

### B. Image Fallback & Placeholder Logic
* **Poster / Image Missing Strategy:** หากไม่มีรูปภาพใน Dataset (`poster_path == null` หรือ โหลดรูปไม่สำเร็จ)
  * ห้ามแสดง Icon ภาพแตก (Broken Link)
  * ให้สร้าง Dynamic SVG Canvas Placeholder ที่ใช้ Background สีเข้ม แบบ Gradient ดีไซน์เรียบหรู พร้อมโลโก้แผ่นฟิล์ม และพิมพ์ชื่อเรื่องภาษาอังกฤษแบบสังเขปไว้ตรงกลาง

---

## 3.2 Page 1: Home Page (`/`) Requirements

### 1. Top Navigation Bar
* **Search Input:** ช่องค้นหาแก้วโปร่งแสง พร้อมไอคอนแว่นขยาย พิมพ์ค้นหาชื่อเรื่องได้ Real-time
* **Category Filters (Pills):** ปุ่มสวิตช์เลือกหมวดหมู่ เช่น `Movies` (Selected By Default), `Action`, `Drama`, `Sci-Fi`, `More`
* **User Profile & Notifications:** ปุ่มโปรไฟล์ผู้ใช้ และกระดิ่งแจ้งเตือนมุมขวาบน

### 2. Hero Featured Movie Section
* **Content Display:** โชว์ภาพยนตร์ไฮไลท์ประจำวัน/ประจำสัปดาห์
* **Elements:**
  * Tag สถานะ (เช่น `🔥 Now Trending` หรือ `Featured`)
  * Genre Pills (เช่น `Action`, `Adventure`)
  * ชื่อเรื่องขนาดใหญ่ (H1 Display Bold)
  * Logline/Overview แบบย่อ (ไม่เกิน 3 บรรทัด)
  * ปุ่ม Action: `Watch Trailer` (ปุ่มสีขาว ข้อความดำ), `Details` (ปุ่มกระจกโปร่งแสง Link ไปยัง `/movie/[id]`)

### 3. Left Panel Widgets
* **New Trailer Section:**
  * แสดงรายการภาพยนตร์ตัวอย่างสั้น 2-3 รายการ พร้อมปุ่ม Play บน Thumbnail
* **Continue Watching Section (Empty State Handling):**
  * กรณียังไม่มีประวัติการรับชมใน LocalStorage ให้แสดง **Empty State Component**:
    * ไอคอนฟิล์มหนังแบบจาง
    * ข้อความ: *"ไม่มีรายการที่รับชมค้างไว้"*
    * Subtext: *"ค้นหาภาพยนตร์คนแสดงที่คุณสนใจเพื่อเริ่มชม"*

### 4. Bottom Section: "You Might Like" Carousel
* **Component Type:** Horizontal Scrollable Carousel (การ์ดหนัง 5-7 เรื่อง)
* **Card Specs:**
  * แสดงภาพโปสเตอร์ทรงตั้งมุมมน
  * Badge บอกประเภทแนวภาพยนตร์
  * ชื่อเรื่องภาษาอังกฤษ และปีที่ฉาย
  * ปุ่ม Play ลอยมุมขวาล่างของการ์ด
* **Hover Interaction:** เมื่อเอาเม้าส์ไปชี้ การ์ดจะขยายใหญ่ขึ้นเล็กน้อย (`transform: scale(1.04); transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);`)
* **Click Behavior:** คลิกการ์ดเพื่อเปลี่ยนเส้นทางไปยังหน้า `/movie/[id]` ของภาพยนตร์เรื่องนั้น

---

## 3.3 Page 2: Movie Detail Page (`/movie/[id]`) Requirements

### 1. Movie Selector (Top Selector Bar)
* **UI Component:** Dropdown Select Box สไตล์ Glassmorphism ลอยตัวอยู่มุมบนซ้ายของการ์ด
* **Functionality:** สามารถกดเลือกเพื่อเปลี่ยนไปดูข้อมูลภาพยนตร์คนแสดงเรื่องอื่นใน Dataset ได้ทันทีโดยไม่ต้องกลับไปหน้า Home

### 2. Poster & KPI Cards (2x2 Grid Layout)
* **Main Poster Frame:** แสดงภาพโปสเตอร์ฉากหน้าความละเอียดสูงพร้อมเส้นขอบกระจกโปร่งแสง
* **KPI Cards Grid (2 Rows x 2 Columns):**
  1. **VOTES:** จำนวนคนโหวตทั้งหมด (จัดรูปแบบตัวเลข มีเครื่องหมายจุลภาค เช่น `1,453` หรือ `282,270`)
  2. **POPULARITY:** ค่าความนิยมตาม Metric ของ TMDB (เช่น `282.27`)
  3. **DURATION:** ความยาวภาพยนตร์ แสดงในรูปแบบ `XXX min.` (เช่น `198 min.`)
  4. **YEAR:** ปีที่ออกฉาย (เช่น `2025`)
* **Data Fallback Logic:** หากข้อมูลตัวใดเป็น Null/Empty ให้แสดงข้อความ `"ไม่มีข้อมูล"` หรือ `"N/A"` เสมอ ห้ามปล่อยเป็นช่องว่างหรือเลข 0 ที่ทำให้ผู้ใช้นิยามความหมายผิด

### 3. Cast Panel (นักแสดงหลัก)
* **UI Component:** แถบแนวนอนแสดงรูปถ่ายส่วนหัวนักแสดง (Avatar Circles/Rounded Squares)
* **Data Elements:** ภาพถ่ายนักแสดง + ชื่อจริงของนักแสดง (เช่น Jack Champion, Zoe Saldaña)
* **Overflow Behavior:** หากมีนักแสดงมากกว่า 6 คน ให้สามารถเลื่อนสไลด์ทางขวาได้ (Horizontal Scroll)

### 4. Overview Section
* **UI Component:** การ์ดข้อความโปร่งแสง แสดงเรื่องย่อ/เนื้อหาโดยรวมของภาพยนตร์อย่างละเอียด

### 5. Financials Card (ข้อมูลทางการเงิน)
* **CRITICAL DATA RULE (ข้อห้ามเด็ดขาด):** 
  * ❌ **ห้ามใช้คำว่า "Net Profit" หรือ "กำไรสุทธิ"** บน Dashboard นี้โดยเด็ดขาด เนื่องจากเป็นข้อมูลทางการเงินที่ไม่เที่ยงตรงสำหรับธุรกิจภาพยนตร์ (ไม่ได้คำนวณส่วนแบ่งโรงหนัง/ค่าการตลาด)
* **Required Financial Metrics:**
  1. **BUDGET:** งบประมาณการสร้าง (จัดรูปแบบสกุลเงิน เช่น `$120,000,000` หรือ `$1.2B`)
  2. **REVENUE:** รายได้รวมทั่วโลก (จัดรูปแบบสกุลเงิน เช่น `$350,000,000` หรือ `$350M`)
  3. **ส่วนต่างรายได้กับงบผลิต:** แสดงผลลัพธ์จากสูตร $Revenue - Budget$ (เช่น `+$230,000,000`) โดยใช้สีเขียวหากเป็นบวก และสีแดงหากติดลบ
  4. **Revenue-to-Budget Ratio:** แสดงอัตราส่วนสัดส่วนรายได้เทียบงบผลิต $\frac{Revenue}{Budget}$ (เช่น `2.92x`)
* **Missing Value Logic:** หากงบประมาณหรือรายได้เป็น `0` ให้แสดงเป็น `"ไม่มีข้อมูลทางการเงิน"` หรือ `"N/A"` แทนการแสดงผลลัพธ์ติดลบที่ผิดพลาด

### 6. TMDB Score (Donut Chart Widget)
* **UI Component:** กราฟวงกลมแบบมีรูตรงกลาง (Donut Chart)
* **Naming Condition:** ใช้ชื่อหัวข้อว่า **"TMDB SCORE"** เฉพาะเมื่อข้อมูลคะแนนนำมาจาก TMDB API/Dataset เท่านั้น (หากนำมาจากแหล่งอื่นให้ใช้คำว่า "User Rating")
* **Chart Styling:**
  * ตัวเลขคะแนนขนาดใหญ่ตรงกลาง (เช่น `7.4` หรือ `8.5`)
  * เส้นวงกลมความก้าวหน้า (Progress Ring) ใช้สี Accent Coral (`#FF6847`) สัดส่วนตามคะแนน (เต็ม 10)

### 7. Similar Movies Analytics (Horizontal Bar Chart)
* **UI Component:** กราฟแท่งแนวนอน (Horizontal Bar Chart) เปรียบเทียบค่าความนิยม (Popularity Comparison) กับภาพยนตร์ที่ใกล้เคียงกัน 4-5 เรื่อง
* **Chart Visual Specs:**
  * แกน Y: ชื่อภาพยนตร์เปรียบเทียบ (เช่น The Lion King, Superman II, The 6th Day)
  * แกน X / ตัวเลขในแท่ง: ค่าความนิยม (Popularity Score)
  * **Bar Color:** ใช้สี Coral/Orange (`#FF6847`) ทั้งหมด
  * Rounding Corners บนแท่งกราฟเพื่อความละมุนสไตล์ Apple

---

# 4. Data Pipeline & Logic Specs for Developer

## 4.1 Data Filtering Rules (การกรองข้อมูลภาพยนตร์คนแสดง)
ก่อนนำ Dataset เข้าสู่ Dashboard Developer ต้องเขียน Script กรองข้อมูล ดังนี้:
1. `genre_ids` / `genres` **MUST NOT CONTAIN** `"Animation"` (ตัดภาพยนตร์อนิเมชันออก)
2. `media_type` **MUST EQUAL** `"movie"` (ตัดซีรีส์และรายการทีวีออก)

## 4.2 Handling Multi-Genre & Multi-Country Data
* **Problem:** ภาพยนตร์ 1 เรื่องอาจมีได้หลาย Genre (เช่น Action, Sci-Fi)
* **Solution:** ในการทำ Filter หรือ Summary Metric ห้ามนำจำนวนนับจาก Pivot Table มาบวกตรงๆ เพราะจะเกิดการนับซ้ำ (Double Counting) ให้ใช้คำสั่ง `COUNT(DISTINCT movie_id)` ในทุก Query การวิเคราะห์เสมอ

---

# 5. Handover Checklist for Antigravity AI Developer

| Component | Status | Dev Instruction |
| :--- | :--- | :--- |
| **Global Theme** | 🟩 Ready | ใช้ CSS Tokens ตามข้อ 2 ตั้งค่า Background Blur และ Tint ตาม Specs |
| **Home Page Layout** | 🟩 Ready | ถอดแบบ Layout จาก Image 2 มี Sidebar, Top Nav, Hero, และ Carousel |
| **Detail Page Layout** | 🟩 Ready | ถอดแบบ Layout จาก Image 1 พร้อม 2x2 KPI Cards และ Financials Card |
| **Financial Metric Logic**| ⚠ Strict Rule | **ห้ามใช้คำว่า Net Profit** ใช้เฉพาะ *"ส่วนต่างรายได้กับงบผลิต"* และ *"Revenue-to-Budget Ratio"* |
| **Null Data Handling** | 🟩 Ready | แสดงข้อความ *"ไม่มีข้อมูล"* หรือ *"N/A"* เมื่อค่าเป็น Null หรือ 0 |
| **Hover Animations** | 🟩 Ready | ใส่ Scale 1.03 - 1.05 ในการ์ด Carousel หน้า Home Page |