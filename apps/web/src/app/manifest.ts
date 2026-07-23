import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Mezie BrandOS",
    short_name: "BrandOS",
    description: "Builder Intelligence command center for Mr. C. Mezie.",
    start_url: "/dashboard",
    display: "standalone",
    background_color: "#06080c",
    theme_color: "#06080c",
  };
}
