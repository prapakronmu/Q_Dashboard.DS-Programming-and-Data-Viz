# UI/UX Style Requirements

**Concept:** Apple Vision Pro + Premium Streaming
**Reference Mapping:**
- `Image 2` = Home Page Layout
- `Image 1` = Detail Page Layout

---

## 1. Design System & Global Styles

*   **Overall Vibe:** ล้ำสมัย, หรูหรา, โปร่งแสง (Spatial UI) คล้ายคลึงกับระบบปฏิบัติการ visionOS
*   **Background:** 
    *   ใช้รูปภาพ Cinematic ของภาพยนตร์เรื่องนั้นๆ
    *   ใช้เอฟเฟกต์ **Gaussian Blur** อย่างหนัก (Blur-3xl) เพื่อให้กลายเป็นพื้นหลังแบบ Abstract
    *   ซ้อนทับด้วย **Dark Gray Overlay** (`rgba(15, 15, 17, 0.6)` ถึง `0.8`) เพื่อดรอปความสว่างและขับให้ UI โดดเด่นขึ้น
*   **Typography:**
    *   **Font Family:** Sans-serif ที่ดูพรีเมียม (เช่น `Inter`, `SF Pro Display`, `Roboto`)
    *   **Text Colors:** ขาว (White) เป็นหลักสำหรับตัวเลข/ข้อมูลสำคัญ และ เทาอ่อน (Light Gray) สำหรับ Label/หัวข้อ
*   **Accent Color (สีเน้น):** 
    *   **Coral / Orange (`#FF6847`)** 
    *   ใช้สำหรับกราฟ (Bar Chart, Radial Chart), ปุ่ม Active, และจุดดึงดูดสายตา

## 2. Component Styling (Glassmorphism)

องค์ประกอบ UI ทั้งหมด (Panels, Cards, Sidebars) ต้องใช้เทคนิค Frosted Glass:

*   **Background:** สีเทาเข้มกึ่งโปร่งแสง (เช่น `rgba(30, 30, 35, 0.45)`)
*   **Blur Effect:** ใส่ Backdrop-filter blur ประมาณ 20px ขึ้นไป
*   **Border:** เส้นขอบบางมากๆ (1px) แบบโปร่งแสง (`rgba(255, 255, 255, 0.08)`) เพื่อสร้างมิติตัดกับฉากหลัง
*   **Border Radius:** ขอบโค้งมนมากเป็นพิเศษ **18px ถึง 24px** (อิงตามสไตล์ Apple)
*   **Shadow:** เงามืดแบบนุ่มนวลเพื่อยกระดับ Card ให้ดูลอยขึ้น

---

## 3. Tailwind CSS Configuration & Tokens

นำ Config นี้ไปใช้ใน `tailwind.config.js` สำหรับฝั่ง Frontend Developer:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        // Base backgrounds
        visionDark: 'rgba(15, 15, 17, 0.7)', // Overlay
        
        // Glass Panels
        glassPanel: 'rgba(30, 30, 35, 0.45)',
        glassBorder: 'rgba(255, 255, 255, 0.08)',
        
        // Typography
        textPrimary: '#ffffff',
        textSecondary: '#a0a0a5',
        
        // Branding / Accent
        brandAccent: '#FF6847', // Coral/Orange from graphs
      },
      fontFamily: {
        sans: ['"Inter"', '"SF Pro Display"', 'sans-serif'],
      },
      borderRadius: {
        'vision': '20px', // 18-24px range
      },
      backdropBlur: {
        'glass': '24px',
        'bgCinematic': '64px',
      }
    }
  }
}
```

## 4. Layout Structure (โครงสร้างหน้าจอ)

### 4.1 Home Page (อิง Image 2)
*   แบ่ง Layout เป็น 3 ส่วนหลัก:
    *   **Left Sidebar (5%):** เล็ก เรียว จัดชิดซ้ายสุด
    *   **Left Column (25%):** สำหรับ Scroll เนื้อหาแนวตั้ง (New Trailers, Continue Watching)
    *   **Right Main Column (70%):** พื้นที่หลักสำหรับ Hero Banner ขอบมนขนาดใหญ่ และ Carousel "You might like" แนวนอนด้านล่าง

### 4.2 Detail Page (อิง Image 1)
*   แบ่ง Layout เป็น Grid System อย่างชัดเจน:
    *   **Column 1 (ซ้ายสุด - 30%):** โปสเตอร์แนวตั้ง (ไม่จำเป็นต้องขอบมนมากเพื่อให้ดูเป็นรูปภาพ) วางทับด้วย Dropdown แบบ Glassmorphism ด้านบน และด้านล่างเป็น 2x2 Grid สำหรับ KPI Cards 4 ใบ
    *   **Column 2 (ขวา - 70%):**
        *   **Top:** แถบรายชื่อนักแสดง เรียงรูปโปรไฟล์แนวนอน
        *   **Middle:** แบ่งเป็นกรอบ Overview ซ้ายกว้างๆ และ Financials ขวาแคบกว่า
        *   **Bottom:** แบ่งเป็นกราฟแท่ง (Similar Movies) และ กราฟวงแหวน (TMDB Score)

*   **Micro-interactions:** 
    *   Hover ที่การ์ดนักแสดง หรือ Carousel ให้ใช้ CSS `hover:scale-105` พร้อม `transition-all duration-300`