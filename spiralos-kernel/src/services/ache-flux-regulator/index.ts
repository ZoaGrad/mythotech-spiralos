import { logger } from '../../shared/logger.js';
import { startAfrLoop } from './afrWorker.js';

startAfrLoop().catch((error) => {
    logger.fatal({ error }, 'AFR loop crashed');
    process.exit(1);
});
