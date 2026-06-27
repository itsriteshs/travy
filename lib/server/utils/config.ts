import fs from "node:fs";
import path from "node:path";

type RuntimeConfig = {
  budget: {
    defaultTotalUsd: number;
    modeThresholds: {
      healthy: number;
      cautious: number;
      low: number;
      critical: number;
    };
  };
  security: {
    riskThreshold: number;
    weights: {
      roleEscalation: number;
      instructionOverride: number;
      promptExtraction: number;
      jailbreakPattern: number;
    };
  };
  retry: {
    otariMaxAttempts: number;
    otariTimeoutMs: number;
  };
};

type ModelPricing = {
  [model: string]: {
    input_token_price: number;
    output_token_price: number;
  };
};

const configCache: Record<string, unknown> = {};

function loadJsonFile<T>(relativePath: string): T {
  if (configCache[relativePath]) {
    return configCache[relativePath] as T;
  }
  const fullPath = path.join(process.cwd(), relativePath);
  const raw = fs.readFileSync(fullPath, "utf8");
  const parsed = JSON.parse(raw) as T;
  configCache[relativePath] = parsed;
  return parsed;
}

export function getRuntimeConfig(): RuntimeConfig {
  return loadJsonFile<RuntimeConfig>("config/runtime-config.json");
}

export function getModelPricing(): ModelPricing {
  return loadJsonFile<ModelPricing>("config/model-pricing.json");
}

/**
 * Clear the config cache — useful for tests that need to reload config.
 */
export function clearConfigCache(): void {
  for (const key of Object.keys(configCache)) {
    delete configCache[key];
  }
}
