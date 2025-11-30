import { logger } from '../../shared/logger.js';
import { startScarIndexLoop } from './scarIndexWorker.js';

startScarIndexLoop().catch((error) => {
  logger.fatal({ error }, 'ScarIndex loop crashed');
  process.exit(1);
});
