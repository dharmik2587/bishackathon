export default function MarqueeBand() {
  const items = [
    'BIS STANDARDS', 'DIRECT MAPPING', 'BM25 RETRIEVAL', 'LLM QUERY REWRITE',
    'DEEPSEEK POWERED', 'CIVIL ENGINEERING', 'ELECTRICAL', 'MECHANICAL',
    'SUB-SECOND LATENCY', 'RAG ENGINE', 'HIT RATE 66.67%', 'MRR 0.6467',
  ];

  const content = [...items, ...items].map((item, i) => (
    <span key={i} style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '20px',
      paddingRight: '20px',
    }}>
      <span style={{ color: '#00d4aa', fontSize: '8px' }}>◆</span>
      <span>{item}</span>
    </span>
  ));

  return (
    <div style={{
      background: '#041120',
      borderTop: '1px solid #0d2d44',
      borderBottom: '1px solid #0d2d44',
      padding: '14px 0',
      overflow: 'hidden',
    }}>
      <div className="marquee-track" style={{
        fontFamily: 'Space Grotesk, monospace',
        fontSize: '10px',
        fontWeight: 500,
        letterSpacing: '0.25em',
        color: '#3d6680',
        textTransform: 'uppercase',
        display: 'flex',
        whiteSpace: 'nowrap',
      }}>
        {content}
      </div>
    </div>
  );
}
