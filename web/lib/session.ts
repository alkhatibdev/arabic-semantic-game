"use client";

import { v4 as uuidv4 } from "uuid";

const USER_ID_KEY = "arabic_semantic_game_user_id";

export function getUserId(): string {
  if (typeof window === "undefined") {
    return "";
  }

  let userId = localStorage.getItem(USER_ID_KEY);

  if (!userId) {
    userId = uuidv4();
    localStorage.setItem(USER_ID_KEY, userId);
  }

  return userId;
}
