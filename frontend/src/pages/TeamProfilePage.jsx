/**
 * TeamProfilePage - Comprehensive, beautiful team profile
 * Rich content with team history, stats, players, matches
 */
import { useState, useEffect, useCallback } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { TEAM_COLORS, TEAM_API_LOGOS, TEAM_CARD_IMAGES, getTeamLogo, normalizeTeam } from '../constants/teams';
import { ArrowLeft, Trophy, Calendar, MapPin, Star, Users, Target, Shield, ChevronRight, Flame, Award } from 'lucide-react';

// Comprehensive IPL team data - bilingual
const TEAM_DATABASE = {
  MI: {
    name: 'Mumbai Indians',
    name_hi: 'मुंबई इंडियंस',
    short: 'MI',
    city: 'Mumbai',
    founded: 2008,
    home_ground: 'Wankhede Stadium',
    capacity: '33,108',
    owner: 'Nita Ambani & Akash Ambani',
    titles: 5,
    title_years: [2013, 2015, 2017, 2019, 2020],
    captain: 'Hardik Pandya',
    coach: 'Mark Boucher',
    motto: 'Duniya Hila Denge Hum',
    color_primary: '#004BA0',
    color_secondary: '#D4AF37',
    history: `Mumbai Indians, the most decorated franchise in IPL history with 5 titles, represent the cricketing capital of India. Founded by the Ambani family under Reliance Industries, MI has been the gold standard of T20 franchise cricket.\n\nFrom Sachin Tendulkar's captaincy in the early years to Rohit Sharma's legendary five-title dynasty, MI has always believed in building a squad for the long term. The franchise is known for its data-driven approach to auctions and its famous "trust the process" philosophy.\n\nKey moments include the iconic 2019 final against CSK won by just 1 run, the dominant 2020 season in UAE where they went unbeaten in the playoffs, and their remarkable ability to peak exactly when it matters most.`,
    history_hi: `मुंबई इंडियंस, IPL इतिहास की सबसे सफल फ्रेंचाइजी है - 5 खिताब जीतकर। अंबानी परिवार द्वारा स्थापित MI ने T20 क्रिकेट में एक नई मिसाल कायम की है। सचिन तेंदुलकर की कप्तानी से लेकर रोहित शर्मा के पांच खिताबी युग तक, MI ने हमेशा "ट्रस्ट द प्रोसेस" के फिलॉसफी पर विश्वास किया।`,
    fun_facts: [
      'Only team to win IPL 5 times',
      'Rohit Sharma has the most IPL titles as captain (5)',
      'Jasprit Bumrah was discovered by MI scouts at age 19',
      'MI holds the record for most consecutive wins in a season (9)',
    ],
    key_players: ['Rohit Sharma', 'Jasprit Bumrah', 'Suryakumar Yadav', 'Ishan Kishan', 'Tim David'],
  },
  CSK: {
    name: 'Chennai Super Kings',
    name_hi: 'चेन्नई सुपर किंग्स',
    short: 'CSK',
    city: 'Chennai',
    founded: 2008,
    home_ground: 'M.A. Chidambaram Stadium',
    capacity: '50,000',
    owner: 'Chennai Super Kings Cricket Ltd. (N. Srinivasan)',
    titles: 5,
    title_years: [2010, 2011, 2018, 2021, 2023],
    captain: 'Ruturaj Gaikwad',
    coach: 'Stephen Fleming',
    motto: 'Whistle Podu',
    color_primary: '#FCCA00',
    color_secondary: '#0081E9',
    history: `Chennai Super Kings, the Yellow Army, stands alongside MI as the joint most-successful team in IPL history with 5 titles. Under the legendary MS Dhoni — the greatest captain in IPL history — CSK built a dynasty based on experience, calmness under pressure, and unshakeable team spirit.\n\nCSK was banned for 2 years (2016-17) in the spot-fixing scandal, but returned with a vengeance in 2018, winning the title immediately. Dhoni's famous "Thala for a reason" persona made CSK a brand larger than just cricket.\n\nThe Chepauk fortress, with its spinning pitch and passionate crowd doing "Whistle Podu," makes it one of the toughest venues in IPL. CSK has made 10 finals in 14 seasons — the most consistent team in cricket history.\n\nIn 2023, Dhoni passed the captaincy to Ruturaj Gaikwad, beginning a new era while still playing his farewell seasons to packed stadiums of emotional fans.`,
    history_hi: `चेन्नई सुपर किंग्स, Yellow Army, IPL की सबसे कंसिस्टेंट टीम है — 5 खिताब और 10 फाइनल्स। MS धोनी की कप्तानी में CSK ने शांत दिमाग और अनुभव के बल पर एक राजवंश बनाया। 2 साल के बैन के बाद 2018 में वापसी और खिताब जीतना CSK की जिद का सबूत है।`,
    fun_facts: [
      'Most IPL finals appearances (10)',
      'Dhoni has led CSK to 5 titles — most by any captain',
      'CSK returned from a 2-year ban to win the title in 2018',
      'Chepauk\'s spinning track is one of the toughest venues to bat',
      'CSK has the highest win percentage among all IPL teams',
    ],
    key_players: ['MS Dhoni', 'Ruturaj Gaikwad', 'Ravindra Jadeja', 'Devon Conway', 'Matheesha Pathirana'],
  },
  RCB: {
    name: 'Royal Challengers Bengaluru',
    name_hi: 'रॉयल चैलेंजर्स बेंगलुरु',
    short: 'RCB',
    city: 'Bengaluru',
    founded: 2008,
    home_ground: 'M. Chinnaswamy Stadium',
    capacity: '40,000',
    owner: 'United Spirits (Diageo)',
    titles: 0,
    title_years: [],
    captain: 'Virat Kohli',
    coach: 'Andy Flower',
    motto: 'Ee Sala Cup Namde',
    color_primary: '#EC1C24',
    color_secondary: '#2B2A29',
    history: `Royal Challengers Bengaluru is the most passionate fanbase in IPL history, yet the most heartbreaking franchise. Despite having legends like Virat Kohli, AB de Villiers, and Chris Gayle — arguably the greatest T20 batsmen ever assembled — RCB has never won the IPL.\n\n"Ee Sala Cup Namde" (This year the cup is ours) has become both a war cry and a meme. But the passion is real — Chinnaswamy Stadium on match night is the loudest, most electric atmosphere in world cricket.\n\nRCB holds the record for the highest individual score (Chris Gayle's 175* vs PWI in 2013), the highest team total (263/5), and Virat Kohli's unbreakable 973-run season in 2016. They've reached 3 finals (2009, 2011, 2016) but fallen short each time.\n\nThe franchise represents hope — the belief that talent, passion, and one magical season can change everything.`,
    history_hi: `RCB IPL का सबसे पैशनेट फैनबेस है — लेकिन अब तक एक भी खिताब नहीं। विराट कोहली, AB डिविलियर्स, क्रिस गेल जैसे दिग्गज होने के बावजूद। "Ee Sala Cup Namde" हर साल गूंजता है। चिन्नास्वामी का माहौल दुनिया में सबसे गर्म है।`,
    fun_facts: [
      'Chris Gayle scored 175* — highest individual IPL score',
      'Virat Kohli scored 973 runs in IPL 2016 — all-time record',
      'RCB holds the highest team total: 263/5',
      'Most passionate fanbase — "Ee Sala Cup Namde" is iconic',
      '3 finals reached but 0 titles won',
    ],
    key_players: ['Virat Kohli', 'Faf du Plessis', 'Glenn Maxwell', 'Mohammed Siraj', 'Rajat Patidar'],
  },
  KKR: {
    name: 'Kolkata Knight Riders',
    name_hi: 'कोलकाता नाइट राइडर्स',
    short: 'KKR',
    city: 'Kolkata',
    founded: 2008,
    home_ground: 'Eden Gardens',
    capacity: '66,000',
    owner: 'Shah Rukh Khan & Juhi Chawla',
    titles: 3,
    title_years: [2012, 2014, 2024],
    captain: 'Shreyas Iyer',
    coach: 'Chandrakant Pandit',
    motto: 'Korbo Lorbo Jeetbo Re',
    color_primary: '#3A225D',
    color_secondary: '#B3A123',
    history: `Kolkata Knight Riders, owned by Bollywood's King Shah Rukh Khan, brings the glamour and drama of Mumbai's film industry to cricket. The franchise struggled in early seasons but transformed under Gautam Gambhir's captaincy, winning back-to-back titles in 2012 and 2014.\n\nEden Gardens, the Mecca of Indian cricket with 66,000+ capacity, creates an atmosphere unlike any other ground. The purple and gold jersey is one of the most recognizable in world sport.\n\nKKR won their third title in 2024 in dominant fashion, proving they had rebuilt successfully. Their famous "Korbo Lorbo Jeetbo Re" (We'll do, fight, and win) anthem captures the fighting Bengali spirit.`,
    history_hi: `KKR, शाहरुख खान की टीम, ग्लैमर और क्रिकेट का बेजोड़ संगम। गौतम गंभीर की कप्तानी में 2012 और 2014 में खिताब जीता। ईडन गार्डन्स का माहौल बेमिसाल है। 2024 में तीसरा खिताब जीतकर एक नया अध्याय लिखा।`,
    fun_facts: [
      'Owned by Shah Rukh Khan — biggest star in Bollywood',
      'Eden Gardens is the largest cricket stadium in India (66,000+)',
      'Sunil Narine\'s mystery spin changed T20 bowling forever',
      'Won 3 titles: 2012, 2014, 2024',
    ],
    key_players: ['Shreyas Iyer', 'Andre Russell', 'Sunil Narine', 'Phil Salt', 'Varun Chakravarthy'],
  },
  DC: {
    name: 'Delhi Capitals',
    name_hi: 'दिल्ली कैपिटल्स',
    short: 'DC',
    city: 'Delhi',
    founded: 2008,
    home_ground: 'Arun Jaitley Stadium',
    capacity: '41,820',
    owner: 'GMR Group & JSW Sports',
    titles: 0,
    title_years: [],
    captain: 'KL Rahul',
    coach: 'Ricky Ponting',
    motto: 'Roar Macha',
    color_primary: '#0078BC',
    color_secondary: '#EF1B23',
    history: `Delhi Capitals (formerly Daredevils) has been the underdog story of IPL. After years of struggle, they finally reached their first IPL final in 2020 under Shreyas Iyer's captaincy.\n\nWith coach Ricky Ponting bringing Australian intensity and a young squad featuring Rishabh Pant, Prithvi Shaw, and world-class overseas talent, DC has become a genuine contender.\n\nThe capital city franchise represents the raw, aggressive spirit of Delhi cricket.`,
    history_hi: `दिल्ली कैपिटल्स (पहले डेयरडेविल्स) IPL का अंडरडॉग है। 2020 में पहली बार फाइनल तक पहुंचे। ऋषभ पंत और रिकी पॉन्टिंग की जोड़ी ने टीम को नई ऊर्जा दी।`,
    fun_facts: [
      'Rebranded from Daredevils to Capitals in 2019',
      'Reached first-ever final in 2020',
      'Rishabh Pant was the youngest IPL captain at 23',
    ],
    key_players: ['KL Rahul', 'David Warner', 'Axar Patel', 'Kuldeep Yadav', 'Mitchell Marsh'],
  },
  PBKS: {
    name: 'Punjab Kings',
    name_hi: 'पंजाब किंग्स',
    short: 'PBKS',
    city: 'Mohali',
    founded: 2008,
    home_ground: 'IS Bindra Stadium',
    capacity: '26,000',
    owner: 'Preity Zinta, Ness Wadia, Mohit Burman',
    titles: 0,
    title_years: [],
    captain: 'Shikhar Dhawan',
    coach: 'Trevor Bayliss',
    motto: 'Sadda Punjab',
    color_primary: '#ED1B24',
    color_secondary: '#A7A9AC',
    history: `Punjab Kings (formerly Kings XI Punjab) is the most unpredictable team in IPL. They can beat any team on their day but have never won the title. Chris Gayle's "Universe Boss" era at Punjab was legendary.\n\nThe passionate Punjabi fanbase brings unmatched energy. Mohali's crowd is known for their dhol beats and Bhangra celebrations.`,
    history_hi: `पंजाब किंग्स IPL की सबसे unpredictable टीम। कभी भी किसी को हरा सकते हैं, लेकिन खिताब अभी तक नहीं। क्रिस गेल का "Universe Boss" युग यादगार था।`,
    fun_facts: [
      'Rebranded from Kings XI Punjab in 2021',
      'Chris Gayle scored fastest IPL century (30 balls) for PBKS',
      'Most dramatic collapses in IPL history',
    ],
    key_players: ['Shikhar Dhawan', 'Sam Curran', 'Liam Livingstone', 'Arshdeep Singh', 'Kagiso Rabada'],
  },
  SRH: {
    name: 'Sunrisers Hyderabad',
    name_hi: 'सनराइजर्स हैदराबाद',
    short: 'SRH',
    city: 'Hyderabad',
    founded: 2013,
    home_ground: 'Rajiv Gandhi International Stadium',
    capacity: '55,000',
    owner: 'Kalanithi Maran (Sun TV)',
    titles: 1,
    title_years: [2016],
    captain: 'Pat Cummins',
    coach: 'Daniel Vettori',
    motto: 'Orange Army',
    color_primary: '#FF822A',
    color_secondary: '#000000',
    history: `Sunrisers Hyderabad replaced the banned Deccan Chargers in 2013 and won the title in just their 4th season (2016) under David Warner's explosive captaincy. Known as the "Orange Army," SRH has been famous for their bowling-first approach.\n\nIn 2024, SRH transformed into the most explosive batting lineup in IPL history, breaking records with Travis Head and Heinrich Klaasen demolishing attacks.`,
    history_hi: `SRH ने 2013 में बैन हुई डेक्कन चार्जर्स की जगह ली और 2016 में डेविड वॉर्नर की कप्तानी में खिताब जीता। "Orange Army" गेंदबाजी की ताकत के लिए मशहूर है।`,
    fun_facts: [
      'Won title in just 4th season (2016)',
      'Replaced banned Deccan Chargers',
      'David Warner scored 4 Orange Caps for SRH',
    ],
    key_players: ['Pat Cummins', 'Travis Head', 'Heinrich Klaasen', 'Bhuvneshwar Kumar', 'Abhishek Sharma'],
  },
  RR: {
    name: 'Rajasthan Royals',
    name_hi: 'राजस्थान रॉयल्स',
    short: 'RR',
    city: 'Jaipur',
    founded: 2008,
    home_ground: 'Sawai Mansingh Stadium',
    capacity: '30,000',
    owner: 'Manoj Badale',
    titles: 1,
    title_years: [2008],
    captain: 'Sanju Samson',
    coach: 'Kumar Sangakkara',
    motto: 'Halla Bol',
    color_primary: '#EA1A85',
    color_secondary: '#254AA5',
    history: `Rajasthan Royals wrote the greatest underdog story in IPL history — winning the inaugural IPL in 2008 under Shane Warne's magical captaincy. With the lowest budget and unknown players, RR proved that cricket intelligence beats spending power.\n\nWarne's mentorship of young Indian players like Ravindra Jadeja, and the heroics of unknown spinner Swapnil Asnodkar, made IPL 2008 legendary. RR reached the 2022 final under Sanju Samson but fell short.`,
    history_hi: `RR ने 2008 में शेन वॉर्न की कप्तानी में पहला IPL जीतकर सबसे बड़ी अंडरडॉग कहानी लिखी। सबसे कम बजट, अनजान खिलाड़ी, लेकिन क्रिकेट IQ ने सब पर भारी पड़ा।`,
    fun_facts: [
      'Won inaugural IPL 2008 as biggest underdogs',
      'Shane Warne\'s captaincy is considered greatest in T20 history',
      'Discovered young talents like Ravindra Jadeja',
    ],
    key_players: ['Sanju Samson', 'Yashasvi Jaiswal', 'Jos Buttler', 'Trent Boult', 'Yuzvendra Chahal'],
  },
  GT: {
    name: 'Gujarat Titans',
    name_hi: 'गुजरात टाइटन्स',
    short: 'GT',
    city: 'Ahmedabad',
    founded: 2022,
    home_ground: 'Narendra Modi Stadium',
    capacity: '132,000',
    owner: 'CVC Capital Partners',
    titles: 1,
    title_years: [2022],
    captain: 'Shubman Gill',
    coach: 'Ashish Nehra',
    motto: 'Aava De',
    color_primary: '#1C1C2B',
    color_secondary: '#D4AF37',
    history: `Gujarat Titans made the most dramatic entrance in IPL history — winning the title in their debut season (2022) under Hardik Pandya's captaincy. Playing at the world's largest cricket stadium (Narendra Modi Stadium, 132,000 capacity), GT combined smart auction picks with fearless cricket.\n\nTheir "Aava De" (Bring it on) spirit, powered by Pandya, Rashid Khan, and David Miller's clutch hitting, made them instant fan favorites. They reached the 2023 final as well, proving their debut wasn't a fluke.`,
    history_hi: `GT ने IPL इतिहास में सबसे dramatic entry की — पहले ही सीजन में 2022 का खिताब। हार्दिक पांड्या की कप्तानी और "Aava De" जोश ने दुनिया के सबसे बड़े स्टेडियम में जादू दिखाया।`,
    fun_facts: [
      'Won IPL in debut season (2022) — unprecedented',
      'Play at world\'s largest cricket stadium (132,000 capacity)',
      'Reached final in 2nd season too (2023)',
      'Rashid Khan\'s leg-spin is GT\'s trump card',
    ],
    key_players: ['Shubman Gill', 'Rashid Khan', 'David Miller', 'Mohammed Shami', 'Sai Sudharsan'],
  },
  LSG: {
    name: 'Lucknow Super Giants',
    name_hi: 'लखनऊ सुपर जायंट्स',
    short: 'LSG',
    city: 'Lucknow',
    founded: 2022,
    home_ground: 'BRSABV Ekana Cricket Stadium',
    capacity: '50,000',
    owner: 'RPSG Group (Sanjiv Goenka)',
    titles: 0,
    title_years: [],
    captain: 'KL Rahul',
    coach: 'Justin Langer',
    motto: 'Super Giant Spirit',
    color_primary: '#A72056',
    color_secondary: '#FFCC00',
    history: `Lucknow Super Giants entered IPL in 2022 alongside GT and immediately became competitive, qualifying for playoffs in their first two seasons. Under KL Rahul's calm leadership and Justin Langer's coaching, LSG built a squad balancing Indian talent with overseas firepower.\n\nThe Ekana Stadium in Lucknow has become a fortress for the franchise, with passionate UP fans filling the stands.`,
    history_hi: `LSG ने 2022 में IPL में एंट्री की और तुरंत competitive बन गई। KL राहुल की शांत कप्तानी में पहले दो सीजन में प्लेऑफ बनाया।`,
    fun_facts: [
      'Qualified for playoffs in debut season',
      'Marcus Stoinis hit fastest LSG century',
      'Ekana Stadium is one of the newest in India',
    ],
    key_players: ['KL Rahul', 'Nicholas Pooran', 'Marcus Stoinis', 'Ravi Bishnoi', 'Quinton de Kock'],
  },
};

export default function TeamProfilePage({ teamShort, matches, onMatchClick, onBack }) {
  const [showFullHistory, setShowFullHistory] = useState(false);

  const team = TEAM_DATABASE[normalizeTeam(teamShort)] || TEAM_DATABASE[teamShort];
  if (!team) return null;

  const color = TEAM_COLORS[normalizeTeam(teamShort)]?.primary || team.color_primary;
  const logo = TEAM_API_LOGOS[normalizeTeam(teamShort)] || '';
  const cardImg = TEAM_CARD_IMAGES[normalizeTeam(teamShort)] || '';

  const teamMatches = (matches || []).filter(m => {
    const a = normalizeTeam(m.team_a?.short_name || '');
    const b = normalizeTeam(m.team_b?.short_name || '');
    const norm = normalizeTeam(teamShort);
    return a === norm || b === norm;
  });

  return (
    <div data-testid="team-profile-page" className="space-y-5 pb-8">
      {/* Back */}
      <button data-testid="team-back-btn" onClick={onBack}
        className="text-xs flex items-center gap-1" style={{ color: COLORS.text.secondary }}>
        <ArrowLeft size={14} /> Back to Search
      </button>

      {/* Hero Banner */}
      <div className="rounded-2xl overflow-hidden relative" style={{ height: '200px' }}>
        {cardImg && <img src={cardImg} alt="" className="w-full h-full object-cover" />}
        <div className="absolute inset-0" style={{
          background: `linear-gradient(to top, ${color}EE 0%, ${color}88 40%, transparent 100%)`
        }} />
        <div className="absolute bottom-0 left-0 right-0 p-5">
          <div className="flex items-end gap-4">
            <div className="w-16 h-16 rounded-2xl overflow-hidden flex items-center justify-center shadow-xl"
              style={{ background: '#fff', border: `3px solid ${color}` }}>
              {logo ? <img src={logo} alt="" className="w-12 h-12 object-contain" /> :
                <span className="text-lg font-black" style={{ color }}>{team.short}</span>}
            </div>
            <div className="flex-1">
              <div className="text-xl font-black text-white leading-tight drop-shadow-lg">{team.name}</div>
              <div className="text-xs mt-0.5 font-medium" style={{ color: '#ffffffcc' }}>{team.name_hi}</div>
              <div className="flex items-center gap-3 mt-1.5">
                <span className="text-[10px] flex items-center gap-1" style={{ color: '#ffffffaa' }}>
                  <MapPin size={10} /> {team.city}
                </span>
                <span className="text-[10px] flex items-center gap-1" style={{ color: '#ffffffaa' }}>
                  <Calendar size={10} /> Est. {team.founded}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats Strip */}
      <div className="grid grid-cols-4 gap-2">
        {[
          { label: 'Titles', value: team.titles, Icon: Trophy, col: '#FFD700' },
          { label: 'Captain', value: team.captain?.split(' ').pop(), Icon: Shield, col: color },
          { label: 'Matches', value: teamMatches.length, Icon: Calendar, col: COLORS.info.main },
          { label: 'Founded', value: team.founded, Icon: Star, col: COLORS.warning.main },
        ].map(({ label, value, Icon, col }) => (
          <div key={label} className="text-center p-2.5 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${col}15` }}>
            <Icon size={14} color={col} className="mx-auto mb-1" />
            <div className="text-sm font-black text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>{value}</div>
            <div className="text-[8px] font-bold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Title Years */}
      {team.title_years.length > 0 && (
        <div className="p-4 rounded-2xl relative overflow-hidden" style={{
          background: `linear-gradient(135deg, #1a1a2e, ${color}22)`,
          border: `1px solid ${color}33`
        }}>
          <div className="absolute top-2 right-3 opacity-10"><Trophy size={48} color={color} /></div>
          <div className="text-[10px] font-bold uppercase tracking-wider mb-2" style={{ color }}>Championship Titles</div>
          <div className="flex gap-2 flex-wrap">
            {team.title_years.map(year => (
              <div key={year} className="px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1"
                style={{ background: `${color}22`, color, border: `1px solid ${color}44` }}>
                <Trophy size={10} /> {year}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Team Details Card */}
      <div className="p-4 rounded-2xl space-y-3" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        <div className="text-xs font-bold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>Team Info</div>
        {[
          { label: 'Home Ground', value: `${team.home_ground} (${team.capacity})` },
          { label: 'Captain', value: team.captain },
          { label: 'Coach', value: team.coach },
          { label: 'Owner', value: team.owner },
          { label: 'Motto', value: `"${team.motto}"` },
        ].map(({ label, value }) => (
          <div key={label} className="flex items-center justify-between py-1.5" style={{ borderBottom: `1px solid ${COLORS.border.light}` }}>
            <span className="text-[10px] font-bold" style={{ color: COLORS.text.tertiary }}>{label}</span>
            <span className="text-xs font-medium text-white text-right max-w-[60%]">{value}</span>
          </div>
        ))}
      </div>

      {/* History Essay */}
      <div className="p-4 rounded-2xl space-y-3" style={{
        background: `linear-gradient(180deg, ${color}08, ${COLORS.background.card})`,
        border: `1px solid ${color}15`
      }}>
        <div className="flex items-center gap-2">
          <Flame size={16} color={color} />
          <span className="text-xs font-bold uppercase tracking-wider" style={{ color }}>History & Legacy</span>
        </div>
        <div className="text-xs leading-relaxed whitespace-pre-line" style={{ color: COLORS.text.secondary }}>
          {showFullHistory ? team.history : team.history.slice(0, 300) + '...'}
        </div>
        {team.history.length > 300 && (
          <button onClick={() => setShowFullHistory(!showFullHistory)}
            className="text-[10px] font-bold" style={{ color }}>
            {showFullHistory ? 'Show Less' : 'Read Full Story'}
          </button>
        )}
        {/* Hindi Version */}
        <div className="p-3 rounded-xl mt-2" style={{ background: `${color}08` }}>
          <div className="text-[10px] font-bold mb-1" style={{ color: COLORS.text.tertiary }}>हिंदी</div>
          <div className="text-[11px] leading-relaxed" style={{ color: COLORS.text.secondary }}>
            {team.history_hi}
          </div>
        </div>
      </div>

      {/* Key Players */}
      <div className="space-y-2.5">
        <div className="flex items-center gap-2">
          <Users size={16} color={color} />
          <span className="text-xs font-bold uppercase tracking-wider" style={{ color }}>Key Players</span>
        </div>
        <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar">
          {team.key_players.map((player, i) => (
            <div key={player} className="shrink-0 px-4 py-3 rounded-xl text-center min-w-[100px]" style={{
              background: COLORS.background.card,
              border: `1px solid ${color}22`
            }}>
              <div className="w-10 h-10 mx-auto rounded-full flex items-center justify-center text-sm font-black mb-1.5"
                style={{ background: `${color}22`, color }}>
                {player.split(' ').map(n => n[0]).join('')}
              </div>
              <div className="text-[10px] font-bold text-white">{player.split(' ').pop()}</div>
              <div className="text-[8px]" style={{ color: COLORS.text.tertiary }}>{player.split(' ')[0]}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Fun Facts */}
      <div className="p-4 rounded-2xl space-y-2.5" style={{
        background: COLORS.background.card,
        border: `1px solid ${color}15`
      }}>
        <div className="flex items-center gap-2">
          <Award size={16} color={color} />
          <span className="text-xs font-bold uppercase tracking-wider" style={{ color }}>Did You Know?</span>
        </div>
        {team.fun_facts.map((fact, i) => (
          <div key={i} className="flex items-start gap-2.5 p-2 rounded-lg" style={{ background: `${color}08` }}>
            <div className="w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5 text-[9px] font-black" style={{ background: `${color}22`, color }}>
              {i + 1}
            </div>
            <span className="text-[11px] leading-snug" style={{ color: COLORS.text.secondary }}>{fact}</span>
          </div>
        ))}
      </div>

      {/* Upcoming Matches */}
      {teamMatches.length > 0 && (
        <div className="space-y-2.5">
          <div className="text-xs font-bold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>
            {team.short} Matches ({teamMatches.length})
          </div>
          {teamMatches.map(m => {
            const ta = m.team_a?.short_name || '?';
            const tb = m.team_b?.short_name || '?';
            const isLive = m.status === 'live';
            return (
              <button key={m.id} onClick={() => onMatchClick?.(m)}
                className="w-full text-left rounded-xl p-3.5 transition-all active:scale-[0.98]"
                style={{ background: COLORS.background.card, border: `1px solid ${isLive ? '#FF3B3B33' : COLORS.border.light}` }}>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-bold text-white">{ta} vs {tb}</div>
                    <div className="text-[10px] mt-0.5" style={{ color: COLORS.text.tertiary }}>
                      {m.venue?.slice(0, 30)} | {m.start_time ? new Date(m.start_time).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : ''}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full" style={{
                      background: isLive ? '#FF3B3B22' : COLORS.info.bg,
                      color: isLive ? '#FF3B3B' : COLORS.info.main
                    }}>{m.status?.toUpperCase()}</span>
                    <ChevronRight size={14} color={COLORS.text.tertiary} />
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
