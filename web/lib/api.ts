import {
  Challenge,
  Guess,
  GameState,
  GuessSubmission,
  GiveUpSubmission,
  WodHint,
} from "@/types/game";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || `HTTP error! status: ${response.status}`,
        response.status
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(error instanceof Error ? error.message : "Network error occurred");
  }
}

// Path segments come from the URL (the [date] route) and from localStorage, so
// they are encoded rather than interpolated raw: an unencoded "../.." collapsed
// during URL resolution and pointed the request at an arbitrary path on the API
// origin, including from generateMetadata on the server.
const seg = (value: string) => encodeURIComponent(value);

export async function getChallenge(date: string): Promise<Challenge> {
  return fetchApi<Challenge>(`/api/v1/challenges/${seg(date)}`);
}

export async function submitGuess(submission: GuessSubmission): Promise<Guess> {
  return fetchApi<Guess>("/api/v1/game/guess", {
    method: "POST",
    body: JSON.stringify(submission),
  });
}

export async function giveUp(submission: GiveUpSubmission): Promise<Guess> {
  return fetchApi<Guess>("/api/v1/game/giveup", {
    method: "POST",
    body: JSON.stringify(submission),
  });
}

export async function getGameState(date: string, userId: string): Promise<GameState> {
  return fetchApi<GameState>(`/api/v1/game/${seg(date)}/state/${seg(userId)}`);
}

export async function provideWodHint(date: string, userId: string): Promise<WodHint> {
  return fetchApi<WodHint>(`/api/v1/game/${seg(date)}/hints/${seg(userId)}`, {
    method: "POST",
  });
}
