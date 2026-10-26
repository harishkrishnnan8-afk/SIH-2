export const pageHead = (title: string, description: string) => () => ({
  meta: [
    { title: `${title} · APAAR Student Data Platform` },
    { name: "description", content: description },
    { property: "og:title", content: `${title} · APAAR Student Data Platform` },
    { property: "og:description", content: description },
    { property: "og:type", content: "website" },
    { name: "twitter:card", content: "summary" },
  ],
});
