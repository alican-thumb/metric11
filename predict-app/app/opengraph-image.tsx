import { ImageResponse } from "next/og";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          background: "#091810",
          fontFamily: "Arial,sans-serif",
        }}
      >
        <div style={{ display: "flex", width: "100%", height: 4, background: "#cde94e" }} />
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            flex: 1,
            justifyContent: "center",
            padding: "0 80px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", marginBottom: 40 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: 64,
                height: 64,
                borderRadius: 14,
                background: "#cde94e",
                color: "#091810",
                fontSize: 30,
                fontWeight: 800,
                marginRight: 24,
              }}
            >
              11
            </div>
            <div style={{ display: "flex", color: "#8fa89a", fontSize: 32, fontWeight: 600 }}>
              metric11 Tahmin
            </div>
          </div>
          <div style={{ display: "flex", color: "#ffffff", fontSize: 64, fontWeight: 800, lineHeight: 1.1 }}>
            Süper Lig Tahmin Oyunu
          </div>
          <div style={{ display: "flex", color: "#8fa89a", fontSize: 30, marginTop: 24 }}>
            Maç tahminlerini gir, puan topla, liderlik tablosunda yarış.
          </div>
        </div>
      </div>
    ),
    size,
  );
}
