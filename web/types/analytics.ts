export type GtagParams = Record<string, unknown>;

declare global {
  interface Window {
    gtag: (command: string, targetId: string, config?: GtagParams) => void;
    dataLayer: unknown[];
  }
}

export {};
