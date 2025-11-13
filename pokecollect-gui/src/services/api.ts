const API_BASE_URL = "http://localhost:8000";

// ============= TYPE DEFINITIONS =============

export interface User {
  user_id: number;
  email: string;
}

export interface Collection {
  collection_id: number;
  user_id: number;
  title: string;
  collection_price_usd: number;
  exchange_rate: number;
  created_at: string;
}

export interface Card {
  card_id: number;
  name: string;
  condition: string;
  quantity: number;
  language: string;
  version: string;
  set_name: string;
  set_number: string;
  date: string;
  image: string;
}

export interface CreateUserRequest {
  email: string;
  password: string;
}

export interface CreateCollectionRequest {
  title: string;
  user_id: number;
}

export interface AddCardRequest {
  collection_id: number;
  condition_id: number;
  quantity: number;
  card_name: string;
  number_in_set: string;
  set_name: string;
  language_id: number;
  edition: string;
}

export interface UpdateExchangeRateRequest {
  new_exchange_rate: number;
}

// ============= API FUNCTIONS =============

// USER AUTHENTICATION

export const createUser = async (data: CreateUserRequest): Promise<User> => {
  const response = await fetch(`${API_BASE_URL}/users/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create user");
  }
  
  return response.json();
};

export const getUser = async (email: string, password: string): Promise<User> => {
  const response = await fetch(`${API_BASE_URL}/users/${email}?password=${encodeURIComponent(password)}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Invalid credentials");
  }
  
  return response.json();
};

export const deleteUser = async (userId: number): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
    method: "DELETE",
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to delete user");
  }
};

// COLLECTIONS

export const getCollectionsByUser = async (userId: number): Promise<Collection[]> => {
  const response = await fetch(`${API_BASE_URL}/collections/user/${userId}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch collections");
  }
  
  return response.json();
};

export const createCollection = async (data: CreateCollectionRequest): Promise<Collection> => {
  const response = await fetch(`${API_BASE_URL}/collections/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create collection");
  }
  
  return response.json();
};

export const getCollection = async (collectionId: number): Promise<Collection> => {
  const response = await fetch(`${API_BASE_URL}/collections/${collectionId}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch collection");
  }
  
  return response.json();
};

export const updateCollectionExchangeRate = async (
  collectionId: number,
  data: UpdateExchangeRateRequest
): Promise<Collection> => {
  const response = await fetch(`${API_BASE_URL}/collections/${collectionId}/exchange_rate`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to update exchange rate");
  }
  
  return response.json();
};

// CARDS IN COLLECTION

export const getCardsByCollection = async (collectionId: number): Promise<Card[]> => {
  const response = await fetch(`${API_BASE_URL}/cards_in_collection/details/${collectionId}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch cards");
  }
  
  return response.json();
};

export const addCardToCollection = async (data: AddCardRequest): Promise<Card> => {
  const response = await fetch(`${API_BASE_URL}/cards_in_collection/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to add card");
  }
  
  return response.json();
};

export const removeCardFromCollection = async (
  cardId: number,
  collectionId: number
): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/cards_in_collection/`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ card_id: cardId, collection_id: collectionId }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to remove card");
  }
};
