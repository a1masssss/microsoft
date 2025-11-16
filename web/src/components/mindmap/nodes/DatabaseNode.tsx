import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';

export type DatabaseNodeData = {
  name: string;
  type: string;
  tableCount: number;
};

function DatabaseNodeComponent({ data }: { data: DatabaseNodeData }) {
  return (
    <div className="px-6 py-4 shadow-lg rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 border-2 border-blue-700 min-w-[250px]">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
          <svg
            className="w-6 h-6 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"
            />
          </svg>
        </div>
        <div className="flex-1">
          <div className="text-white font-bold text-lg">{data.name}</div>
          <div className="text-blue-100 text-sm">{data.type}</div>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-blue-400/30">
        <div className="text-white text-sm">
          <span className="font-semibold">{data.tableCount}</span> tables
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-blue-400 !w-3 !h-3 !border-2 !border-white"
      />
    </div>
  );
}

export default memo(DatabaseNodeComponent);
