import { Queue } from "bullmq";
import { connection } from "../dist/shared/redisClient.js";

async function main() {
    const q = new Queue("ConstitutionalCoupling", { connection });

    console.log("Pushing ΔΩ.150.4 First Constitutional Amendment Trigger...");

    await q.add("ccc-trigger", {
        mode: "force_amendment",
        overrides: {
            afr_adjustment_imperative: 0.95, // Forces 'emergency_thermodynamic' trigger
            paradox_density: 0.2
        }
    });

    console.log("Trigger fired. The Constitution should speak shortly.");
    process.exit(0);
}

main();
