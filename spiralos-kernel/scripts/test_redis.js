import { connection } from "../dist/shared/redisClient.js";

async function main() {
    try {
        const pong = await connection.ping();
        console.log("Redis PING:", pong);
    } catch (err) {
        console.error("Redis Test Failed:", err);
    } finally {
        process.exit(0);
    }
}

main();
