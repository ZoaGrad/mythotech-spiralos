import { Queue } from "bullmq";
import { connection } from "../dist/shared/redisClient.js";

async function main() {
    const q = new Queue("ConstitutionalCoupling", { connection });

    const counts = await q.getJobCounts();
    console.log("Job Counts:", counts);

    process.exit(0);
}

main();
