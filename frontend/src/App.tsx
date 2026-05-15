import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  applyEdgeChanges, 
  applyNodeChanges,
  MarkerType,
  Handle,
  Position,
  useReactFlow,
  ReactFlowProvider
} from 'reactflow';
import type { 
  Node, 
  Edge, 
  OnNodesChange, 
  OnEdgesChange 
} from 'reactflow';
import 'reactflow/dist/style.css';
import * as dagre from '@dagrejs/dagre';
import './index.css';

const worker = new Worker(`${import.meta.env.BASE_URL}pyodide-worker.js`);

const parseSqlWithWorker = (sql: string, dialect: string): Promise<any> => {
  return new Promise((resolve, reject) => {
    const id = Math.random().toString(36).substring(7);
    const handleMessage = (event: MessageEvent) => {
      if (event.data.id === id) {
        worker.removeEventListener('message', handleMessage);
        if (event.data.error) reject(new Error(event.data.error));
        else resolve(event.data.result);
      }
    };
    worker.addEventListener('message', handleMessage);
    worker.postMessage({ id, sql, dialect });
  });
};

/**
 * [GEN-6: Absolute Symmetry & Viewport Precision]
 * 1. ISSUE: "Right side too wide", "Shifted to Top/Left", "Overflowing Right/Bottom".
 * 2. FIX: Manual pixel mapping for children. Eliminating Dagre's internal child layout.
 * 3. SYMMETRY: GROUP_W = NODE_W + (PAD_X * 2). Child X = PAD_X. Unbeatable 1:1 symmetry.
 */

// ---------------------------------------------------------
// 1. Sophisticated Components (Fixed Widths)
// ---------------------------------------------------------

const NODE_WIDTH = 220;
const NODE_HEIGHT = 46;

const TableGroupNode = ({ data }: any) => (
  <div style={{ 
    width: '100%', height: '100%', 
    backgroundColor: '#ffffff', border: data.highlighted ? '2px solid #3b82f6' : '1.5px solid #e2e8f0', borderRadius: '16px',
    overflow: 'hidden', boxShadow: data.highlighted ? '0 0 10px rgba(59, 130, 246, 0.5)' : '0 10px 30px -5px rgba(0, 0, 0, 0.05)',
    display: 'flex', flexDirection: 'column', transition: 'all 0.2s ease'
  }}>
    <div style={{ 
      padding: '10px 16px', backgroundColor: data.highlighted ? '#eff6ff' : '#f8fafc', borderBottom: data.highlighted ? '1.2px solid #3b82f6' : '1.2px solid #e2e8f0',
      display: 'flex', alignItems: 'center', gap: '8px', transition: 'all 0.2s ease'
    }}>
      <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: data.highlighted ? '#3b82f6' : '#6366f1', transition: 'all 0.2s ease' }} />
      <span style={{ fontSize: '11px', fontWeight: '800', color: data.highlighted ? '#1e3a8a' : '#475569', textTransform: 'uppercase', letterSpacing: '0.05em', transition: 'all 0.2s ease' }}>
        {data.label}
      </span>
    </div>
  </div>
);

const ColumnNode = ({ data }: any) => {
  const themes: Record<string, any> = {
    join_key: { color: '#f59e0b', bg: '#fffbeb', icon: '🔑' },
    final_column: { color: '#ef4444', bg: '#fef2f2', icon: '🎯' },
    data_source: { color: '#10b981', bg: '#f0fdf4', icon: '🔌' },
    source_column: { color: '#6366f1', bg: '#eef2ff', icon: '📄' }
  };
  const theme = themes[data.type] || themes.source_column;

  return (
    <div style={{ 
      width: `${NODE_WIDTH}px`, height: `${NODE_HEIGHT}px`, borderRadius: '10px', backgroundColor: '#ffffff',
      border: data.highlighted ? '2px solid #3b82f6' : '1.2px solid #e2e8f0', display: 'flex', alignItems: 'center',
      padding: '0 14px', gap: '10px', boxShadow: data.highlighted ? '0 0 10px rgba(59, 130, 246, 0.5)' : '0 1px 3px rgba(0,0,0,0.02)',
      position: 'relative', transition: 'all 0.2s ease'
    }}>
      <div style={{ width: '28px', height: '28px', borderRadius: '8px', backgroundColor: theme.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', transition: 'all 0.2s ease' }}>
        {theme.icon}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: '12px', fontWeight: '600', color: '#1e293b', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', transition: 'all 0.2s ease' }}>
          {data.label}
        </div>
      </div>
      <Handle type="target" position={Position.Left} style={{ left: '-6px', background: theme.color, width: '10px', height: '10px', border: '2.5px solid white' }} />
      <Handle type="source" position={Position.Right} style={{ right: '-6px', background: theme.color, width: '10px', height: '10px', border: '2.5px solid white' }} />
    </div>
  );
};

const nodeTypes = {
  group: TableGroupNode,
  source_column: ColumnNode,
  final_column: ColumnNode,
  data_source: ColumnNode,
  join_key: ColumnNode
};

// ---------------------------------------------------------
// 2. Absolute Symmetry Layout Engine
// ---------------------------------------------------------

const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  const dagreGraph = new (dagre as any).graphlib.Graph(); // Note: Not using compound mode for primary layout
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  // PRECISION CONSTANTS
  const GAP_V = 14;   
  const PAD_X = 20;   // Symmetric side padding
  const PAD_T = 52;   // Header height
  const PAD_B = 20;   // Bottom buffer
  const GROUP_W = NODE_WIDTH + (PAD_X * 2); // Perfectly balanced width

  const groupChildren: Record<string, string[]> = {};
  nodes.forEach(n => {
    if (n.parentNode) {
      if (!groupChildren[n.parentNode]) groupChildren[n.parentNode] = [];
      groupChildren[n.parentNode].push(n.id);
    }
  });

  // Setup Dagre only for Group/Independent positioning
  dagreGraph.setGraph({ rankdir: 'LR', nodesep: 60, ranksep: 160, marginx: 0, marginy: 0 });

  // 1. Calculate Group sizes and register
  nodes.forEach((n: any) => {
    if (n.type === 'group') {
      const count = groupChildren[n.id]?.length || 1;
      const height = PAD_T + (count * NODE_HEIGHT) + ((count - 1) * GAP_V) + PAD_B;
      dagreGraph.setNode(n.id, { width: GROUP_W, height });
    } else if (!n.parentNode) {
      dagreGraph.setNode(n.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
    }
  });

  // Use only edges between groups or independent nodes for Dagre
  edges.forEach(e => {
    const srcNode = nodes.find(n => n.id === e.source);
    const tarNode = nodes.find(n => n.id === e.target);
    const src = srcNode?.parentNode || e.source;
    const tar = tarNode?.parentNode || e.target;
    if (src !== tar) dagreGraph.setEdge(src, tar);
  });

  (dagre as any).layout(dagreGraph);

  // 2. Map coordinates with Hard-Coded Symmetry
  const layoutedNodes = nodes.map((n) => {
    const isGroup = n.type === 'group';
    
    if (isGroup) {
      const d = dagreGraph.node(n.id);
      return { 
        ...n, 
        position: { x: d.x - d.width/2, y: d.y - d.height/2 }, 
        style: { width: d.width, height: d.height, zIndex: -1 }
      };
    }

    if (n.parentNode) {
      const idx = groupChildren[n.parentNode]?.indexOf(n.id) || 0;
      return { 
        ...n, 
        position: { 
          x: PAD_X, // [ABSOLUTE SYMMETRY] Guaranteed equal spacing on both sides
          y: PAD_T + (idx * (NODE_HEIGHT + GAP_V)) 
        }, 
        style: { zIndex: 10 },
        width: NODE_WIDTH,
        height: NODE_HEIGHT
      };
    }

    // Independent nodes
    const d = dagreGraph.node(n.id);
    return { ...n, position: { x: d.x - d.width/2, y: d.y - d.height/2 }, style: { zIndex: 10 }};
  });

  return { 
    nodes: layoutedNodes, 
    edges: edges.map(e => ({
      ...e, type: 'smoothstep', markerEnd: { type: MarkerType.ArrowClosed, color: '#cbd5e1' },
      style: { strokeWidth: 1.5, stroke: '#cbd5e1' }, animated: false
    }))
  };
};

// ---------------------------------------------------------
// 3. Robust Graph Container
// ---------------------------------------------------------

function LineageGraph({ sql, loading, onResultLoaded }: any) {
  const { fitView } = useReactFlow();
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  const onNodesChange: OnNodesChange = useCallback((c) => setNodes((nds) => applyNodeChanges(c, nds)), []);
  const onEdgesChange: OnEdgesChange = useCallback((c) => setEdges((eds) => applyEdgeChanges(c, eds)), []);

  const handleRun = async () => {
    try {
      const data = await parseSqlWithWorker(sql, 'tsql');
      const { nodes: lNodes, edges: lEdges } = getLayoutedElements(data.nodes, data.edges);
      setNodes(lNodes);
      setEdges(lEdges);
      
      // Multi-stage fitting to combat rendering race conditions
      setTimeout(() => fitView({ padding: 0.2, duration: 200 }), 50);
      setTimeout(() => fitView({ padding: 0.2, duration: 200 }), 150);
    } catch (e) { alert('Visualization failed.'); } finally { onResultLoaded(); }
  };

  useEffect(() => { if (loading) handleRun(); }, [loading]);

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    const up = new Set<string>();
    const down = new Set<string>();
    
    const findUp = (nId: string) => {
      edges.forEach(e => {
        if (e.target === nId && !up.has(e.source)) {
          up.add(e.source);
          findUp(e.source);
        }
      });
    };
    
    const findDown = (nId: string) => {
      edges.forEach(e => {
        if (e.source === nId && !down.has(e.target)) {
          down.add(e.target);
          findDown(e.target);
        }
      });
    };
    
    findUp(node.id);
    findDown(node.id);
    
    const highlightIds = new Set([node.id, ...up, ...down]);

    setNodes(nds => {
      const parentIds = new Set<string>();
      nds.forEach(n => {
        if (highlightIds.has(n.id) && n.parentNode) {
          parentIds.add(n.parentNode);
        }
      });
      return nds.map(n => ({
        ...n,
        data: { ...n.data, highlighted: highlightIds.has(n.id) },
        style: { ...n.style, opacity: (highlightIds.has(n.id) || parentIds.has(n.id)) ? 1 : 0.2 }
      }));
    });

    setEdges(eds => eds.map(e => ({
      ...e,
      style: {
        ...e.style,
        stroke: highlightIds.has(e.source) && highlightIds.has(e.target) ? '#3b82f6' : '#cbd5e1',
        strokeWidth: highlightIds.has(e.source) && highlightIds.has(e.target) ? 2.5 : 1.5,
      },
      markerEnd: { 
        type: MarkerType.ArrowClosed, 
        color: highlightIds.has(e.source) && highlightIds.has(e.target) ? '#3b82f6' : '#cbd5e1' 
      },
      zIndex: highlightIds.has(e.source) && highlightIds.has(e.target) ? 10 : 0
    })));
  }, [edges]);

  const onPaneClick = useCallback(() => {
    setNodes(nds => nds.map(n => ({
      ...n,
      data: { ...n.data, highlighted: false },
      style: { ...n.style, opacity: 1 }
    })));
    setEdges(eds => eds.map(e => ({
      ...e,
      style: { ...e.style, stroke: '#cbd5e1', strokeWidth: 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#cbd5e1' },
      zIndex: 0
    })));
  }, []);

  return (
    <ReactFlow
      nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange}
      onNodeClick={onNodeClick} onPaneClick={onPaneClick}
      nodeTypes={nodeTypes} fitView minZoom={0.01} maxZoom={4}
    >
      <Background color="#cbd5e1" variant="dots" gap={24} />
      <Controls style={{ boxShadow: 'none', border: '1px solid #e2e8f0' }} />
    </ReactFlow>
  );
}

export default function App() {
  const [sql, setSql] = useState('');
  const [loading, setLoading] = useState(false);

  return (
    <ReactFlowProvider>
      <div style={{ width: '100vw', height: '100vh', display: 'flex', background: '#f8fafc', overflow: 'hidden' }}>
        {/* Sidebar: Fixed width to prevent canvas skewing */}
        <aside style={{ width: '460px', borderRight: '1px solid #e2e8f0', background: '#ffffff', display: 'flex', flexDirection: 'column', zIndex: 100, flexShrink: 0 }}>
          <div style={{ padding: '40px', flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '40px' }}>
              <img src="/favicon.png" style={{ width: '32px', height: '32px', objectFit: 'contain' }} alt="Logo" />
              <h1 style={{ fontSize: '20px', fontWeight: '900', color: '#1e293b', margin: 0, letterSpacing: '-0.02em' }}>VDGOPHER for SQL</h1>
            </div>
            
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: '300px' }}>
              <label style={{ fontSize: '11px', fontWeight: '800', color: '#94a3b8', letterSpacing: '0.1em', marginBottom: '12px' }}>SOURCE SQL</label>
              <textarea 
                value={sql} onChange={(e) => setSql(e.target.value)}
                placeholder="Paste your complex SQL query here..."
                style={{ width: '100%', flex: 1, padding: '24px', borderRadius: '16px', border: '1.5px solid #f1f5f9', background: '#fcfcfd', outline: 'none', resize: 'none', fontSize: '13px', fontFamily: '"JetBrains Mono", monospace', lineHeight: '1.6', color: '#334155' }}
              />
            </div>

            <button 
              onClick={() => setLoading(true)} disabled={loading}
              style={{ width: '100%', marginTop: '32px', padding: '20px', borderRadius: '14px', background: '#0f172a', color: 'white', fontWeight: '700', fontSize: '15px', cursor: 'pointer', border: 'none', transition: 'all 0.2s ease' }}
              onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#1e293b')}
              onMouseOut={(e) => (e.currentTarget.style.backgroundColor = '#0f172a')}
            >
              {loading ? 'Analyzing Logic...' : 'Generate Lineage Map'}
            </button>

            <div style={{ marginTop: 'auto', paddingTop: '40px' }}>
              <h3 style={{ fontSize: '11px', fontWeight: '800', color: '#94a3b8', marginBottom: '16px', letterSpacing: '0.1em' }}>LOGIC LEGEND</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', fontWeight: '600', color: '#475569' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '2px', backgroundColor: '#ef4444' }} /> Output
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', fontWeight: '600', color: '#475569' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '2px', backgroundColor: '#f59e0b' }} /> Join Key
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', fontWeight: '600', color: '#475569' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '2px', backgroundColor: '#10b981' }} /> Source
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', fontWeight: '600', color: '#475569' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '2px', backgroundColor: '#6366f1' }} /> Process
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Canvas: Strictly fills flex-1 area */}
        <main style={{ flex: 1, position: 'relative', height: '100%', overflow: 'hidden' }}>
          <LineageGraph sql={sql} loading={loading} onResultLoaded={() => setLoading(false)} />
        </main>
      </div>
    </ReactFlowProvider>
  );
}
