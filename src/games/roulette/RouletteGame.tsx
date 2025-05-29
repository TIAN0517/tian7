import React from 'react';

const RouletteGame: React.FC = () => (
  <div style={{ padding: 32 }}>
    <h2 style={{ fontSize: 28, fontWeight: 'bold', marginBottom: 16 }}>🎲 歐式輪盤</h2>
    <p style={{ marginBottom: 24 }}>請選擇您的下注類型與金額，點擊「旋轉」開始遊戲！</p>
    {/* 這裡可加3D輪盤、下注區、結果顯示等 */}
    <div style={{ background: '#222', borderRadius: 12, padding: 24, color: '#fff' }}>
      <p>功能開發中...</p>
    </div>
  </div>
);

export default RouletteGame; 