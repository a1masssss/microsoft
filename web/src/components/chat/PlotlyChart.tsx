/**
 * Plotly Chart Component
 * Renders interactive Plotly visualizations
 */
import { useEffect, useRef } from 'react';
import type { VisualizationData } from '@/api/ai-chatbot';
import Plotly from 'plotly.js-dist';

interface PlotlyChartProps {
  visualization: VisualizationData;
}

export function PlotlyChart({ visualization }: PlotlyChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chartRef.current && visualization.plotly_json) {
      try {
        const plotlyData = JSON.parse(visualization.plotly_json);

        Plotly.newPlot(
          chartRef.current,
          plotlyData.data,
          plotlyData.layout,
          {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            displaylogo: false,
          }
        );
      } catch (error) {
        console.error('Error rendering Plotly chart:', error);
      }
    }

    // Cleanup
    return () => {
      if (chartRef.current) {
        Plotly.purge(chartRef.current);
      }
    };
  }, [visualization.plotly_json]);

  return (
    <div className="w-full bg-white dark:bg-neutral-800 rounded-lg p-4 shadow-lg">
      <div className="flex items-center justify-between mb-3">
        <span className="px-2 py-1 text-xs font-semibold bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
          {visualization.chart_type}
        </span>
        {visualization.config?.title && (
          <h4 className="text-sm font-semibold text-gray-800 dark:text-gray-200">
            {visualization.config.title}
          </h4>
        )}
      </div>
      <div ref={chartRef} className="w-full" style={{ minHeight: '400px' }} />

      {/* Metadata badges */}
      {visualization.metadata && (
        <div className="flex gap-2 mt-3 flex-wrap">
          {visualization.metadata.truncated && (
            <span className="px-2 py-1 text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded">
              Showing top 20 of {visualization.metadata.original_rows} rows
            </span>
          )}
          {visualization.metadata.sampled && (
            <span className="px-2 py-1 text-xs bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded">
              Sampled {visualization.metadata.sample_size} points
            </span>
          )}
        </div>
      )}
    </div>
  );
}

