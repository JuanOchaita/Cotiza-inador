export interface ApiUser {
  user_id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface ApiCollectionSummary {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  cards_count: number;
  total_value_usd: number;
}

export interface ApiCardItem {
  card_collection_id: number;
  name: string;
  set_number: string | null;
  set_name: string | null;
  condition: string;
  language: string;
  version: string | null;
  value_usd: number;
  quantity: number;
  image_url: string | null;
}

export interface ApiCollectionDetail {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  cards_count: number;
  total_value_usd: number;
  cards: ApiCardItem[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: ApiUser;
}
