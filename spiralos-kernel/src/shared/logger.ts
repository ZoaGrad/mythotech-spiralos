import pino from 'pino';
import { env } from './env.js';

export const logger = pino({
  name: 'spiralos-kernel',
  level: env.LOG_LEVEL ?? 'info',
  transport: process.env.NODE_ENV === 'production' ? undefined : {
    target: 'pino-pretty',
    options: { colorize: true, translateTime: 'SYS:standard' }
  }
});
