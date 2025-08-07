import { existsSync, readFileSync, writeFileSync, mkdirSync } from "fs";
import { homedir } from "os";
import { join } from "path";
import type { Config } from "./types";

const CONFIG_DIR = join(homedir(), ".config", "gpt-image-gen");
const CONFIG_FILE = join(CONFIG_DIR, "config.json");

export class ConfigManager {
  private config: Config = {};

  constructor() {
    this.loadConfig();
  }

  private loadConfig(): void {
    if (existsSync(CONFIG_FILE)) {
      try {
        const data = readFileSync(CONFIG_FILE, "utf-8");
        this.config = JSON.parse(data);
      } catch (error) {
        console.error("Warning: Failed to load config file:", error);
      }
    }
  }

  private saveConfig(): void {
    if (!existsSync(CONFIG_DIR)) {
      mkdirSync(CONFIG_DIR, { recursive: true });
    }
    writeFileSync(CONFIG_FILE, JSON.stringify(this.config, null, 2));
  }

  getApiKey(): string | undefined {
    return process.env.OPENAI_API_KEY || this.config.apiKey;
  }

  setApiKey(apiKey: string): void {
    this.config.apiKey = apiKey;
    this.saveConfig();
  }

  get(key: keyof Config): any {
    return this.config[key];
  }

  set(key: keyof Config, value: any): void {
    this.config[key] = value;
    this.saveConfig();
  }

  getAll(): Config {
    return { ...this.config };
  }

  clear(): void {
    this.config = {};
    this.saveConfig();
  }
}