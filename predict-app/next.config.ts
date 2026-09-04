import type { NextConfig } from "next";

// metric11.com/tahmin/* -> bu uygulama (vercel.json rewrite ile, ana site projesinde).
// basePath OLMADAN: Clerk'in (ve Next.js'in kendi) mutlak yönlendirmeleri uygulamanın
// KENDİ algıladığı kökü olan "/"e gidiyor — bu da dıştan bakınca metric11.com/'a
// (asıl kök) düşüyor, /tahmin'i kaybediyor (2026-09-05, canlıda tespit edildi: Clerk
// handshake yönlendirmesi kullanıcıyı /tahmin yerine ana sitenin gündem sayfasına
// atıyordu). basePath ile uygulama HER ZAMAN /tahmin altında yaşadığını biliyor,
// tüm iç yönlendirmeler/varlıklar buna göre otomatik önekleniyor.
const nextConfig: NextConfig = {
  basePath: "/tahmin",
};

export default nextConfig;
