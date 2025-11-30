import { logger } from '../../shared/logger.js';
import { startSsdGuardLoop } from './ssdWorker.js';

startSsdGuardLoop().catch((error) => {
  logger.fatal({ error }, 'SSD Guard loop crashed');
  process.exit(1);
});
