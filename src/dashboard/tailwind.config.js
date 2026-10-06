/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Base backgrounds
        visionDark: 'rgba(15, 15, 17, 0.7)', 
        
        // Glass Panels
        glassPanel: 'rgba(30, 30, 35, 0.45)',
        glassBorder: 'rgba(255, 255, 255, 0.08)',
        
        // Typography
        textPrimary: '#ffffff',
        textSecondary: '#a0a0a5',
        
        // Branding / Accent
        brandAccent: '#FF6847', // Coral/Orange
      },
      borderRadius: {
        'vision': '20px', // 18-24px range
      },
      backdropBlur: {
        'glass': '24px',
        'bgCinematic': '64px',
      }
    },
  },
  plugins: [],
}
