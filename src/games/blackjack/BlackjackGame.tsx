import React from 'react';

const BlackjackGame: React.FC = () => (
  <div style={{ padding: 32 }}>
    <h2 style={{ fontSize: 28, fontWeight: 'bold', marginBottom: 16 }}>🂡 21點</h2>
    <p style={{ marginBottom: 24 }}>請選擇下注金額，點擊「發牌」開始遊戲！</p>
    {/* 這裡可加多手牌、加倍、分牌、結果顯示等 */}
    <div style={{ background: '#222', borderRadius: 12, padding: 24, color: '#fff' }}>
      <p>功能開發中...</p>
    </div>
  </div>
);

export default BlackjackGame; 
