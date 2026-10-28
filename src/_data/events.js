import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const dir = path.join(path.dirname(fileURLToPath(import.meta.url)), 'events');
const groups = ['2026', '2025', '2024', 'upcoming'];
const series = {
  '2026': { title: '2026 Summer Series', url: '/2026-summer-series-at-evergreen-brickworks/' },
  '2025': { title: '2025 Summer Series', url: '/2025-summer-series-at-guild-park/' },
  '2024': { title: '2024 Summer Series', url: '/2024summerseriesguildpark/' },
  upcoming: { title: 'Upcoming events', url: '/upcoming-events/' }
};

const byGroup = {};
const all = [];
for (const g of groups) {
  const list = JSON.parse(readFileSync(path.join(dir, g + '.json'), 'utf8'));
  // newest first, like the old site
  list.sort((a, b) => (b.date + b.start).localeCompare(a.date + a.start));
  list.forEach((ev, i) => {
    ev.series = series[g];
    // list is newest first, so "next" is the previous entry
    ev.next = list[i - 1] || null;
    ev.prev = list[i + 1] || null;
    all.push(ev);
  });
  byGroup[g] = list;
}

export default { all, byGroup, series };
