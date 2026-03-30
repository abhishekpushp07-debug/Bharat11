/**
 * IPL Team Constants — All 10 teams with logos, colors, shortnames
 * Logo images provided by user. CricketData API logos for small display.
 */

// User-provided team card images (1024x480)
export const TEAM_CARD_IMAGES = {
  GT: 'https://customer-assets.emergentagent.com/job_5deb66be-3e3c-4154-87e7-3979bdc5fae2/artifacts/b82e7ewx_IPL-Match-29-GT-vs-CSK-1024x480.jpg',
  DC: 'https://customer-assets.emergentagent.com/job_5deb66be-3e3c-4154-87e7-3979bdc5fae2/artifacts/9pc1ygzy_IPL-Match-50-DC-vs-SH-1024x480.jpg',
  CSK: 'https://customer-assets.emergentagent.com/job_5deb66be-3e3c-4154-87e7-3979bdc5fae2/artifacts/h6rpvfme_IPL-Match-62-CSK-vs-GT-1024x480.jpg',
  LSG: 'https://customer-assets.emergentagent.com/job_5deb66be-3e3c-4154-87e7-3979bdc5fae2/artifacts/0c6r9bor_IPL-Match-63-LSG-vs-RR-1024x480.jpg',
  PBKS: 'https://customer-assets.emergentagent.com/job_5deb66be-3e3c-4154-87e7-3979bdc5fae2/artifacts/cm0mnlsz_IPL-Match-64-PK-vs-DC-1024x480.jpg',
  PK: 'https://customer-assets.emergentagent.com/job_5deb66be-3e3c-4154-87e7-3979bdc5fae2/artifacts/cm0mnlsz_IPL-Match-64-PK-vs-DC-1024x480.jpg',
  SRH: 'https://customer-assets.emergentagent.com/job_5deb66be-3e3c-4154-87e7-3979bdc5fae2/artifacts/aogoxkcd_IPL-Match-70-SH-vs-PK-1024x480.jpg',
  SH: 'https://customer-assets.emergentagent.com/job_5deb66be-3e3c-4154-87e7-3979bdc5fae2/artifacts/aogoxkcd_IPL-Match-70-SH-vs-PK-1024x480.jpg',
  KKR: 'https://customer-assets.emergentagent.com/job_5deb66be-3e3c-4154-87e7-3979bdc5fae2/artifacts/8m8qmbdt_IPL-Match-66-KKR-vs-LSG-1024x480.jpg',
  RCB: 'https://customer-assets.emergentagent.com/job_5deb66be-3e3c-4154-87e7-3979bdc5fae2/artifacts/uvwqzqdc_IPL-Match-67-RCB-vs-GT-1024x480.jpg',
  RCBW: 'https://customer-assets.emergentagent.com/job_5deb66be-3e3c-4154-87e7-3979bdc5fae2/artifacts/uvwqzqdc_IPL-Match-67-RCB-vs-GT-1024x480.jpg',
  RR: 'https://customer-assets.emergentagent.com/job_5deb66be-3e3c-4154-87e7-3979bdc5fae2/artifacts/n6dxt54b_IPL-Match-68-RR-vs-CSK-1024x480.jpg',
  MI: 'https://customer-assets.emergentagent.com/job_5deb66be-3e3c-4154-87e7-3979bdc5fae2/artifacts/e63286lf_IPL-Match-69-MI-vs-DC-1024x480.jpg',
};

// CricketData API team logos (small 48px) — from series_points response
export const TEAM_API_LOGOS = {
  CSK: 'https://g.cricapi.com/iapi/135-637852956181378533.png?w=48',
  DC: 'https://g.cricapi.com/iapi/148-637874596301457910.png?w=48',
  GT: 'https://g.cricapi.com/iapi/172-637852957798476823.png?w=48',
  KKR: 'https://g.cricapi.com/iapi/206-637852958714346149.png?w=48',
  LSG: 'https://g.cricapi.com/iapi/215-637876059669009476.png?w=48',
  MI: 'https://g.cricapi.com/iapi/226-637852956375593901.png?w=48',
  PBKS: 'https://g.cricapi.com/iapi/247-637852956959778791.png?w=48',
  PK: 'https://g.cricapi.com/iapi/247-637852956959778791.png?w=48',
  RR: 'https://g.cricapi.com/iapi/251-637852956607161886.png?w=48',
  RCB: 'https://g.cricapi.com/iapi/21439-638468478038395955.jpg?w=48',
  RCBW: 'https://g.cricapi.com/iapi/21439-638468478038395955.jpg?w=48',
  SRH: 'https://g.cricapi.com/iapi/279-637852957609490368.png?w=48',
  SH: 'https://g.cricapi.com/iapi/279-637852957609490368.png?w=48',
};

// Team brand colors {primary, secondary}
export const TEAM_COLORS = {
  MI: { primary: '#004BA0', secondary: '#00599E' },
  CSK: { primary: '#F9CD05', secondary: '#F3A012' },
  RCB: { primary: '#D4213D', secondary: '#A0171F' },
  RCBW: { primary: '#D4213D', secondary: '#A0171F' },
  KKR: { primary: '#3A225D', secondary: '#552583' },
  DC: { primary: '#0078BC', secondary: '#17479E' },
  PBKS: { primary: '#ED1B24', secondary: '#AA1019' },
  PK: { primary: '#ED1B24', secondary: '#AA1019' },
  SRH: { primary: '#FF822A', secondary: '#E35205' },
  SH: { primary: '#FF822A', secondary: '#E35205' },
  RR: { primary: '#EA1A85', secondary: '#C51D70' },
  GT: { primary: '#1C1C2B', secondary: '#0B4F6C' },
  LSG: { primary: '#2E90A8', secondary: '#1B7B93' },
};

// All valid IPL short names (for filtering)
export const IPL_TEAMS = new Set([
  'MI', 'CSK', 'RCB', 'RCBW', 'KKR', 'DC', 'PBKS', 'PK', 'SRH', 'SH', 'RR', 'GT', 'LSG'
]);

// Normalize team shortname (CricketData uses RCBW for RCB, PBKS for PK etc.)
export const normalizeTeam = (short) => {
  const map = { 'RCBW': 'RCB', 'PK': 'PBKS', 'SH': 'SRH' };
  return map[short] || short;
};

// Get team gradient for backgrounds
export const getTeamGradient = (short) => {
  const c = TEAM_COLORS[short] || { primary: '#555', secondary: '#333' };
  return `linear-gradient(135deg, ${c.primary}, ${c.secondary})`;
};

// Get small logo URL
export const getTeamLogo = (short) => TEAM_API_LOGOS[short] || TEAM_API_LOGOS[normalizeTeam(short)] || '';

// Get card image URL
export const getTeamCardImage = (short) => TEAM_CARD_IMAGES[short] || TEAM_CARD_IMAGES[normalizeTeam(short)] || '';
