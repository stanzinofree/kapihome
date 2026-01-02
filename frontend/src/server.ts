import Handlebars from "handlebars";

const server = Bun.serve({
  port: 3000,
  async fetch(req) {
    const url = new URL(req.url);
    
    if (url.pathname === "/") {
      const templateFile = await Bun.file("src/templates/index.hbs").text();
      const template = Handlebars.compile(templateFile);
      const html = template({ title: "KapiHome - Zen Capibara" });
      
      return new Response(html, {
        headers: { "Content-Type": "text/html" },
      });
    }
    
    if (url.pathname.startsWith("/static/")) {
      const filePath = url.pathname.replace("/static/", "src/static/");
      const file = Bun.file(filePath);
      return new Response(file);
    }
    
    return new Response("Not Found", { status: 404 });
  },
});

console.log(`Server running at http://localhost:${server.port}`);
