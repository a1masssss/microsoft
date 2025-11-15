declare module 'plotly.js-dist' {
  import { PlotlyHTMLElement } from 'plotly.js';
  
  export interface PlotParams {
    data: any[];
    layout?: any;
    config?: any;
  }
  
  export function newPlot(
    root: HTMLElement,
    data: any[],
    layout?: any,
    config?: any
  ): Promise<PlotlyHTMLElement>;
  
  export function purge(root: HTMLElement): void;
  
  export default {
    newPlot,
    purge,
  };
}

