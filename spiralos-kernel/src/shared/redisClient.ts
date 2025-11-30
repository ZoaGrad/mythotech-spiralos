import Redis from 'ioredis';
import { logger } from './logger.js';

const redisConfig = {
    host: process.env.REDIS_HOST || 'redis-16500.c326.us-east-1-3.ec2.cloud.redislabs.com',
    port: parseInt(process.env.REDIS_PORT || '16500'),
    password: process.env.REDIS_PASSWORD || 'BUaC7qpXvVfM8dE992uADIM6UHTX7NDM',
    retryDelayOnFailover: 100,
    maxRetriesPerRequest: null,
    enableReadyCheck: true,
    lazyConnect: true
};

class RedisClient {
    private client: Redis;
    private isConnected = false;

    constructor() {
        this.client = new Redis(redisConfig);
        this.setupEventListeners();
    }

    private setupEventListeners() {
        this.client.on('connect', () => {
            this.isConnected = true;
            logger.info('Redis client connected');
        });

        this.client.on('error', (error) => {
            logger.error({ err: error }, 'Redis client error');
            this.isConnected = false;
        });

        this.client.on('close', () => {
            logger.warn('Redis connection closed');
            this.isConnected = false;
        });

        this.client.on('reconnecting', () => {
            logger.info('Redis client reconnecting...');
        });
    }

    async ensureConnection(): Promise<boolean> {
        if (this.isConnected) return true;

        try {
            await this.client.connect();
            return true;
        } catch (error) {
            logger.error({ err: error }, 'Failed to connect to Redis');
            return false;
        }
    }

    getClient(): Redis {
        return this.client;
    }

    async disconnect(): Promise<void> {
        await this.client.quit();
    }
}

export const redisClient = new RedisClient();
export const connection = redisClient.getClient();
