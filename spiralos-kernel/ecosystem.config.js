/**
 * PM2 ecosystem configuration for the SpiralOS v2 kernel workers.
 * Use `pm2 start ecosystem.config.js` to launch both the SSD Guard and Scar Index Oracle workers.
 */
module.exports = {
  apps: [
    {
      name: "ssd-guard",
      script: "npm",
      args: "run start:ssd-guard",
      cwd: "./spiralos-kernel",
      exec_mode: "fork",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "300M",
      env: {
        NODE_ENV: "production",
      },
    },
    {
      name: "scar-index-oracle",
      script: "npm",
      args: "run start:scar-index",
      cwd: "./spiralos-kernel",
      exec_mode: "fork",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "300M",
      env: {
        NODE_ENV: "production",
      },
    },
  ],
};
