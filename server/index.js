// ── Vizolane Contact Form Backend ─────────────────────────
// Express server that handles contact form submissions:
//   1. Validates input
//   2. Stores in Google Sheets
//   3. Sends emails to admin + user

require("dotenv").config();

const express = require("express");
const cors = require("cors");
const rateLimit = require("express-rate-limit");
const path = require("path");

const { sendAdminNotification, sendUserConfirmation, verifyConnection } = require("./services/emailService");
const { initSheets, appendContactToSheet } = require("./services/sheetsService");

const app = express();
const PORT = process.env.PORT || 3000;

// ── Middleware ────────────────────────────────────────────

// Parse JSON bodies
app.use(express.json());

// Parse URL-encoded bodies (form fallback)
app.use(express.urlencoded({ extended: true }));

// Serve frontend statically for testing
app.use(express.static(path.join(__dirname, "..")));

// CORS — allow frontend origins
const allowedOrigins = (process.env.FRONTEND_URL || "http://localhost:5500")
  .split(",")
  .map((url) => url.trim());

app.use(
  cors({
    origin: (origin, callback) => {
      // Allow requests with no origin (mobile apps, Postman, etc.)
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        console.warn(`⛔ Blocked by CORS: ${origin}`);
        callback(new Error("Not allowed by CORS"));
      }
    },
    methods: ["POST", "OPTIONS"],
    allowedHeaders: ["Content-Type"],
  })
);

// Rate limiting — max 5 submissions per IP per 15 minutes
const contactLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    success: false,
    error: "Too many requests. Please try again after 15 minutes.",
  },
});

// ── Health check ─────────────────────────────────────────

app.get("/api/health", (_req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

// ── POST /api/contact ────────────────────────────────────

app.post("/api/contact", contactLimiter, async (req, res) => {
  try {
    const { name, email, phone, message } = req.body;

    // ── Validation ────────────────────────────────
    const errors = [];
    if (!name || typeof name !== "string" || name.trim().length < 2) {
      errors.push("Name is required (at least 2 characters).");
    }
    if (!email || typeof email !== "string" || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      errors.push("A valid email address is required.");
    }
    if (!message || typeof message !== "string" || message.trim().length < 5) {
      errors.push("Message is required (at least 5 characters).");
    }

    if (errors.length > 0) {
      return res.status(400).json({ success: false, errors });
    }

    // Sanitize
    const contactData = {
      name: name.trim(),
      email: email.trim().toLowerCase(),
      phone: phone ? phone.trim() : "",
      message: message.trim(),
    };

    console.log(`\n📨 New contact from: ${contactData.name} <${contactData.email}>`);

    // ── Execute in parallel: Sheets + Emails ──────
    const results = await Promise.allSettled([
      appendContactToSheet(contactData),
      sendAdminNotification(contactData),
      sendUserConfirmation(contactData),
    ]);

    // Log results
    const labels = ["Google Sheets", "Admin Email", "User Email"];
    results.forEach((result, i) => {
      if (result.status === "fulfilled") {
        console.log(`   ✅ ${labels[i]}: success`);
      } else {
        console.error(`   ❌ ${labels[i]}: ${result.reason?.message || "failed"}`);
      }
    });

    // Check if at least one critical operation succeeded
    const emailsSent = results[1].status === "fulfilled" || results[2].status === "fulfilled";
    const sheetWritten = results[0].status === "fulfilled";

    if (!emailsSent && !sheetWritten) {
      return res.status(500).json({
        success: false,
        error: "Failed to process your submission. Please try again or email us directly at admin@vizolane.com.",
      });
    }

    res.json({
      success: true,
      message: "Thank you! Your message has been received. We'll get back to you soon.",
    });
  } catch (err) {
    console.error("❌ Unexpected error in /api/contact:", err);
    res.status(500).json({
      success: false,
      error: "Something went wrong. Please try again or email us at admin@vizolane.com.",
    });
  }
});

// ── 404 handler ──────────────────────────────────────────

app.use((_req, res) => {
  res.status(404).json({ error: "Route not found" });
});

// ── Start server (Local Dev) ───────────────────────────────

async function start() {
  console.log("\n🚀 Starting Vizolane Contact Backend...\n");

  // Initialize services (non-blocking — server starts even if they fail)
  await Promise.allSettled([verifyConnection(), initSheets()]);

  app.listen(PORT, () => {
    console.log(`\n✅ Server running on http://localhost:${PORT}`);
    console.log(`   POST /api/contact  — handle contact form`);
    console.log(`   GET  /api/health   — health check\n`);
  });
}

// Start only if run directly (not imported by Vercel)
if (require.main === module) {
  start();
}

// Export for Vercel Serverless
module.exports = app;
