import { Clapperboard } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex h-full min-h-[80vh] items-center justify-center">
      {/* ตัวอย่างการใช้ Glass Panel Component */}
      <div className="glass-panel p-12 text-center max-w-xl w-full flex flex-col items-center gap-6">
        <div className="p-4 rounded-full bg-white/10 text-brandAccent">
          <Clapperboard size={48} strokeWidth={1.5} />
        </div>
        
        <div>
          <h1 className="text-3xl font-bold mb-2 tracking-tight">Movie Analytics</h1>
          <p className="text-textSecondary leading-relaxed">
            Premium Live-action Dashboard
            <br />Apple Vision Pro Aesthetic Initialized.
          </p>
        </div>

        {/* ตัวอย่างการใช้ Accent Color และ Hover Animation เบื้องต้น */}
        <button className="mt-4 px-8 py-3 bg-brandAccent text-white font-semibold rounded-full hover:scale-105 transition-transform duration-300 shadow-lg shadow-brandAccent/20">
          Enter Dashboard
        </button>
      </div>
    </div>
  );
}
