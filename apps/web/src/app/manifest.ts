import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Mezie BrandOS",
    short_name: "BrandOS",
    description: "Builder Intelligence command center for Mr. C. Mezie.",
    id: "/",
    start_url: "/dashboard",
    scope: "/",
    display: "standalone",
    orientation: "any",
    background_color: "#06080c",
    theme_color: "#06080c",
    categories: ["business", "productivity"],
    icons: [
      {
        src: "/icons/brandos-icon.svg",
        sizes: "any",
        type: "image/svg+xml",
        purpose: "any",
      },
      {
        src: "/icons/brandos-icon.svg",
        sizes: "any",
        type: "image/svg+xml",
        purpose: "maskable",
      },
    ],
  };
}
