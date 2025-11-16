import { useCallback, useEffect, useState } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  BackgroundVariant,
  Panel,
} from '@xyflow/react';
import type { Connection, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from '@dagrejs/dagre';

import DatabaseNode from './nodes/DatabaseNode';
import type { DatabaseNodeData } from './nodes/DatabaseNode';
import TableNode from './nodes/TableNode';
import type { TableNodeData } from './nodes/TableNode';
import { aiChatbotApi } from '@/api/ai-chatbot';

const nodeTypes = {
  database: DatabaseNode,
  table: TableNode,
};

// Dagre layout configuration
const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 250;
const nodeHeight = 100;

const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  dagreGraph.setGraph({ rankdir: direction, ranksep: 100, nodesep: 50 });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);

    return {
      ...node,
      position: {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
};

type Column = {
  name: string;
  type: string;
  isPrimary?: boolean;
};

interface DatabaseMindMapProps {
  databaseId: number;
  onError?: (error: string) => void;
}

export default function DatabaseMindMap({ databaseId, onError }: DatabaseMindMapProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [loading, setLoading] = useState(true);
  const [layoutDirection, setLayoutDirection] = useState<'TB' | 'LR'>('TB');

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Parse table_info string to extract columns
  const parseTableInfo = (tableInfo: string, tableName: string): Column[] => {
    const columns: Column[] = [];

    // Find the CREATE TABLE statement for this specific table
    const tableRegex = new RegExp(
      `CREATE TABLE (?:IF NOT EXISTS )?["\`]?${tableName}["\`]?\\s*\\(([^;]+)\\)`,
      'is'
    );
    const match = tableInfo.match(tableRegex);

    if (!match) return columns;

    const columnDefinitions = match[1];
    const lines = columnDefinitions.split('\n');

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('PRIMARY KEY') || trimmed.startsWith('FOREIGN KEY') || trimmed.startsWith('CONSTRAINT')) {
        continue;
      }

      // Match column definition: "column_name" TYPE or column_name TYPE
      const columnMatch = trimmed.match(/^["\`]?(\w+)["\`]?\s+(\w+(?:\([^)]+\))?)/);
      if (columnMatch) {
        const [, name, type] = columnMatch;
        const isPrimary = trimmed.toUpperCase().includes('PRIMARY KEY');
        columns.push({ name, type, isPrimary });
      }
    }

    return columns;
  };

  // Fetch database schema and create nodes/edges
  const loadDatabaseSchema = async () => {
    setLoading(true);
    try {
      const data = await aiChatbotApi.exploreDatabase(databaseId);

      // Create database root node
      const databaseNode: Node<DatabaseNodeData> = {
        id: 'db-root',
        type: 'database',
        data: {
          name: data.database.name,
          type: data.database.type,
          tableCount: data.tables.length,
        },
        position: { x: 0, y: 0 },
      };

      // Create table nodes
      const tableNodes: Node<TableNodeData>[] = data.tables.map((tableName, index) => {
        const columns = data.table_info ? parseTableInfo(data.table_info, tableName) : [];

        return {
          id: `table-${index}`,
          type: 'table',
          data: {
            name: tableName,
            columns,
          },
          position: { x: 0, y: 0 }, // Will be set by dagre
        };
      });

      // Create edges from database to tables
      const tableEdges: Edge[] = data.tables.map((_, index) => ({
        id: `e-db-table-${index}`,
        source: 'db-root',
        target: `table-${index}`,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#9333ea', strokeWidth: 2 },
      }));

      // Apply layout
      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
        [databaseNode, ...tableNodes],
        tableEdges,
        layoutDirection
      );

      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
    } catch (error) {
      console.error('Error loading database schema:', error);
      if (onError) {
        onError(error instanceof Error ? error.message : 'Unknown error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDatabaseSchema();
  }, [databaseId]);

  // Re-layout when direction changes
  const onLayout = useCallback(
    (direction: 'TB' | 'LR') => {
      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
        nodes,
        edges,
        direction
      );

      setNodes([...layoutedNodes]);
      setEdges([...layoutedEdges]);
      setLayoutDirection(direction);
    },
    [nodes, edges, setNodes, setEdges]
  );

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          <p className="mt-4 text-gray-600">Loading database schema...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
        maxZoom={2}
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: true,
        }}
      >
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        <Controls />

        <Panel position="top-right" className="bg-white rounded-lg shadow-lg p-2 m-2">
          <div className="flex gap-2">
            <button
              onClick={() => onLayout('TB')}
              className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                layoutDirection === 'TB'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Vertical
            </button>
            <button
              onClick={() => onLayout('LR')}
              className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                layoutDirection === 'LR'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Horizontal
            </button>
          </div>
        </Panel>

        <Panel position="top-left" className="bg-white rounded-lg shadow-lg p-3 m-2">
          <div className="text-sm">
            <div className="font-semibold text-gray-800 mb-2">Database Schema</div>
            <div className="text-gray-600">
              {nodes.length - 1} tables • {edges.length} connections
            </div>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}
