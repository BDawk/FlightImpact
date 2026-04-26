// Build-time flag set in vite.config.ts
declare const __BUILD_TARGET__: string;

export const BUILD_TARGET = (__BUILD_TARGET__ ?? "devkit") as "devkit" | "production";
export const IS_DEVKIT = BUILD_TARGET === "devkit";
