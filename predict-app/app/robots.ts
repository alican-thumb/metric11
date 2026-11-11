import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: [
        "/api/",
        "/profil",
        "/sign-in",
        "/sign-up",
        "/gruplar",
        "/kadro/kur",
        "/kadro/hafta",
        "/kadro/transfer",
        "/kadro/liderlik",
      ],
    },
    sitemap: "https://tahmin.metric11.com/sitemap.xml",
  };
}
