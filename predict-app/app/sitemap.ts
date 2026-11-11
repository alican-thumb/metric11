import type { MetadataRoute } from "next";

const BASE_URL = "https://tahmin.metric11.com";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();
  return [
    { url: BASE_URL, lastModified: now, changeFrequency: "daily", priority: 1 },
    { url: `${BASE_URL}/kadro`, lastModified: now, changeFrequency: "daily", priority: 1 },
    { url: `${BASE_URL}/topluluk`, lastModified: now, changeFrequency: "daily", priority: 0.8 },
    { url: `${BASE_URL}/leaderboard`, lastModified: now, changeFrequency: "daily", priority: 0.8 },
    { url: `${BASE_URL}/taraftar`, lastModified: now, changeFrequency: "daily", priority: 0.8 },
  ];
}
