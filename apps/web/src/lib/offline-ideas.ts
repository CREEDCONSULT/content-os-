export const OFFLINE_IDEA_QUEUE_KEY = "mezie-brandos:offline-idea-queue:v1";
export const OFFLINE_IDEA_QUEUE_EVENT = "brandos:offline-idea-queue-changed";

export type CreateIdeaPayload = {
  title: string;
  raw_input: string;
  pillar?: string;
  audience: string;
  platform_fit: string[];
};

export type QueuedIdea = {
  id: string;
  queued_at: string;
  payload: CreateIdeaPayload;
};

function storageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function notifyQueueChanged(): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent(OFFLINE_IDEA_QUEUE_EVENT));
  }
}

export function listQueuedIdeas(): QueuedIdea[] {
  if (!storageAvailable()) return [];
  const raw = window.localStorage.getItem(OFFLINE_IDEA_QUEUE_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(
      (item): item is QueuedIdea =>
        typeof item === "object" &&
        item !== null &&
        typeof (item as QueuedIdea).id === "string" &&
        typeof (item as QueuedIdea).queued_at === "string" &&
        typeof (item as QueuedIdea).payload?.title === "string",
    );
  } catch {
    return [];
  }
}

function saveQueue(items: QueuedIdea[]): void {
  if (!storageAvailable()) {
    throw new Error("Offline storage is unavailable in this browser.");
  }
  window.localStorage.setItem(OFFLINE_IDEA_QUEUE_KEY, JSON.stringify(items));
  notifyQueueChanged();
}

export function queueOfflineIdea(payload: CreateIdeaPayload): QueuedIdea {
  const queued: QueuedIdea = {
    id: globalThis.crypto?.randomUUID?.() ?? `offline-${Date.now()}`,
    queued_at: new Date().toISOString(),
    payload,
  };
  saveQueue([...listQueuedIdeas(), queued]);
  return queued;
}

export async function flushOfflineIdeas(
  send: (payload: CreateIdeaPayload) => Promise<unknown>,
): Promise<{ sent: number; remaining: number }> {
  const queue = listQueuedIdeas();
  let sent = 0;
  const remaining: QueuedIdea[] = [];

  for (const item of queue) {
    try {
      await send(item.payload);
      sent += 1;
    } catch {
      remaining.push(item);
    }
  }

  if (queue.length > 0) saveQueue(remaining);
  return { sent, remaining: remaining.length };
}
