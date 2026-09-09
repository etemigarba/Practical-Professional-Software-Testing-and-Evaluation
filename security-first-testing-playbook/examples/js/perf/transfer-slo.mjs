// Slide 40 — performance testing against a service objective, not a feeling.
//
// CORRECTION TO THE SLIDE: as printed, the script declares a `checks` threshold
// but has no `export default function`, so there are no check() calls to produce
// samples. A threshold with no source is a vacuous gate. A real default function
// is supplied here so every declared threshold has something to measure.
//
// Run: k6 run perf/transfer-slo.mjs

import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "2m", target: 200 }, // ramp
    { duration: "5m", target: 200 }, // steady
    { duration: "2m", target: 0 },   // ramp down
  ],
  thresholds: {
    http_req_duration: ["p(95)<250", "p(99)<800"],
    http_req_failed: ["rate<0.001"],
    checks: ["rate>0.99"],
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8080";

export default function () {
  const response = http.post(
    `${BASE_URL}/transfers`,
    JSON.stringify({ to: "0123456789", amount: 5000 }),
    { headers: { "Content-Type": "application/json" } },
  );

  // Every declared threshold now has a source.
  check(response, {
    "status is 201": (r) => r.status === 201,
    "response has a transfer id": (r) => r.json("id") !== undefined,
    "currency is NGN": (r) => r.json("currency") === "NGN",
  });

  sleep(1);
}
