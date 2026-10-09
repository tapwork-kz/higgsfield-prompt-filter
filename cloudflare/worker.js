/**
 * Cloudflare Worker: Higgsfield AI Prompt Filter Edge Server.
 * Supports:
 * 1. Direct REST API (/api/filter)
 * 2. Telegram Webhook handler (/webhook)
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Health check
    if (url.pathname === "/" || url.pathname === "/health") {
      return new Response(JSON.stringify({ status: "ok", service: "Higgsfield Prompt Filter Edge" }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    // Direct REST API for external generators
    if (url.pathname === "/api/filter" && request.method === "POST") {
      try {
        const body = await request.json();
        const text = body.text || "";
        const model = body.model || env.DEFAULT_MODEL || "Kling";
        const mode = body.mode || env.DEFAULT_MODE || "PRO";

        const result = transformPrompt(text, model, mode);
        return new Response(JSON.stringify(result), {
          headers: { "Content-Type": "application/json" },
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
          status: 400,
          headers: { "Content-Type": "application/json" },
        });
      }
    }

    // Telegram Webhook Handler
    if (url.pathname === "/webhook" && request.method === "POST") {
      try {
        const update = await request.json();
        if (update.message && update.message.text) {
          const chatId = update.message.chat.id;
          const userText = update.message.text;

          if (userText === "/start") {
            await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, chatId, 
              "👋 <b>Higgsfield Prompt Filter (Cloudflare Edge)</b> активен!\nОтправьте описание сцены для генерации."
            );
          } else {
            const transformed = transformPrompt(userText, "Kling", "PRO");
            const responseText = 
              `PROMPT:\n<code>${escapeHtml(transformed.prompt)}</code>\n\n` +
              `NEGATIVE / CONSTRAINTS:\n<code>${escapeHtml(transformed.negative_constraints)}</code>\n\n` +
              `SETTINGS:\nModel: ${transformed.settings.Model}\nAspect Ratio: ${transformed.settings["Aspect Ratio"]}\nDuration: ${transformed.settings.Duration}`;

            await sendTelegramMessage(env.TELEGRAM_BOT_TOKEN, chatId, responseText);
          }
        }
        return new Response("OK", { status: 200 });
      } catch (err) {
        return new Response("Webhook Error: " + err.message, { status: 500 });
      }
    }

    return new Response("Not Found", { status: 404 });
  },
};

/**
 * Lightweight prompt transformation engine for Cloudflare Edge runtime
 */
function transformPrompt(text, model, mode) {
  const lower = text.toLowerCase();
  
  // Constraints
  const constraints = [];
  const negatives = [
    "deformed anatomy", "teleporting objects", "glitchy motion", 
    "erratic camera shake", "warped geometry", "low resolution blur", "watermark"
  ];

  if (lower.includes("не менять лицо") || lower.includes("keep face")) {
    constraints.push("PRESERVE IDENTITY / DO NOT ALTER FACIAL FEATURES");
    negatives.push("altered facial proportions", "changed facial identity");
  }

  let subject = "subject";
  if (lower.includes("bmw")) {
    subject = "BMW E39";
    constraints.push("PRESERVE VEHICLE MODEL AND BODY DESIGN (BMW E39)");
  }

  let location = "metropolitan urban street";
  if (lower.includes("алматы") || lower.includes("almaty")) {
    location = "Almaty city street with modern urban architecture";
  }

  let camera = "35mm anamorphic cinema lens, low-angle tracking shot at smooth pace";
  if (lower.includes("сзади") || lower.includes("rear")) {
    camera = "35mm prime lens, low rear three-quarter angle tracking";
  }

  let lighting = "atmospheric street lighting, wet asphalt reflections, and vehicular headlamps";
  if (lower.includes("ночь") || lower.includes("night")) {
    lighting = "nocturnal ambient street lighting with sharp specular reflections and high contrast";
  }

  let action = "cruising smoothly along the illuminated asphalt with realistic tire grip";

  let prompt = "";
  const preserveStr = constraints.length ? `[CONSTRAINTS: ${constraints.join(" | ")}] ` : "";

  if (model.toLowerCase() === "veo") {
    prompt = `${preserveStr}Cinematic 24fps shot of ${subject} ${action}. Camera: ${camera}. Environment: ${location}. Lighting: ${lighting}. 4K film stock, sharp focus.`;
  } else if (model.toLowerCase() === "runway") {
    prompt = `${preserveStr}[Camera Movement]: ${camera}. [Subject Action]: ${subject} ${action}. [Environment]: ${location}. [Lighting]: ${lighting}.`;
  } else if (model.toLowerCase() === "flux") {
    prompt = `${preserveStr}A candid, authentic photograph of ${subject} ${action}. Captured with ${camera}. Setting is ${location} under ${lighting}. Natural film grain.`;
  } else {
    // Kling default
    prompt = `${preserveStr}SUBJECT: ${subject} | ACTION: ${action} | CAMERA: ${camera} | ENVIRONMENT: ${location} | LIGHTING: ${lighting} | TEMPORAL CONSISTENCY: maintain consistent geometry and reflections throughout the clip`;
  }

  return {
    prompt,
    negative_constraints: negatives.join(", "),
    settings: {
      Model: model,
      "Aspect Ratio": "16:9",
      Duration: "5s",
      Mode: mode,
    },
    constraints,
  };
}

async function sendTelegramMessage(token, chatId, text) {
  if (!token) return;
  await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text: text,
      parse_mode: "HTML",
    }),
  });
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
