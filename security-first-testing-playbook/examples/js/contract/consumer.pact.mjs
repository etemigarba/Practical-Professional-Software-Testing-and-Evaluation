// Slide 21 — consumer-driven contract testing, Pact JS v3 (PactV3 + MatchersV3).
//
// CORRECTIONS TO THE SLIDE (see docs/slide-to-code-map.md):
//
//  1. The slide uses `term({ matcher, generate })`. That is the Pact JS **v2**
//     matcher DSL. v3 uses `MatchersV3.regex(matcher, generate)`; mixing the two
//     throws at runtime.
//  2. The slide's builder chain has no terminator. `PactV3` only writes a pact
//     file when `.executeTest()` runs, so as printed no pact is ever produced.
//
// This file is illustrative and opt-in. The Python suite in
// tests/contract/ verifies the same interactions in-process, so the default
// verification gate needs neither Node nor a Pact broker.

import { PactV3, MatchersV3 } from "@pact-foundation/pact";
import { describe, it, expect } from "vitest";

const { uuid, integer, regex, like } = MatchersV3;

const provider = new PactV3({
  consumer: "invoice-consumer",
  provider: "invoice-provider",
  dir: "./pacts",
});

describe("invoice consumer", () => {
  it("depends on the fields it actually reads", async () => {
    await provider
      .given("invoice 7c2 exists for tenant-a")
      .uponReceiving("a request for that invoice")
      .withRequest({
        method: "GET",
        path: "/invoices/7c2",
        headers: { Authorization: like("Bearer eyJhbGciOi...") },
      })
      .willRespondWith({
        status: 200,
        body: {
          id: uuid(),
          total: integer(45000),
          currency: regex("NGN|USD", "NGN"),
          status: regex("AWAITING_APPROVAL|PAID|DRAFT", "AWAITING_APPROVAL"),
        },
      })
      // Correction 2: without executeTest, no pact is written.
      .executeTest(async (mockServer) => {
        const response = await fetch(`${mockServer.url}/invoices/7c2`, {
          headers: { Authorization: "Bearer test-token" },
        });
        const body = await response.json();

        expect(response.status).toBe(200);
        expect(body.currency).toBe("NGN");
        expect(body.total).toBe(45000);
      });
  });

  it("depends on a cross-tenant request being indistinguishable from a miss", async () => {
    await provider
      .given("invoice 7c2 exists for tenant-a")
      .uponReceiving("a request from another tenant")
      .withRequest({
        method: "GET",
        path: "/invoices/7c2",
        headers: { Authorization: like("Bearer other-tenant-token") },
      })
      // 404, never 403 with a body: a 403 confirms the resource exists.
      .willRespondWith({ status: 404 })
      .executeTest(async (mockServer) => {
        const response = await fetch(`${mockServer.url}/invoices/7c2`, {
          headers: { Authorization: "Bearer other-tenant-token" },
        });

        expect(response.status).toBe(404);
      });
  });
});
