// Slide 22 — end-to-end testing: few, critical, ruthlessly maintained.
//
// Role and label selectors with web-first assertions. No fixed waits, no CSS
// class selectors: those two are the largest sources of flakiness, and slide 23
// costs flakiness at roughly 6-8 engineer-hours per week.
//
// Opt-in and illustrative. It is not part of the Python verification gate.

import { test, expect } from "@playwright/test";

test.describe("critical journey: customer transfer", () => {
  test.beforeEach(async ({ page }) => {
    // Each test creates its own data through the API, then exercises one path.
    // Shared fixtures make failures unattributable (slide 22).
    await page.request.post("/test-support/accounts", {
      data: { balance: 500000, dailyLimit: 200000, tenant: "tenant-a" },
    });
  });

  test("customer completes a transfer", async ({ page }) => {
    await page.goto("/transfer");
    await page.getByLabel("Recipient account").fill("0123456789");
    await page.getByLabel("Amount").fill("50000");
    await page.getByRole("button", { name: "Send" }).click();

    // Auto-waits and retries; no arbitrary timeout.
    await expect(page.getByRole("status")).toHaveText("Transfer of ₦50,000 sent");
    await expect(page.getByTestId("balance")).toHaveText("₦450,000");
  });

  test("customer is stopped at the daily limit", async ({ page }) => {
    await page.goto("/transfer");
    await page.getByLabel("Recipient account").fill("0123456789");
    await page.getByLabel("Amount").fill("200001");
    await page.getByRole("button", { name: "Send" }).click();

    await expect(page.getByRole("alert")).toContainText("daily limit");
    // The operation is atomic: nothing moved.
    await expect(page.getByTestId("balance")).toHaveText("₦500,000");
  });
});
