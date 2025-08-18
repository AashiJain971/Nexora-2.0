import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// Test both APIs
async function testBackendConnections() {
  // Test Invoice API (GET /)
  try {
    const invoiceRes = await fetch("http://localhost:8001/");
    const invoiceData = await invoiceRes.json();
    console.log("✅ Invoice API connection OK:", invoiceData);
  } catch (err) {
    console.error("❌ Invoice API connection failed:", err);
  }

  // Test Credit Score API (POST /calculate-credit-score)
  try {
    const creditRes = await fetch("http://localhost:8001/calculate-credit-score", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        no_of_invoices: 10,
        total_amount: 10000,
        total_amount_pending: 3000,
        total_amount_paid: 7000,
        tax: 1000,
        extra_charges: 200,
        payment_completion_rate: 0.7,
        paid_to_pending_ratio: 2.33,
      }),
    });

    if (!creditRes.ok) {
      throw new Error(`HTTP ${creditRes.status} - ${creditRes.statusText}`);
    }

    const creditData = await creditRes.json();
    console.log("✅ Credit Score API POST OK:", creditData);
  } catch (err) {
    console.error("❌ Credit Score API POST failed:", err);
  }
}

testBackendConnections();

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
