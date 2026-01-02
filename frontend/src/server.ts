import Handlebars from "handlebars";

const BACKEND_URL = process.env.BACKEND_URL || "http://kapihome-backend:8000";

const server = Bun.serve({
  port: 3000,
  async fetch(req) {
    const url = new URL(req.url);
    
    // Proxy API requests to backend
    if (url.pathname.startsWith("/api/")) {
      try {
        const backendUrl = `${BACKEND_URL}${url.pathname}${url.search}`;
        const response = await fetch(backendUrl, {
          method: req.method,
          headers: req.headers,
          body: req.body,
        });
        
        return new Response(response.body, {
          status: response.status,
          headers: response.headers,
        });
      } catch (error) {
        console.error("Backend proxy error:", error);
        return new Response("Backend unavailable", { status: 503 });
      }
    }
    
    // Serve homepage
    if (url.pathname === "/") {
      const templateFile = await Bun.file("src/templates/index.hbs").text();
      const template = Handlebars.compile(templateFile);
      const html = template({ title: "KapiHome - Zen Capibara" });
      
      return new Response(html, {
        headers: { "Content-Type": "text/html" },
      });
    }
    
    // Serve static files
    if (url.pathname.startsWith("/static/")) {
      const filePath = url.pathname.replace("/static/", "src/static/");
      const file = Bun.file(filePath);
      return new Response(file);
    }
    
    return new Response("Not Found", { status: 404 });
  },
});

console.log(`Frontend server running at http://localhost:${server.port}`);
console.log(`Backend proxy target -> ${BACKEND_URL}`);
