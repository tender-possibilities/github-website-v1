import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const file = path.join(path.dirname(fileURLToPath(import.meta.url)), 'events', 'past_gallery.json');
export default JSON.parse(readFileSync(file, 'utf8'));
