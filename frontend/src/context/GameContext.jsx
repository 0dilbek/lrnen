import { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import api from '../api';

// XP hisoblash: har yakunlangan dars = 100 XP + score ballari
function calcXP(progress) {
  return progress.reduce((sum, p) => {
    if (p.status === 'completed') return sum + 100 + (p.score || 0);
    return sum + Math.round((p.score || 0) * 0.3);
  }, 0);
}

// Badge'lar
const BADGE_DEFS = [
  { id: 'first_lesson', emoji: '🌱', label: 'Birinchi qadam',    desc: 'Birinchi darsni boshladi',      check: (p) => p.length >= 1 },
  { id: 'first_done',   emoji: '⭐', label: 'Birinchi g\'alaba', desc: 'Birinchi darsni yakunladi',     check: (p) => p.filter(x => x.status==='completed').length >= 1 },
  { id: 'three_done',   emoji: '🔥', label: 'Qizg\'in o\'quvchi',desc: '3 ta darsni yakunladi',         check: (p) => p.filter(x => x.status==='completed').length >= 3 },
  { id: 'five_done',    emoji: '🏅', label: 'Chempion',           desc: '5 ta darsni yakunladi',         check: (p) => p.filter(x => x.status==='completed').length >= 5 },
  { id: 'perfect',      emoji: '💯', label: 'Mukammal',           desc: '100% ball oldi',                check: (p) => p.some(x => x.score === 100) },
  { id: 'xp500',        emoji: '🏆', label: 'XP ustasi',          desc: '500 XP to\'pladi',              check: (p) => calcXP(p) >= 500 },
];

// Streak: localStorage'da saqlash
function updateStreak(username) {
  const key = `streak_${username}`;
  const today = new Date().toDateString();
  const raw = localStorage.getItem(key);
  if (!raw) {
    const data = { count: 1, last: today };
    localStorage.setItem(key, JSON.stringify(data));
    return 1;
  }
  const data = JSON.parse(raw);
  if (data.last === today) return data.count;
  const yesterday = new Date(Date.now() - 86400000).toDateString();
  const count = data.last === yesterday ? data.count + 1 : 1;
  localStorage.setItem(key, JSON.stringify({ count, last: today }));
  return count;
}

function getStreak(username) {
  const raw = localStorage.getItem(`streak_${username}`);
  if (!raw) return 0;
  const data = JSON.parse(raw);
  const today = new Date().toDateString();
  const yesterday = new Date(Date.now() - 86400000).toDateString();
  if (data.last === today || data.last === yesterday) return data.count;
  return 0;
}

const GameContext = createContext(null);

export function GameProvider({ children }) {
  const { user } = useAuth();
  const [xp, setXP]         = useState(0);
  const [badges, setBadges] = useState([]);
  const [streak, setStreak] = useState(0);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (!user || user.role === 'admin') return;
    api.get('/courses/progress/').then(({ data }) => {
      const earnedXP    = calcXP(data);
      const earnedBadges = BADGE_DEFS.filter(b => b.check(data));
      const currentStreak = updateStreak(user.username);
      setXP(earnedXP);
      setBadges(earnedBadges);
      setStreak(currentStreak);
      setLoaded(true);
    }).catch(() => setLoaded(true));
  }, [user]);

  return (
    <GameContext.Provider value={{ xp, badges, streak, loaded, BADGE_DEFS }}>
      {children}
    </GameContext.Provider>
  );
}

export const useGame = () => useContext(GameContext);
export { calcXP, BADGE_DEFS, getStreak };
