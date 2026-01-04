import Handlebars from "handlebars";

const BACKEND_URL = process.env.BACKEND_URL || "http://kapihome-backend:8000";

// Register partials
const navbarPartial = await Bun.file("src/templates/partials/navbar.hbs").text();
Handlebars.registerPartial("navbar", navbarPartial);

const headPartial = await Bun.file("src/templates/partials/head.hbs").text();
Handlebars.registerPartial("head", headPartial);

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
    
    // Serve LinkedIn page
    if (url.pathname === "/linkedin") {
      const templateFile = await Bun.file("src/templates/linkedin.hbs").text();
      const template = Handlebars.compile(templateFile);
      const html = template({ title: "KapiHome - Zen Capibara" });
      
      return new Response(html, {
        headers: { "Content-Type": "text/html" },
      });
    }
    
    // Serve Exercism page
    if (url.pathname === "/exercism") {
      const templateFile = await Bun.file("src/templates/exercism.hbs").text();
      const template = Handlebars.compile(templateFile);
      const html = template({ title: "KapiHome - Zen Capibara" });
      
      return new Response(html, {
        headers: { "Content-Type": "text/html" },
      });
    }
    
    // Serve GitHub page
    if (url.pathname === "/github") {
      const templateFile = await Bun.file("src/templates/github.hbs").text();
      const template = Handlebars.compile(templateFile);
      const html = template({ title: "KapiHome - Zen Capibara" });
      
      return new Response(html, {
        headers: { "Content-Type": "text/html" },
      });
    }
    
    // Serve RTM page
    if (url.pathname === "/rtm") {
      const templateFile = await Bun.file("src/templates/rtm.hbs").text();
      const template = Handlebars.compile(templateFile);
      const html = template({ title: "KapiHome - Zen Capibara" });
      
      return new Response(html, {
        headers: { "Content-Type": "text/html" },
      });
    }
    
    // Serve Monitoring page
    if (url.pathname === "/monitoring") {
      const templateFile = await Bun.file("src/templates/monitoring.hbs").text();
      const template = Handlebars.compile(templateFile);
      const html = template({ title: "KapiHome - Monitoring" });
      
      return new Response(html, {
        headers: { "Content-Type": "text/html" },
      });
    }
    
    // Serve Welltory page
    if (url.pathname === "/welltory") {
      const templateFile = await Bun.file("src/templates/welltory.hbs").text();
      const template = Handlebars.compile(templateFile);
      const html = template({ title: "KapiHome - Health" });
      
      return new Response(html, {
        headers: { "Content-Type": "text/html" },
      });
    }
    
    // Serve About page
    if (url.pathname === "/about") {
      const templateFile = await Bun.file("src/templates/about.hbs").text();
      const template = Handlebars.compile(templateFile);
      const html = template({ title: "About Me - Alessandro Middei" });
      
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
