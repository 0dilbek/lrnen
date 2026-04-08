import { useState, useEffect } from 'react';
import api from '../api';
import { useAuth } from '../context/AuthContext';
import { useGame } from '../context/GameContext';
import { Loader2, Trophy, Zap, Flame } from 'lucide-react';

const RANK_STYLE = [
  { bg: 'from-yellow-400 to-orange-400', text: 'text-yellow-800', label: '🥇' },
  { bg: 'from-gray-300 to-gray-400',     text: 'text-gray-700',   label: '🥈' },
  { bg: 'from-orange-300 to-amber-400',  text: 'text-orange-800', label: '🥉' },
];

export default function LeaderboardPage() {
  const { user } = useAuth();
  const { xp: myXP } = useGame();
  const [board, setBoard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/auth/leaderboard/').then(({ data }) => setBoard(data)).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="animate-spin text-blue-600" size={40} />
      </div>
    );
  }

  const myEntry = board.find(b => b.username === user?.username);
  const top3 = board.slice(0, 3);
  const rest = board.slice(3);

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <div className="text-5xl mb-3">🏆</div>
        <h1 className="text-2xl font-extrabold text-gray-900">Reyting jadvali</h1>
        <p className="text-gray-500 mt-1">Eng ko'p XP to'plagan o'quvchilar</p>
      </div>

      {/* Podium — top 3 */}
      {top3.length > 0 && (
        <div className="flex items-end justify-center gap-3 mb-8">
          {/* 2nd */}
          {top3[1] && <PodiumCard entry={top3[1]} rank={2} isMe={top3[1].username === user?.username} />}
          {/* 1st */}
          {top3[0] && <PodiumCard entry={top3[0]} rank={1} isMe={top3[0].username === user?.username} tall />}
          {/* 3rd */}
          {top3[2] && <PodiumCard entry={top3[2]} rank={3} isMe={top3[2].username === user?.username} />}
        </div>
      )}

      {/* My position highlight (agar top3 da bo'lmasa) */}
      {myEntry && myEntry.rank > 3 && (
        <div className="bg-gradient-to-r from-blue-50 to-violet-50 border-2 border-blue-300 rounded-2xl px-5 py-4 mb-6 flex items-center gap-4">
          <span className="text-2xl font-extrabold text-blue-600">#{myEntry.rank}</span>
          <div className="flex-1">
            <p className="font-bold text-gray-900">Siz 👤</p>
            <p className="text-sm text-gray-500">@{myEntry.username}</p>
          </div>
          <div className="text-right">
            <p className="font-extrabold text-violet-700 flex items-center gap-1"><Zap size={14} />{myXP} XP</p>
            <p className="text-xs text-gray-400">{myEntry.completed} dars</p>
          </div>
        </div>
      )}

      {/* Rest of the list */}
      {rest.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="divide-y divide-gray-50">
            {rest.map((entry) => {
              const isMe = entry.username === user?.username;
              return (
                <div
                  key={entry.id}
                  className={`px-5 py-4 flex items-center gap-4 ${isMe ? 'bg-blue-50' : 'hover:bg-gray-50'} transition`}
                >
                  <span className={`w-8 text-center font-extrabold text-lg ${isMe ? 'text-blue-600' : 'text-gray-400'}`}>
                    #{entry.rank}
                  </span>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white text-sm shrink-0 ${isMe ? 'bg-gradient-to-br from-blue-500 to-violet-600' : 'bg-gradient-to-br from-gray-400 to-gray-500'}`}>
                    {(entry.full_name || entry.username)[0].toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`font-semibold truncate ${isMe ? 'text-blue-700' : 'text-gray-900'}`}>
                      {entry.full_name || entry.username} {isMe && '👤'}
                    </p>
                    <p className="text-xs text-gray-400">@{entry.username}</p>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="font-extrabold text-violet-700 flex items-center gap-1 justify-end">
                      <Zap size={12} />{entry.xp}
                    </p>
                    <p className="text-xs text-gray-400">{entry.completed} dars</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {board.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <Trophy size={48} className="mx-auto mb-3 opacity-30" />
          <p>Hali reyting mavjud emas</p>
        </div>
      )}
    </div>
  );
}

function PodiumCard({ entry, rank, isMe, tall }) {
  const style = RANK_STYLE[rank - 1];
  return (
    <div className={`flex flex-col items-center ${tall ? 'order-2' : rank === 2 ? 'order-1' : 'order-3'}`}>
      <div className={`w-14 h-14 rounded-full bg-gradient-to-br ${style.bg} flex items-center justify-center font-extrabold text-xl text-white shadow-lg mb-2 ${isMe ? 'ring-4 ring-blue-400' : ''}`}>
        {(entry.full_name || entry.username)[0].toUpperCase()}
      </div>
      <p className="text-xs font-bold text-gray-700 text-center max-w-[72px] truncate">
        {entry.full_name?.split(' ')[0] || entry.username}
      </p>
      <div className={`mt-2 flex flex-col items-center justify-end bg-gradient-to-t ${style.bg} rounded-t-xl w-20 ${tall ? 'h-28' : 'h-20'} shadow-md`}>
        <span className="text-2xl mb-1">{style.label}</span>
        <span className="text-xs font-bold text-white/90 pb-2 flex items-center gap-0.5">
          <Zap size={10} />{entry.xp}
        </span>
      </div>
    </div>
  );
}
