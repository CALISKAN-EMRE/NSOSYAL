import {
  ContextCard,
  Post,
  RecommendedPost,
  SafetyAnalysisResponse,
  SystemHealth,
  Topic,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      cache: "no-store",
    });

    if (!res.ok) {
      const errorBody = await res.text();
      throw new Error(`API error (${res.status}): ${errorBody || res.statusText}`);
    }

    return (await res.json()) as T;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Fetch failed for ${url}:`, message);
    throw new Error(message);
  }
}

export const api = {
  getHealth: () => fetchJson<SystemHealth>("/health"),

  getPosts: (params?: { topic_id?: string; search?: string; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.topic_id) searchParams.append("topic_id", params.topic_id);
    if (params?.search) searchParams.append("search", params.search);
    if (params?.limit) searchParams.append("limit", params.limit.toString());
    const query = searchParams.toString();
    return fetchJson<Post[]>(`/api/posts${query ? `?${query}` : ""}`);
  },

  getTopics: () => fetchJson<Topic[]>("/api/topics"),

  getContextCard: (topicId: string) => fetchJson<ContextCard>(`/api/context/${topicId}`),

  getRecommendations: (params?: { preferred_topic?: string; interests?: string; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.preferred_topic) searchParams.append("preferred_topic", params.preferred_topic);
    if (params?.interests) searchParams.append("interests", params.interests);
    if (params?.limit) searchParams.append("limit", params.limit.toString());
    const query = searchParams.toString();
    return fetchJson<RecommendedPost[]>(`/api/recommendations${query ? `?${query}` : ""}`);
  },

  analyzeSafety: (text: string, postId?: string, authorId?: string) =>
    fetchJson<SafetyAnalysisResponse>("/api/safety/analyze", {
      method: "POST",
      body: JSON.stringify({
        text,
        post_id: postId,
        author_id: authorId,
      }),
    }),
};
