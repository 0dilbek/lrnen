import { useState, useEffect } from 'react';
import api from '../api';
import { useAuth } from '../context/AuthContext';
import { useGame } from '../context/GameContext';
import { Loader2, Trophy, Zap } from 'lucide-react';

const RANK_STYLE = [
  { bg: 'from-yellow-400 to-orange-400', label: '🥇' },
  { bg: 'from-slate-300 to-slate-400',   label: '🥈' },
  { bg: 'from-orange-300 to-amber-400',  label: '🥉' },
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
        <Loader2 className="animate-spin text-indigo-400" size={40} />
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
        <h1 className="text-2xl font-extrabold stu-title">Reyting jadvali</h1>
        <p className="stu-muted mt-1">Eng ko'p XP to'plagan o'quvchilar</p>
      </div>

      {top3.length > 0 && (
        <div className="flex items-end justify-center gap-3 mb-8">
          {top3[1] && <PodiumCard entry={top3[1]} rank={2} isMe={top3[1].username === user?.username} />}
          {top3[0] && <PodiumCard entry={top3[0]} rank={1} isMe={top3[0].username === user?.username} tall />}
          {top3[2] && <PodiumCard entry={top3[2]} rank={3} isMe={top3[2].username === user?.username} />}
        </div>
      )}

      {myEntry && myEntry.rank > 3 && (
        <div className="bg-indigo-500/10 border-2 border-indigo-500/30 rounded-2xl px-5 py-4 mb-6 flex items-center gap-4">
          <span className="text-2xl font-extrabold text-indigo-400">#{myEntry.rank}</span>
          <div className="flex-1">
            <p className="font-bold stu-title">Siz 👤</p>
            <p className="text-sm text-slate-400">@{myEntry.username}</p>
          </div>
          <div className="text-right">
            <p className="font-extrabold text-violet-400 flex items-center gap-1"><Zap size={14} />{myXP} XP</p>
            <p className="text-xs text-slate-500">{myEntry.completed} dars</p>
          </div>
        </div>
      )}

      {rest.length > 0 && (
        <div className="student-card overflow-hidden">
          <div className="divide-y divide-border">
            {rest.map((entry) => {
              const isMe = entry.username === user?.username;
              return (
                <div
                  key={entry.id}
                  className={`px-5 py-4 flex items-center gap-4 ${isMe ? 'bg-indigo-500/10' : 'hover:bg-surface-200/40'} transition`}
                >
                  <span className={`w-8 text-center font-extrabold text-lg ${isMe ? 'text-indigo-400' : 'text-slate-500'}`}>
                    #{entry.rank}
                  </span>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white text-sm shrink-0 ${isMe ? 'bg-gradient-to-br from-indigo-500 to-violet-600' : 'bg-gradient-to-br from-slate-500 to-slate-600'}`}>
                    {(entry.full_name || entry.username)[0].toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`font-semibold truncate ${isMe ? 'text-indigo-600' : 'stu-title'}`}>
                      {entry.full_name || entry.username} {isMe && '👤'}
                    </p>
                    <p className="text-xs text-slate-500">@{entry.username}</p>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="font-extrabold text-violet-400 flex items-center gap-1 justify-end">
                      <Zap size={12} />{entry.xp}
                    </p>
                    <p className="text-xs text-slate-500">{entry.completed} dars</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {board.length === 0 && (
        <div className="text-center py-16 text-slate-500">
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
      <div className={`w-14 h-14 rounded-full bg-gradient-to-br ${style.bg} flex items-center justify-center font-extrabold text-xl text-white shadow-lg mb-2 ${isMe ? 'ring-4 ring-indigo-400' : ''}`}>
        {(entry.full_name || entry.username)[0].toUpperCase()}
      </div>
      <p className="text-xs font-bold stu-muted text-center max-w-[72px] truncate">
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