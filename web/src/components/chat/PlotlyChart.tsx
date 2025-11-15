/**
 * Enhanced Plotly Chart Component
 * Renders interactive Plotly visualizations with controls and improved display
 */
import { useEffect, useRef, useState } from 'react';
import type { VisualizationData } from '@/api/ai-chatbot';
import Plotly from 'plotly.js-dist';
import { Download, Maximize2, RefreshCw, BarChart3, LineChart, PieChart, Activity } from 'lucide-react';

interface PlotlyChartProps {
  visualization: VisualizationData;
}

const CHART_TYPE_ICONS: Record<string, React.ReactNode> = {
  bar: <BarChart3 size={16} />,
  line: <LineChart size={16} />,
  pie: <PieChart size={16} />,
  scatter: <Activity size={16} />,
  histogram: <Activity size={16} />,
  heatmap: <BarChart3 size={16} />,
  box: <BarChart3 size={16} />,
};

export function PlotlyChart({ visualization }: PlotlyChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (chartRef.current && visualization.plotly_json) {
      setIsLoading(true);
      setError(null);
      
      try {
        const plotlyData = JSON.parse(visualization.plotly_json);

        // Update layout for dark mode if needed
        const layout = {
          ...plotlyData.layout,
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(0,0,0,0)',
          font: {
            ...plotlyData.layout?.font,
            color: '#e5e5e5',
          },
          xaxis: {
            ...plotlyData.layout?.xaxis,
            gridcolor: 'rgba(255,255,255,0.1)',
          },
          yaxis: {
            ...plotlyData.layout?.yaxis,
            gridcolor: 'rgba(255,255,255,0.1)',
          },
        };

        Plotly.newPlot(
          chartRef.current,
          plotlyData.data,
          layout,
          {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            displaylogo: false,
            toImageButtonOptions: {
              format: 'png',
              filename: `chart_${visualization.chart_type}_${Date.now()}`,
              height: 600,
              width: 1200,
              scale: 2,
            },
          }
        );
        
        setIsLoading(false);
      } catch (err) {
        console.error('Error rendering Plotly chart:', err);
        setError('Failed to render chart');
        setIsLoading(false);
      }
    }

    // Cleanup
    return () => {
      if (chartRef.current) {
        Plotly.purge(chartRef.current);
      }
    };
  }, [visualization.plotly_json]);

  const handleExport = (format: 'png' | 'svg' | 'pdf') => {
    if (!chartRef.current) return;
    
    const gd = chartRef.current as any;
    const filename = `chart_${visualization.chart_type}_${Date.now()}`;
    
    // Use Plotly's toImage method if available
    if (gd && (gd as any).toImage) {
      (gd as any).toImage({
        format,
        filename,
        height: 600,
        width: 1200,
        scale: format === 'png' ? 2 : 1,
      }).then((url: string) => {
        const link = document.createElement('a');
        link.href = url;
        link.download = `${filename}.${format}`;
        link.click();
      });
    } else {
      // Fallback: use browser's download
      const canvas = chartRef.current?.querySelector('canvas');
      if (canvas) {
        canvas.toBlob((blob) => {
          if (blob) {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `${filename}.png`;
            link.click();
            URL.revokeObjectURL(url);
          }
        }, `image/${format}`);
      }
    }
  };

  const handleFullscreen = () => {
    if (!chartRef.current) return;
    
    if (!isFullscreen) {
      if (chartRef.current.requestFullscreen) {
        chartRef.current.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  if (error) {
    return (
      <div className="w-full bg-neutral-800 rounded-lg p-4 border border-neutral-700">
        <div className="text-red-400 text-sm">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="w-full bg-neutral-800 rounded-lg p-4 border border-neutral-700">
      {/* Header with controls */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 text-xs font-semibold bg-blue-500/20 text-blue-300 rounded border border-blue-500/30 flex items-center gap-1">
            {CHART_TYPE_ICONS[visualization.chart_type] || <BarChart3 size={16} />}
            {visualization.chart_type}
          </span>
          {visualization.config?.title && (
            <h4 className="text-sm font-semibold text-neutral-200">
              {visualization.config.title}
            </h4>
          )}
        </div>
        
        {/* Action buttons */}
        <div className="flex items-center gap-2">
          {/* Export dropdown */}
          <div className="relative group">
            <button
              className="p-1.5 hover:bg-neutral-700 rounded transition-colors"
              title="Export chart"
            >
              <Download size={16} className="text-neutral-400" />
            </button>
            <div className="absolute right-0 top-full mt-1 bg-neutral-800 border border-neutral-700 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
              <div className="py-1">
                <button
                  onClick={() => handleExport('png')}
                  className="w-full px-3 py-1.5 text-left text-sm text-neutral-300 hover:bg-neutral-700"
                >
                  Export as PNG
                </button>
                <button
                  onClick={() => handleExport('svg')}
                  className="w-full px-3 py-1.5 text-left text-sm text-neutral-300 hover:bg-neutral-700"
                >
                  Export as SVG
                </button>
                <button
                  onClick={() => handleExport('pdf')}
                  className="w-full px-3 py-1.5 text-left text-sm text-neutral-300 hover:bg-neutral-700"
                >
                  Export as PDF
                </button>
              </div>
            </div>
          </div>
          
          {/* Fullscreen */}
          <button
            onClick={handleFullscreen}
            className="p-1.5 hover:bg-neutral-700 rounded transition-colors"
            title="Toggle fullscreen"
          >
            <Maximize2 size={16} className="text-neutral-400" />
          </button>
        </div>
      </div>

      {/* Chart container */}
      <div className="relative">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-neutral-800/50 z-10">
            <div className="flex items-center gap-2 text-neutral-400">
              <RefreshCw size={16} className="animate-spin" />
              <span className="text-sm">Loading chart...</span>
            </div>
          </div>
        )}
        <div 
          ref={chartRef} 
          className="w-full" 
          style={{ minHeight: '400px' }}
        />
      </div>

      {/* Metadata badges */}
      {visualization.metadata && (
        <div className="flex gap-2 mt-3 flex-wrap">
          {visualization.metadata.truncated && (
            <span className="px-2 py-1 text-xs bg-yellow-500/20 text-yellow-300 rounded border border-yellow-500/30">
              Showing top 20 of {visualization.metadata.original_rows} rows
            </span>
          )}
          {visualization.metadata.sampled && (
            <span className="px-2 py-1 text-xs bg-purple-500/20 text-purple-300 rounded border border-purple-500/30">
              Sampled {visualization.metadata.sample_size} points
            </span>
          )}
          {'correlation' in (visualization.metadata || {}) && visualization.metadata?.correlation !== undefined && (
            <span className="px-2 py-1 text-xs bg-green-500/20 text-green-300 rounded border border-green-500/30">
              Correlation: {visualization.metadata.correlation.toFixed(2)}
            </span>
          )}
        </div>
      )}

      {/* Insights */}
      {visualization.insights && (
        <div className="mt-3 pt-3 border-t border-neutral-700">
          <p className="text-sm text-neutral-300">{visualization.insights}</p>
        </div>
      )}
    </div>
  );
}
