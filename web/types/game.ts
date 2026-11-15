export interface Challenge {
  date: string;
  game_number: number;
  has_challenge: boolean;
  word?: string;
}

export interface Guess {
  id: number;
  word: string;
  similarity_score: number;
  cosine_similarity: number;
  is_correct: boolean;
  created_at: string;
  attempt_number?: number;
  /** True when this row is the revealed answer from giving up, not a real guess. */
  is_given_up?: boolean;
}

export interface GameStatus {
  won: boolean;
  attempts: number;
  won_at?: string;
  target_word?: string;
}

export interface GameState {
  challenge_date: string;
  game_number: number;
  guesses: Guess[];
  game_status?: GameStatus;
  has_won: boolean;
  hints: WodHint[];
  /** Hint allowance for this player, served by the API rather than hardcoded. */
  max_hints: number;
}

export interface GuessSubmission {
  user_id: string;
  challenge_date: string;
  word: string;
}

export interface GiveUpSubmission {
  user_id: string;
  challenge_date: string;
}

export interface WodHint {
  hint_text: string;
  hint_order: number;
}
