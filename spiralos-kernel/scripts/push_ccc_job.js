import { Queue } from "bullmq";
import { connection } from "../dist/shared/redisClient.js";

async function main() {
    const q = new Queue("ConstitutionalCoupling", { connection });

    await q.add("ccc-test", { mode: "validation" });

    console.log("Pushed CCC validation job.");
    process.exit(0);
}

main();
