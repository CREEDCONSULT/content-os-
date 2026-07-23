import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  flushOfflineIdeas,
  listQueuedIdeas,
  OFFLINE_IDEA_QUEUE_KEY,
  queueOfflineIdea,
} from "@/lib/offline-ideas";

const payload = {
  title: "Offline field note",
  raw_input: "A useful observation captured while disconnected.",
  pillar: "Build",
  audience: "Emerging Builder",
  platform_fit: ["LinkedIn"],
};

describe("offline idea queue", () => {
  beforeEach(() => window.localStorage.clear());

  it("persists a queued idea without server state", () => {
    const queued = queueOfflineIdea(payload);

    expect(queued.payload).toEqual(payload);
    expect(listQueuedIdeas()).toHaveLength(1);
    expect(window.localStorage.getItem(OFFLINE_IDEA_QUEUE_KEY)).toContain(
      "Offline field note",
    );
  });

  it("removes only successfully replayed records", async () => {
    queueOfflineIdea(payload);
    queueOfflineIdea({ ...payload, title: "Second note" });
    const send = vi
      .fn()
      .mockResolvedValueOnce({})
      .mockRejectedValueOnce(new Error("still offline"));

    const result = await flushOfflineIdeas(send);

    expect(result).toEqual({ sent: 1, remaining: 1 });
    expect(listQueuedIdeas()[0]?.payload.title).toBe("Second note");
  });
});
