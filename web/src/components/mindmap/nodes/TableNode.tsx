import { memo, useState } from 'react';
import { Handle, Position } from '@xyflow/react';

export type TableNodeData = {
  name: string;
  columns?: Array<{
    name: string;
    type: string;
    isPrimary?: boolean;
  }>;
  rowCount?: number;
};

function TableNodeComponent({ data }: { data: TableNodeData }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const columnCount = data.columns?.length || 0;

  return (
    <div className="shadow-lg rounded-lg bg-white border-2 border-purple-300 min-w-[200px] max-w-[300px]">
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-purple-400 !w-3 !h-3 !border-2 !border-white"
      />

      <div
        className="px-4 py-3 bg-gradient-to-r from-purple-500 to-purple-600 rounded-t-md cursor-pointer hover:from-purple-600 hover:to-purple-700 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg
              className="w-5 h-5 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
            <span className="text-white font-semibold">{data.name}</span>
          </div>
          <svg
            className={`w-4 h-4 text-white transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      <div className="px-4 py-2 bg-purple-50 text-sm text-gray-600">
        <div className="flex justify-between">
          <span>{columnCount} columns</span>
          {data.rowCount !== undefined && <span>{data.rowCount} rows</span>}
        </div>
      </div>

      {isExpanded && data.columns && data.columns.length > 0 && (
        <div className="border-t border-purple-200 max-h-48 overflow-y-auto">
          {data.columns.map((column, index) => (
            <div
              key={index}
              className={`px-4 py-2 text-sm border-b border-purple-100 last:border-b-0 ${
                column.isPrimary ? 'bg-yellow-50' : 'bg-white'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-800 flex items-center gap-1">
                  {column.isPrimary && (
                    <svg className="w-3 h-3 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  )}
                  {column.name}
                </span>
                <span className="text-gray-500 text-xs">{column.type}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-purple-400 !w-3 !h-3 !border-2 !border-white"
      />
    </div>
  );
}

export default memo(TableNodeComponent);
