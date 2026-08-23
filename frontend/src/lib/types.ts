export interface Author {
  id: string;
  name: string;
  handle: string;
  avatar?: string;
  badge?: string;
}

export interface PostMetrics {
  likes: number;
  reposts: number;
  replies: number;
}

export interface Post {
  id: string;
  author: Author;
  text: string;
  created_at: string;
  topic_id: string;
  topic_title: string;
  source_type: string;
  perspective?: string;
  tags: string[];
  metrics: PostMetrics;
  safety_risk_level?: "LOW" | "MEDIUM" | "HIGH";
}

export interface Topic {
  id: string;
  title: string;
  description?: string;
  post_count: number;
  participant_count: number;
  tags: string[];
  last_activity?: string;
}

export interface PerspectiveDetail {
  perspective_type: string;
  label: string;
  summary: string;
  post_count: number;
  supporting_post_ids: string[];
  sample_quotes: string[];
}

export interface TimelineItem {
  timestamp: string;
  title: string;
  summary: string;
  related_post_id?: string;
}

export interface SourceContext {
  source_name: string;
  source_type: string;
  mention_count: number;
  reliability_note?: string;
  relevance_score?: number;
  dense_score?: number;
  rank?: number;
}

export interface ContextCard {
  id: string;
  topic_id: string;
  topic_title: string;
  summary: string;
  key_themes: string[];
  perspectives: PerspectiveDetail[];
  timeline: TimelineItem[];
  sources: SourceContext[];
  total_posts: number;
  total_participants: number;
  generated_at: string;
  method: string;
  semantic_cluster_id?: string;
  cluster_confidence?: number;
  pipeline_timing_ms?: {
    clustering_ms?: number;
    dense_retrieval_ms?: number;
    reranking_ms?: number;
    total_pipeline_ms?: number;
  };
  model_used?: string;
}

export interface SafetySignal {
  rule_id: string;
  category: string;
  description: string;
  severity: "info" | "warning" | "critical";
  confidence: number;
  detail?: string;
}

export interface SafetyRiskVector {
  spam_score: number;
  repetition_score: number;
  coordination_score: number;
  toxicity_score: number;
  hate_speech_score: number;
  overall_risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  signals: SafetySignal[];
  is_actionable: boolean;
  human_review_recommended: boolean;
}

export interface SafetyAnalysisResponse {
  text_length: number;
  risk_vector: SafetyRiskVector;
  analyzed_at: string;
}

export interface ScoreFactor {
  factor_name: string;
  label: string;
  weight: number;
  raw_score: number;
  weighted_impact: number;
  is_penalty: boolean;
  explanation: string;
}

export interface RecommendationExplanation {
  post_id: string;
  final_score: number;
  summary_reason: string;
  factors: ScoreFactor[];
}

export interface RecommendedPost {
  post: Post;
  explanation: RecommendationExplanation;
}

export interface SearchResultItem {
  post: Post;
  relevance_score: number;
  rank: number;
  matched_highlights: string[];
}

export interface SearchResponse {
  query: string;
  total_results: number;
  results: SearchResultItem[];
  model_used: string;
  search_latency_ms: number;
}

export interface SystemStatusResponse {
  app_name: string;
  version: string;
  model_manager: {
    status: string;
    semantic_mode: string;
    device: string;
    is_gpu_accelerated: boolean;
    cuda_vram_allocated_gb: number;
    models_loaded: {
      clustering_model: string;
      search_model: string;
      reranker_model: string;
    };
    error_detail?: string | null;
  };
  pipelines: Record<string, string>;
}

export interface SystemHealth {
  status: string;
  app_name: string;
  version: string;
  environment: string;
  data_source_adapter: {
    adapter_type: string;
    status: string;
    cached_posts_count: number;
    cached_topics_count: number;
  };
  ai_pipeline_status: Record<string, string>;
  disclaimer: string;
}
