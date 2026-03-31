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
    history: `Mumbai Indians — the most decorated franchise in IPL history — isn't just a cricket team. It's a dynasty.\n\nThe early years (2008-2012) were rough. Sachin Tendulkar captained, Harbhajan Singh led the bowling. MI were talented but couldn't crack the code. Then in 2013, a quiet kid from Nagpur named Rohit Sharma took over captaincy mid-season from Ricky Ponting. Nobody expected what happened next.\n\nRohit won the title that very year. Then 2015. Then 2017. Then 2019. Then 2020. FIVE titles in EIGHT years. The most dominant run in T20 franchise history.\n\nThe 2017 final against Rising Pune Supergiant is IPL folklore — Mitchell Johnson's last over, Steve Smith caught at the boundary, MI winning by 1 run. Then in 2019, the EXACT same script — CSK needed 2 off the last ball, Shardul bowled it, Dhoni couldn't finish. MI won by 1 run again. Two 1-run finals. You can't write this stuff.\n\nLasith Malinga's yorkers, Kieron Pollard's muscle, Hardik Pandya's flair, and Bumrah's unplayable death bowling — MI's DNA is about peaking in pressure moments.\n\n2022 and 2024 saw MI finish 10th (last). But in 2025, with Suryakumar Yadav smashing 717 runs at 167.91 SR, MI roared back to playoffs. Wankhede at full capacity on matchnight? There's nothing like it in world cricket.\n\nThe Ambani family's vision — data-driven auctions, trust the process philosophy, long-term player development — has made MI the gold standard of franchise sport globally.`,
    history_hi: `मुंबई इंडियंस — IPL इतिहास की सबसे सफल फ्रेंचाइजी। 2008-2012 तक संघर्ष, फिर 2013 में रोहित शर्मा की कप्तानी शुरू हुई और इतिहास बदल गया। 8 साल में 5 खिताब! 2017 और 2019 में 1-1 रन से जीते फाइनल — ऐसी किस्मत किसी की नहीं। मलिंगा की यॉर्कर, पोलार्ड की ताकत, बुमराह की डेथ बॉलिंग — MI का DNA प्रेशर में चमकना है। वानखेड़े का माहौल दुनिया में बेमिसाल। 2022 और 2024 में 10वें रहे, लेकिन 2025 में SKY के 717 रनों से वापसी। Trust the Process — यही MI है।`,
    fun_facts: [
      'Two 1-run final wins (2017 vs RPS, 2019 vs CSK) — only MI!',
      'Rohit took over captaincy mid-2013 season and won the title immediately',
      'Bumrah was discovered playing tennis-ball cricket in Ahmedabad at age 19',
      'Only team to finish 10th twice (2022, 2024) AND have 5 titles',
      'Wankhede on MI match night is the loudest cricket venue in India',
      'Sachin Tendulkar was MI icon player and first captain (2008-2012)',
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
    history: `Chennai Super Kings isn't just a cricket team. It's a religion. And MS Dhoni? He's the god.\n\nCSK has been the MOST CONSISTENT team in IPL history — 10 finals, 12 playoff appearances in 16 seasons. Under Dhoni's captaincy, CSK built a philosophy that went against everything modern T20 cricket believed: pick experience over youth, trust process over panic, stay calm when everyone else is screaming.\n\nThe 2013 spot-fixing scandal nearly destroyed CSK. The Lodha Committee banned CSK for 2 years (2016-2017) after team principal Gurunath Meiyappan was found guilty of betting. Dhoni was shipped to Rising Pune Supergiant. Fans were devastated. Cricket said CSK was finished.\n\nThen came 2018. The comeback. CSK returned from exile, were called "Daddies Army" for their aged squad, and won the title in their first game back. Shane Watson's 117* in the final — bleeding knee, tape on his legs, batting like a warrior — is IPL's most iconic individual performance in a final. Dhoni wept. India wept.\n\nChepauk's spinning tracks, the deafening "Whistle Podu," Dhoni's 112-metre six against MI in the 2012 eliminator, Ravindra Jadeja's all-round brilliance — CSK is emotion, not just cricket.\n\nIn 2023, Dhoni won his 5th title, equaling Rohit's record. He then passed the captaincy to Ruturaj Gaikwad, his handpicked heir. Every Dhoni match at Chepauk since has felt like a farewell — 50,000 fans chanting "Dhoni Dhoni" with tears in their eyes.\n\nThe Yellow Army is forever. Whistle Podu!`,
    history_hi: `CSK सिर्फ क्रिकेट टीम नहीं, एक धर्म है। और धोनी? भगवान। 16 सीजन में 10 फाइनल, 12 प्लेऑफ — ऐसी consistency किसी की नहीं। 2013 में सट्टेबाजी स्कैंडल के बाद 2 साल का बैन — सब बोले CSK खत्म। फिर 2018 में वापसी और पहले ही सीजन में खिताब! Watson का खून बहता घुटना, 117* फाइनल में — IPL का सबसे iconic पल। चेपॉक की स्पिन पिच, "Whistle Podu" का शोर, धोनी का हेलीकॉप्टर शॉट — CSK = इमोशन। 2023 में 5वां खिताब जीतकर ऋतुराज को कमान दी। Thala for a reason — हमेशा!`,
    fun_facts: [
      'Most IPL finals appearances (10) — nobody is even close',
      'Banned 2 years (2016-2017) — won title in comeback year 2018',
      'Watson batted with bleeding knee in 2018 final — scored 117*',
      'Dhoni hit a 112m six vs MI in 2012 eliminator',
      'Chepauk spinning track — most bowlers fear this ground',
      'CSK = "Daddies Army" — age is just a number when you win',
      'First IPL captain to reach 100 wins — MS Dhoni',
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
    titles: 1,
    title_years: [2025],
    captain: 'Virat Kohli',
    coach: 'Andy Flower',
    motto: 'Ee Sala Cup Namde',
    color_primary: '#EC1C24',
    color_secondary: '#2B2A29',
    history: `Royal Challengers Bengaluru — the franchise that turned 17 years of heartbreak into the greatest redemption story in IPL history.\n\nRCB has always been about superstars. Chris Gayle's 175* — the highest individual score in ANY T20 match ever. Virat Kohli's godlike 2016 season: 973 runs, 4 centuries, 7 fifties in a single IPL. That season, Kohli and AB de Villiers built the two highest partnerships in IPL history — 229 runs and 215 runs. Nobody has come close.\n\nBut IPL trophies? Zero. Year after year after year. "Ee Sala Cup Namde" (This year, the cup is ours!) became the most famous meme in cricket. Three finals reached (2009, 2011, 2016) — three finals lost. In 2017, RCB scored 49 all out against KKR. FORTY-NINE. The lowest score in IPL history. It was the darkest day for any IPL franchise.\n\nThe Chinnaswamy Stadium crowd never gave up. They sang, they cried, they came back. Every year, 40,000 people packed into Bengaluru's cauldron believing THIS was the year.\n\nThen came 2025. IPL's 18th season. Kohli was 36. People said RCB's window was closing. But something magical happened. RCB qualified as the 4th team, fought through qualifiers, and reached the final against PBKS at Wankhede Mumbai.\n\nThe final: PBKS scored 176. RCB chased it down with Kohli anchoring and Rajat Patidar finishing. RCB won by 6 runs. When Kohli lifted the trophy — tears streaming down his face, Chinnaswamy erupting 900 km away — 17 years of pain melted into pure, raw, beautiful joy.\n\n"EE SALA CUP NAMDE" was no longer a meme. It was prophecy. RCB fans across the world sobbed, screamed, and celebrated the greatest moment in their cricket lives. The wait was finally over.`,
    history_hi: `RCB — 17 साल के दर्द के बाद IPL इतिहास की सबसे बड़ी redemption story!\n\nRCB हमेशा सुपरस्टार्स की टीम रही। Gayle का 175* — T20 का सर्वोच्च स्कोर। Kohli का 2016 — 973 रन, 4 शतक! Kohli-ABD ने IPL की दो सबसे बड़ी साझेदारियां (229, 215) बनाईं। लेकिन ट्रॉफी? शून्य।\n\n"Ee Sala Cup Namde" क्रिकेट का सबसे मशहूर meme बन गया। 3 फाइनल (2009, 2011, 2016) — तीनों हारे। 2017 में KKR के खिलाफ 49 ऑल आउट — IPL इतिहास का सबसे कम स्कोर। सबसे काला दिन।\n\nचिन्नास्वामी के 40,000 फैंस ने कभी हार नहीं मानी। गाते रहे, रोते रहे, वापस आते रहे।\n\n2025 — IPL का 18वां सीजन। कोहली 36 के। सब बोले RCB की window बंद। लेकिन जादू हुआ। RCB 4th क्वालीफाई, qualifiers जीते, फाइनल में PBKS से 6 रन से जीते! जब कोहली ने ट्रॉफी उठाई — आंखों में आंसू, चिन्नास्वामी 900 km दूर गूंज रहा — 17 साल का दर्द खुशी में बदल गया। "EE SALA CUP NAMDE" — अब meme नहीं, prophecy है!`,
    fun_facts: [
      'Gayle 175* — highest individual score in ANY T20 ever!',
      'Kohli 973 runs in 2016 — may NEVER be broken',
      'Kohli-ABD hold the top 2 partnerships in IPL (229, 215)',
      '49 all out vs KKR (2017) — IPL lowest score EVER',
      'Won maiden title in 18th IPL season (2025) — beat PBKS in final',
      '"Ee Sala Cup Namde" — from meme to prophecy (2025)',
      '3 finals lost before winning the 4th (2009, 2011, 2016, then 2025)',
      'Chinnaswamy Stadium: loudest crowd in world cricket',
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
    history: `Kolkata Knight Riders — where Bollywood meets cricket. Shah Rukh Khan, the King of Bollywood, bought the franchise and gave it star power no other team could match. But early on, star power wasn't enough.\n\n2008-2010 were painful. KKR couldn't win, couldn't settle on a captain (Sourav Ganguly, Brendon McCullum, John Buchanan). But McCullum's 158* on IPL's very first ball — that blast from 73 balls that launched the entire league — will forever be KKR's gift to cricket history.\n\nThen came 2011. Gautam Gambhir arrived for a record Rs 14.9 Cr and changed EVERYTHING. His leadership, combined with Sunil Narine's mystery spin, turned KKR into champions — 2012 and 2014. "Korbo Lorbo Jeetbo Re" echoed through Eden Gardens as 66,000 fans celebrated.\n\nAfter a 10-year title drought, KKR reinvented themselves in 2024. Narine — the spinner who couldn't bat — was sent to open. He scored 488 runs at 180.74 SR, including his maiden T20 century (109 vs RR). KKR crushed SRH by 8 wickets in the final with 57 balls to spare. It was the most dominant final performance in IPL history.\n\nKKR also holds the longest winning streak in IPL history — 14 consecutive wins. Eden Gardens, the Mecca of Indian cricket, on a KKR match night is where cricket becomes theatre.\n\nSRK watching from the stands, Narine bowling his mystery, Russell smashing sixes into the Kolkata sky — KKR is pure drama.`,
    history_hi: `KKR — जहां बॉलीवुड क्रिकेट से मिलता है। शाहरुख खान ने टीम खरीदी लेकिन शुरुआत कठिन रही। फिर 2011 में गौतम गंभीर आए — Rs 14.9 Cr में — और इतिहास बदल गया। 2012 और 2014 में खिताब! "कोरबो लोरबो जीतबो रे" ईडन गार्डन्स में गूंजा। 10 साल बाद 2024 में नरेन को ओपन कराया — उसने 488 रन बनाए 180.74 SR से! फाइनल में SRH को 57 गेंद शेष रहते हराया। 14 लगातार जीत का IPL रिकॉर्ड भी KKR का है। ईडन गार्डन्स पर KKR मैच = शुद्ध ड्रामा!`,
    fun_facts: [
      'McCullum 158* on IPL first-ever ball (April 18, 2008) — IPL was born here!',
      'Longest winning streak in IPL history — 14 consecutive wins',
      'Narine: mystery spinner to explosive opener in 2024 — scored 109 vs RR',
      'SRK owns the team — Bollywood royalty meets cricket',
      'Gambhir bought for Rs 14.9 Cr in 2011 — led to 2 titles',
      'KKR crushed SRH in 2024 final with 57 balls to spare — most dominant final win',
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
    history: `Delhi Capitals — the cursed franchise. Or are they? Originally "Delhi Daredevils," this team has been IPL's biggest underachiever. The capital city of India, all the talent, all the money, zero trophies.\n\nBut the drama! In 2008-2009, they topped the league and looked unstoppable with Sehwag and Gambhir. Then both left. From 2013-2018, DC (then Daredevils) finished bottom half SIX consecutive seasons. They went through 7 captains in 8 years. Fans joked that Delhi was where IPL careers went to die.\n\nIn 2019, new owners JSW rebranded to "Delhi Capitals" and brought in Ricky Ponting as coach. The transformation was real. Shreyas Iyer's calm captaincy, young Rishabh Pant's fireworks, and Shaw's flair took them to their FIRST EVER IPL final in 2020 (Dubai).\n\nThen Rishabh Pant survived a horrific car crash in December 2022. His comeback to cricket — and eventually being bought by LSG for Rs 27 Cr (IPL record) — was the most emotional story in cricket. DC lost their biggest asset but gained India's goodwill.\n\nThe franchise signed David Warner, KL Rahul, Kuldeep Yadav, Axar Patel — building patiently. Delhi's time will come. The question isn't if, it's when.\n\nArun Jaitley Stadium on a warm Delhi evening, the passionate North Indian crowd — when DC clicks, they're electric.`,
    history_hi: `दिल्ली कैपिटल्स — IPL की सबसे बड़ी अंडरअचीवर। भारत की राजधानी, सारा पैसा, सारा टैलेंट — लेकिन खिताब? शून्य। 2008-09 में टॉप किया, फिर 2013-18 तक 6 साल लगातार नीचे। 7 कप्तान 8 साल में! 2019 में "कैपिटल्स" बने, Ponting कोच आए, Shreyas Iyer ने कमान संभाली और 2020 में पहला फाइनल खेला! Rishabh Pant की कार दुर्घटना (2022) के बाद वापसी — IPL की सबसे इमोशनल कहानी। दिल्ली का वक्त आएगा — सवाल ये है कि कब, ये नहीं कि आएगा या नहीं।`,
    fun_facts: [
      'Originally "Delhi Daredevils" — rebranded 2019 to "Capitals"',
      'First-ever final in 2020 — took 12 years!',
      '7 different captains in 8 years (2011-2018) — IPL record!',
      'Rishabh Pant: DC star to Rs 27 Cr LSG buy after car crash comeback',
      'Sehwag & Gambhir dominated 2008-2009 then both left',
      'Ricky Ponting: Australian legend coaching Delhi — brought professionalism',
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
    history: `Punjab Kings — IPL's most heartbreaking franchise. The talent? World-class. The results? Pain.\n\nOriginally "Kings XI Punjab," they were competitive from Day 1. In 2008, they lost their first two games but won 9 of the next 10, with Kumar Sangakkara's 94* becoming legendary. In 2014, they TOPPED the league table under George Bailey, powered by Glenn Maxwell's fireworks and David Miller's finishing. But they lost the final to KKR. That's peak PBKS — dominate the league, choke when it matters.\n\nChris Gayle's era at Punjab was pure box office. His fastest IPL century (30 balls) came in a PBKS jersey. KL Rahul scored 3 consecutive Orange Caps (well, he came close each year). Every year, fans said "this is our year." Every year, heartbreak.\n\nThe franchise rebranded to "Punjab Kings" in 2021 — new name, same old luck. They went through captains like tissue paper: Yuvraj, Sehwag, Bailey, Maxwell, Murali Vijay, Rahul, Mayank, Dhawan, Shreyas Iyer.\n\nBut 2025? PBKS finally had their moment. They TOPPED the league, Shreyas Iyer scored 604 runs, Arshdeep Singh took 21 wickets. They reached the FINAL against RCB at Wankhede... and lost by 6 runs. AGAIN. The Universe Boss legacy, the Sadda Punjab spirit, Preity Zinta's passionate screams from the stands — PBKS is cricket's ultimate "what if" franchise.\n\nMohali's Bhangra beats, dhol drums, and Punjabi passion make every PBKS game a festival. Zero trophies, infinite entertainment.`,
    history_hi: `पंजाब किंग्स — IPL की सबसे दर्दनाक टीम। टैलेंट वर्ल्ड-क्लास, रिज़ल्ट? दर्द। 2014 में लीग टॉप किया, फाइनल हारे। गेल की सबसे तेज IPL सेंचुरी PBKS की जर्सी में आई। KL राहुल ने ऑरेंज कैप जीती। हर साल बोलते "इस बार हमारा है" — हर बार दिल टूटता। 2021 में Kings XI से Punjab Kings बने — नया नाम, वही किस्मत। 2025 में लीग टॉप किया, Shreyas Iyer 604 रन, Arshdeep 21 विकेट — फिर फाइनल में RCB से 6 रन से हारे! प्रीति जिंटा की चीखें, मोहाली का भांगड़ा — PBKS = "what if" franchise।`,
    fun_facts: [
      'IPL 2025 runner-up — lost final to RCB by 6 runs (SO CLOSE)',
      'Originally Kings XI Punjab — rebranded 2021',
      'Gayle scored fastest IPL century ever (30 balls) in PBKS colors',
      'Topped league in 2014 AND 2025 — lost both times in knockouts!',
      'Most captains in IPL history — lost count!',
      'Preity Zinta in the stands is more entertaining than the cricket',
      'Arshdeep Singh: PBKS product who became India death-bowling specialist',
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
    history: `Sunrisers Hyderabad rose from the ashes of the disgraced Deccan Chargers like a phoenix. Born in 2013, SRH was handed the Hyderabad franchise after DC was terminated for financial irregularities. Nobody expected them to succeed this quickly.\n\nIn just their 4th season (2016), David Warner led SRH to their maiden IPL title, beating RCB by 8 runs in a thrilling final. Warner scored 69, Bhuvneshwar Kumar's death bowling (14 runs in overs 18 and 20) sealed it despite RCB being 145/1 after 10 overs. The Orange Army was born.\n\nSRH became synonymous with elite bowling — Bhuvneshwar, Rashid Khan, and later Umran Malik terrorized batting lineups. But 2024 changed everything. SRH went from bowling-first to BATTING MONSTERS.\n\nTravis Head and Abhishek Sharma opening. Heinrich Klaasen in the middle. SRH scored 287/3 against RCB — the highest team total in IPL history. Then 286/6 in 2025. Then 278/3. SRH now owns the TOP THREE highest totals in IPL history. Let that sink in.\n\nKlaasen's 105* off 39 balls against KKR in 2025 (joint-3rd fastest IPL century), Abhishek Sharma's 141 against PBKS — SRH redefined what's possible in T20 batting.\n\nThey reached the 2024 final (lost to KKR) and have been the most entertaining team to watch. Pat Cummins brings Australian steel as captain. Rajiv Gandhi International Stadium, with 55,000 seats, turns orange on match days.\n\nFrom the ashes of Deccan Chargers to owning the IPL's most fearsome batting lineup — SRH's transformation is complete.`,
    history_hi: `SRH — राख से उठी फीनिक्स! 2013 में बैन हुई Deccan Chargers की जगह ली। सिर्फ 4 सीजन में 2016 में Warner की कप्तानी में खिताब! Bhuvneshwar की डेथ बॉलिंग फाइनल में जीत की नायक रही। SRH गेंदबाजी की ताकत से जानी जाती थी — लेकिन 2024 में सब बदल गया!\n\nTravis Head, Abhishek Sharma ओपनिंग में, Klaasen बीच में — SRH ने 287/3 बनाया RCB के खिलाफ (IPL का सर्वोच्च स्कोर!)। फिर 286/6, फिर 278/3 — IPL के टॉप 3 स्कोर तीनों SRH के हैं! Klaasen का 39 गेंदों में 105* — IPL का तीसरा सबसे तेज शतक। Abhishek का 141 — SRH ने T20 बल्लेबाजी की परिभाषा बदल दी। Deccan Chargers की राख से IPL की सबसे खतरनाक बैटिंग लाइनअप तक — SRH की कहानी अद्भुत है।`,
    fun_facts: [
      'Owns TOP 3 highest team totals in IPL: 287/3, 286/6, 278/3!',
      'Won title in just 4th season (2016) — Warner 69 in final',
      'Replaced banned Deccan Chargers in 2013',
      'Warner won 3 Orange Caps for SRH (2015, 2017, 2019)',
      'Klaasen 105* off 39 balls — joint 3rd fastest IPL century (2025)',
      'Abhishek Sharma 141 — 3rd highest individual score in IPL (2025)',
      'From bowling-first to batting monsters in one year (2023 to 2024)',
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
    history: `Rajasthan Royals — the team that wrote the greatest underdog story in sports history.\n\nIPL 2008. The inaugural season. Every team bought superstars at mega auctions. RR? They had the smallest purse. Their biggest "star" was a 38-year-old Australian leg-spinner named Shane Warne. Experts laughed. Nobody gave them a chance.\n\nBut Warne wasn't just a bowler. He was a genius. He took unknown Indian players — Swapnil Asnodkar, Ravindra Jadeja (19 years old), Yusuf Pathan, Sohail Tanvir — and turned them into IPL heroes. RR topped the league and won the inaugural title, beating CSK by 3 wickets in the final.\n\nWarne's captaincy in IPL 2008 is considered the greatest tactical masterclass in T20 history. He proved cricket intelligence beats money.\n\nThen came the darkness. The 2013 spot-fixing scandal hit RR hard — Sreesanth, Ankeet Chavan, and Ajit Chandila were arrested. RR co-owner Raj Kundra was banned for life for betting. The team was suspended for 2 years (2016-2017).\n\nRR returned and rebuilt. In 2022, under Sanju Samson, they reached the final powered by Jos Buttler's historic 4 centuries in a season (863 runs, Orange Cap). They lost the final to GT but proved they could compete.\n\nYashasvi Jaiswal's emergence — from selling panipuri on Mumbai streets to scoring the fastest IPL fifty (13 balls) — embodies the RR spirit. Kumar Sangakkara brought Sri Lankan wisdom as coach.\n\nThe Pink City's "Halla Bol" (Attack!) spirit, Warne's legacy, and RR's moneyball philosophy make them IPL's most romantic franchise.`,
    history_hi: `RR — खेल इतिहास की सबसे बड़ी अंडरडॉग कहानी! IPL 2008 — सबसे कम बजट, कोई बड़ा सितारा नहीं। बस 38 साल का ऑस्ट्रेलियन Shane Warne। सब हंसे, लेकिन Warne ने अनजान खिलाड़ियों — Asnodkar, Jadeja (19 साल), Yusuf Pathan — को हीरो बना दिया। लीग टॉप किया, CSK को हराकर पहला IPL जीता!\n\n2013 में स्पॉट-फिक्सिंग स्कैंडल — Sreesanth गिरफ्तार, Kundra बैन। 2 साल का प्रतिबंध। फिर वापसी। 2022 में Sanju Samson की कप्तानी में Buttler ने 4 शतक लगाए (863 रन!) — फाइनल तक पहुंचे लेकिन GT से हारे। यशस्वी जायसवाल — पानीपुरी बेचने से IPL की सबसे तेज फिफ्टी (13 गेंद) तक — RR spirit है। Halla Bol!`,
    fun_facts: [
      'Won inaugural IPL 2008 — smallest budget, biggest heart',
      'Warne captaincy 2008 = greatest tactical IPL masterclass ever',
      'Spot-fixing scandal: 3 RR players arrested in 2013',
      'Banned 2 years (2016-2017) — same as CSK',
      'Buttler scored 4 centuries in 2022 — 863 runs, Orange Cap',
      'Jaiswal: panipuri seller to fastest IPL fifty (13 balls)',
      'Discovered Jadeja at age 19 — went on to play 255 IPL matches',
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
    history: `Gujarat Titans — the franchise that rewrote the rulebook.\n\nWhen GT entered IPL in 2022, everyone expected a "new team tax" — struggles, learning curve, bottom-half finishes. Instead, Hardik Pandya's GT won the whole thing. In their FIRST season. The only franchise to win IPL in their debut year since RR in 2008.\n\nPlaying at the Narendra Modi Stadium — the world's largest cricket stadium with 132,000 seats — GT made Ahmedabad a fortress. Their strategy was revolutionary: pick "smart" players over "star" players. Hardik's captaincy was instinctive, Rashid Khan's leg-spin was unplayable, David Miller became the greatest finisher in the game.\n\nGT reached the 2023 final too (lost to CSK in a DLS-affected game), proving their debut season wasn't a fluke.\n\nIn 2025, Shubman Gill led the team to playoffs. Sai Sudharsan scored 759 runs (Orange Cap), Prasidh Krishna took 25 wickets (Purple Cap) — BOTH awards going to GT players! They chased 205 without losing a wicket against DC — the first 200+ chase for no loss in IPL history.\n\nFrom their "Aava De" (Bring it on!) battle cry to the stunning 132,000-capacity stadium glowing on match nights, GT has established themselves as a permanent force. They represent new India — ambitious, fearless, and refusing to wait in line.`,
    history_hi: `GT — जिसने नियम बदल दिए! 2022 में IPL में आए और पहले ही सीजन में खिताब जीत लिया! RR (2008) के बाद ऐसा करने वाली पहली टीम। 132,000 सीटों वाला नरेंद्र मोदी स्टेडियम — दुनिया का सबसे बड़ा — GT का किला। Hardik की कप्तानी, Rashid की स्पिन, Miller की फिनिशिंग — "स्टार" नहीं, "स्मार्ट" खिलाड़ी चुने!\n\n2023 में भी फाइनल (CSK से हारे)। 2025 में Sai Sudharsan ने Orange Cap (759 रन) और Prasidh Krishna ने Purple Cap (25 विकेट) जीती — दोनों GT से! 205 रन बिना विकेट खोए चेज किए DC के खिलाफ — IPL इतिहास में पहली बार! "Aava De" — GT = fearless cricket।`,
    fun_facts: [
      'Won IPL in debut season 2022 — UNPRECEDENTED since RR 2008!',
      'Narendra Modi Stadium: 132,000 capacity — world\'s largest cricket ground',
      'Both Orange Cap AND Purple Cap won by GT players in 2025!',
      'Chased 205 without losing a wicket vs DC — IPL first!',
      'Reached final in first 2 seasons — debut + 2nd year',
      'Rashid Khan chose GT over SRH — best transfer in IPL history',
      '"Aava De" = "Bring it on" in Gujarati — perfect motto',
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
    history: `Lucknow Super Giants — the new kid with serious ambitions.\n\nLSG entered IPL in 2022 alongside GT, bought by the RPSG Group (Sanjiv Goenka) for a staggering Rs 7,090 Cr — the most expensive franchise bid ever. Former Rising Pune Supergiant owner, Goenka brought experience and ruthless ambition.\n\nKL Rahul was the first pick, followed by Quinton de Kock, Marcus Stoinis, and Ravi Bishnoi. Under coach Justin Langer (former Australian head coach), LSG qualified for playoffs in their debut season (2022) AND second season (2023) — matching GT's consistency.\n\nBut then came the drama. After a below-par 2024, Sanjiv Goenka was caught on camera visibly angry with KL Rahul after a loss. The franchise-captain relationship deteriorated. Rahul left for DC.\n\nThe 2025 mega auction saw LSG make the biggest splash — Rs 27 Cr for Rishabh Pant, the most expensive player in IPL history. The comeback kid from a near-fatal car crash became LSG's centrepiece. Nicholas Pooran's power hitting added Caribbean firepower.\n\nEkana Cricket Stadium in Lucknow has become a genuine fortress. UP cricket fans — hungry for a team of their own — have embraced LSG with full passion. Zero trophies so far, but the foundation is strong.\n\nLSG represents new India's hunger — they don't just want to compete, they want to dominate. With Pant leading and Goenka's investment, it's a matter of time.`,
    history_hi: `LSG — serious ambitions वाला नया खिलाड़ी। Rs 7,090 Cr की बोली — IPL इतिहास की सबसे महंगी franchise! KL Rahul पहली पसंद, Justin Langer कोच। पहले दो सीजन में प्लेऑफ — GT जैसी consistency!\n\nफिर ड्रामा — 2024 में Sanjiv Goenka कैमरे पर KL Rahul पर गुस्सा हुए। Rahul चले गए DC। 2025 में Rs 27 Cr में Rishabh Pant — IPL इतिहास का सबसे महंगा खिलाड़ी! कार दुर्घटना से वापसी के बाद Pant LSG के हीरो। Lucknow के Ekana Stadium में UP cricket fans का जोश अलग ही है। खिताब अभी नहीं, लेकिन foundation मजबूत है।`,
    fun_facts: [
      'Rs 7,090 Cr franchise fee — most expensive IPL team bid ever!',
      'Bought Rishabh Pant for Rs 27 Cr — all-time IPL record',
      'Qualified for playoffs in debut (2022) AND second season (2023)',
      'Goenka-KL Rahul public spat after 2024 loss went viral',
      'Owner also owned Rising Pune Supergiant (2016-17)',
      'Ekana Stadium — one of India\'s newest and most modern grounds',
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
