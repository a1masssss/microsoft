/**
 * Plotly Chart Component
 * Renders interactive Plotly visualizations
 */
import { useEffect, useRef } from 'react';
import type { VisualizationData } from '../api/ai-chatbot';
import Plotly from 'plotly.js-dist';

interface PlotlyChartProps {
  visualization: VisualizationData;
}

export default function PlotlyChart({ visualization }: PlotlyChartProps) {
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
    <div className="plotly-chart">
      <div className="chart-header">
        <span className="chart-type-badge">{visualization.chart_type}</span>
        {visualization.config?.title && (
          <h4>{visualization.config.title}</h4>
        )}
      </div>
      <div ref={chartRef} className="chart-container" />

      {/* Metadata badges */}
      {visualization.metadata && (
        <div className="chart-metadata">
          {visualization.metadata.truncated && (
            <span className="metadata-badge">
              Showing top 20 of {visualization.metadata.original_rows} rows
            </span>
          )}
          {visualization.metadata.sampled && (
            <span className="metadata-badge">
              Sampled {visualization.metadata.sample_size} points
            </span>
          )}
        </div>
      )}
    </div>
  );
}
