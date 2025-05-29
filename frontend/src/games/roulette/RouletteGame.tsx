import React, { useState } from 'react';

const betTypes = [
  { type: 'red', name: '紅色' },
  { type: 'black', name: '黑色' },
  { type: 'even', name: '偶數' },
  { type: 'odd', name: '奇數' },
  { type: 'straight', name: '直注' }
];

const RouletteGame: React.FC = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [betType, setBetType] = useState('red');
  const [amount, setAmount] = useState(100);
  const [result, setResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // 建立會話
  const createSession = async () => {
    setLoading(true);
    const res = await fetch('/api/v1/games/roulette/create-session', { method: 'POST' });
    const data = await res.json();
    setSessionId(data.session_id);
    setLoading(false);
  };

  // 下注
  const placeBet = async () => {
    if (!sessionId) return;
    setLoading(true);
    await fetch(`/api/v1/games/roulette/${sessionId}/bet?bet_type=${betType}&amount=${amount}`, { method: 'POST' });
    setLoading(false);
  };

  // 旋轉
  const spin = async () => {
    if (!sessionId) return;
    setLoading(true);
    const res = await fetch(`/api/v1/games/roulette/${sessionId}/spin`, { method: 'POST' });
    const data = await res.json();
    setResult(data);
    setLoading(false);
    fetchHistory();
  };

  // 查歷史
  const fetchHistory = async () => {
    const res = await fetch('/api/v1/games/roulette/history');
    const data = await res.json();
    setHistory(data.history || []);
  };

  return (
    <div style={{ padding: 32 }}>
      <h2 style={{ fontSize: 28, fontWeight: 'bold', marginBottom: 16 }}>🎲 歐式輪盤</h2>
      {!sessionId ? (
        <button onClick={createSession} disabled={loading} style={{ padding: 12, fontSize: 18 }}>
          {loading ? '建立中...' : '建立遊戲會話'}
        </button>
      ) : (
        <>
          <div style={{ marginBottom: 16 }}>
            <label>下注類型：</label>
            <select value={betType} onChange={e => setBetType(e.target.value)}>
              {betTypes.map(b => <option key={b.type} value={b.type}>{b.name}</option>)}
            </select>
            <label style={{ marginLeft: 16 }}>金額：</label>
            <input type="number" value={amount} min={1} max={10000} onChange={e => setAmount(Number(e.target.value))} />
            <button onClick={placeBet} disabled={loading} style={{ marginLeft: 16 }}>
              {loading ? '下注中...' : '下注'}
            </button>
          </div>
          <button onClick={spin} disabled={loading} style={{ padding: 12, fontSize: 18 }}>
            {loading ? '旋轉中...' : '旋轉輪盤'}
          </button>
          {result && (
            <div style={{ marginTop: 24, background: '#222', color: '#fff', padding: 16, borderRadius: 8 }}>
              <div>結果號碼：<b>{result.result_number}</b>，顏色：<b>{result.color}</b></div>
              <div>贏家：{result.winners && result.winners.length > 0 ? result.winners.map((w: any) => `${w.user_id} (${w.bet_type}) +${w.win_amount}`).join(', ') : '無'}</div>
              <div>總派彩：{result.total_payout}</div>
            </div>
          )}
          <div style={{ marginTop: 32 }}>
            <h3>歷史紀錄</h3>
            <ul>
              {history.map((h, i) => (
                <li key={i}>號碼: {h.result_number}, 顏色: {h.color}, 派彩: {h.total_payout}</li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
};

export default RouletteGame; 