"""
Modern Interactive Data Visualization Generator using Plotly
Automatically generates professional, interactive visualizations from SQL query results
Uses intelligent data structure analysis to select optimal chart types
"""

import pandas as pd
import plotly.express as px
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class VisualizationGenerator:
    """
    Intelligent visualization generator that:
    1. Analyzes data structure to select optimal chart type
    2. Generates interactive Plotly visualizations
    3. Returns JSON for frontend rendering
    4. Provides insights for non-technical users
    """

    def should_visualize(self, query: str, sql_query: str, df: pd.DataFrame) -> bool:
        """
        Determine if visualization should be generated

        Args:
            query: User's natural language query
            sql_query: Generated SQL query
            df: DataFrame with query results

        Returns:
            True if visualization should be generated
        """
        if df is None or df.empty:
            return False

        # Don't visualize single values (unless explicitly requested)
        if len(df) == 1 and len(df.columns) == 1:
            query_lower = query.lower()
            if not any(kw in query_lower for kw in ["show", "plot", "chart", "visualize", "graph"]):
                return False

        # Don't visualize too much data (performance)
        if len(df) > 10000:
            return False

        # Don't visualize if too many columns (confusing)
        if len(df.columns) > 10:
            return False

        # Check if query suggests aggregation/analysis (good for viz)
        sql_lower = sql_query.lower() if sql_query else ""
        has_aggregation = any(kw in sql_lower for kw in ["group by", "count(", "sum(", "avg(", "max(", "min("])

        # Visualize if:
        # 1. Multiple rows with reasonable columns
        # 2. Has aggregation
        # 3. Has numeric data
        has_numeric = len(df.select_dtypes(include=['number']).columns) > 0

        return (len(df) > 1 and len(df.columns) >= 2 and has_numeric) or has_aggregation

    def determine_chart_type(self, df: pd.DataFrame, query: str) -> str:
        """
        Intelligent chart type selection based on data structure

        Args:
            df: DataFrame with query results
            query: User's natural language query

        Returns:
            Chart type string
        """
        query_lower = query.lower()

        # Analyze data structure
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()

        # Check for datetime columns
        datetime_cols = []
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                datetime_cols.append(col)
            elif df[col].dtype == 'object':
                # Try to detect date strings
                try:
                    sample = df[col].dropna().head(5)
                    if len(sample) > 0:
                        pd.to_datetime(sample)
                        datetime_cols.append(col)
                except:
                    pass

        # Explicit chart type in query
        if any(kw in query_lower for kw in ["pie chart", "pie"]):
            if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                return "pie"

        if any(kw in query_lower for kw in ["scatter", "correlation", "relationship"]):
            if len(numeric_cols) >= 2:
                return "scatter"

        if any(kw in query_lower for kw in ["trend", "over time", "timeline"]):
            if len(datetime_cols) > 0 or len(categorical_cols) > 0:
                return "line"

        # Data-driven selection

        # Time series data → Line chart
        if datetime_cols:
            return "line"

        # Two numeric columns → Scatter plot
        if len(numeric_cols) >= 2 and len(categorical_cols) == 0:
            if len(df) > 50:  # Enough points for correlation
                return "scatter"

        # One categorical + one numeric → Bar chart (most common)
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            cardinality = df[categorical_cols[0]].nunique()

            # Pie chart for proportions with few categories
            if cardinality <= 8 and any(kw in query_lower for kw in ["percentage", "proportion", "share", "distribution"]):
                return "pie"

            return "bar"

        # Single numeric column → Histogram
        if len(numeric_cols) == 1 and len(categorical_cols) == 0:
            return "histogram"

        # Default to bar chart
        return "bar"

    def generate_visualization(
        self,
        df: pd.DataFrame,
        query: str,
        sql_query: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Main method to generate visualization from query results

        Args:
            df: DataFrame with SQL query results
            query: User's natural language query
            sql_query: Generated SQL query
            config: Optional configuration dictionary

        Returns:
            Dictionary with visualization data or None if not needed
        """
        try:
            # Check if visualization is needed
            if not self.should_visualize(query, sql_query, df):
                return None

            # Determine chart type
            chart_type = self.determine_chart_type(df, query)

            # Generate chart
            fig, metadata = self._create_chart(df, chart_type, query, config)

            if fig is None:
                return None

            # Generate insights
            insights = self._generate_insights(df, chart_type, query)

            return {
                "enabled": True,
                "chart_type": chart_type,
                "plotly_json": fig.to_json(),  # Interactive Plotly JSON
                "config": {
                    "title": fig.layout.title.text if fig.layout.title else "Data Visualization",
                    **(config or {})
                },
                "metadata": metadata,
                "insights": insights
            }

        except Exception as e:
            logger.error(f"Error generating visualization: {e}", exc_info=True)
            # Return None to gracefully handle visualization failures
            return None

    def _create_chart(
        self,
        df: pd.DataFrame,
        chart_type: str,
        query: str,  # noqa: ARG002 - Reserved for future use
        config: Optional[Dict[str, Any]] = None
    ) -> tuple:
        """Generate Plotly chart based on type"""

        if config is None:
            config = {}

        try:
            if chart_type == "bar":
                return self._create_bar_chart(df, config)
            elif chart_type == "line":
                return self._create_line_chart(df, config)
            elif chart_type == "pie":
                return self._create_pie_chart(df, config)
            elif chart_type == "scatter":
                return self._create_scatter_chart(df, config)
            elif chart_type == "histogram":
                return self._create_histogram(df, config)
            else:
                return self._create_bar_chart(df, config)
        except Exception as e:
            logger.error(f"Error creating {chart_type} chart: {e}")
            return None, {}

    def _create_bar_chart(self, df: pd.DataFrame, config: Dict) -> tuple:
        """Create interactive bar chart"""

        categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not categorical_cols or not numerical_cols:
            return None, {}

        cat_col = categorical_cols[0]
        num_col = numerical_cols[0]

        # Limit to top 20 for readability
        df_plot = df.copy()
        truncated = False
        if len(df_plot) > 20:
            df_plot = df_plot.nlargest(20, num_col)
            truncated = True

        # Sort by value for better visual
        df_plot = df_plot.sort_values(by=num_col, ascending=True)

        # Horizontal bar if many categories
        if len(df_plot) > 10:
            fig = px.bar(
                df_plot,
                y=cat_col,
                x=num_col,
                orientation='h',
                title=config.get("title", f"{num_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}"),
                template="plotly_white",
                color=num_col,
                color_continuous_scale="Blues"
            )
        else:
            fig = px.bar(
                df_plot,
                x=cat_col,
                y=num_col,
                title=config.get("title", f"{num_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}"),
                template="plotly_white",
                color=num_col,
                color_continuous_scale="Blues"
            )

        # Add value labels
        fig.update_traces(texttemplate='%{y:,.0f}' if len(df_plot) <= 10 else '%{x:,.0f}',
                         textposition='outside')

        # Improve layout
        fig.update_layout(
            showlegend=False,
            hovermode='closest',
            xaxis_title=cat_col.replace('_', ' ').title() if len(df_plot) <= 10 else num_col.replace('_', ' ').title(),
            yaxis_title=num_col.replace('_', ' ').title() if len(df_plot) <= 10 else cat_col.replace('_', ' ').title(),
            height=400 + (len(df_plot) * 20 if len(df_plot) > 10 else 0)
        )

        metadata = {
            "chart_type": "bar",
            "truncated": truncated,
            "original_rows": len(df) if truncated else len(df_plot)
        }

        return fig, metadata

    def _create_line_chart(self, df: pd.DataFrame, config: Dict) -> tuple:
        """Create interactive line chart for time series"""

        # Find datetime column
        datetime_cols = []
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                datetime_cols.append(col)
            elif df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                    datetime_cols.append(col)
                except:
                    pass

        if not datetime_cols:
            # Use first column as x-axis
            datetime_cols = [df.columns[0]]

        datetime_col = datetime_cols[0]
        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not numerical_cols:
            return None, {}

        # Sort by datetime
        df_plot = df.sort_values(by=datetime_col)

        fig = px.line(
            df_plot,
            x=datetime_col,
            y=numerical_cols,
            title=config.get("title", "Trend Over Time"),
            template="plotly_white",
            markers=True
        )

        # Improve layout
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        fig.update_layout(
            hovermode='x unified',
            xaxis_title=datetime_col.replace('_', ' ').title(),
            yaxis_title="Value",
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig, {"chart_type": "line"}

    def _create_pie_chart(self, df: pd.DataFrame, config: Dict) -> tuple:
        """Create interactive pie chart"""

        categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not categorical_cols or not numerical_cols:
            return None, {}

        cat_col = categorical_cols[0]
        num_col = numerical_cols[0]

        # Limit to top 10
        df_plot = df.copy()
        if len(df_plot) > 10:
            df_top = df_plot.nlargest(10, num_col)
            others_sum = df_plot.iloc[10:][num_col].sum()
            if others_sum > 0:
                others_row = pd.DataFrame({cat_col: ['Others'], num_col: [others_sum]})
                df_plot = pd.concat([df_top, others_row], ignore_index=True)
            else:
                df_plot = df_top

        fig = px.pie(
            df_plot,
            names=cat_col,
            values=num_col,
            title=config.get("title", f"{num_col.replace('_', ' ').title()} Distribution"),
            template="plotly_white",
            hole=0.3  # Donut chart for modern look
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=500)

        return fig, {"chart_type": "pie"}

    def _create_scatter_chart(self, df: pd.DataFrame, config: Dict) -> tuple:
        """Create interactive scatter plot"""

        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()

        if len(numerical_cols) < 2:
            return None, {}

        x_col, y_col = numerical_cols[0], numerical_cols[1]

        # Sample if too many points
        df_plot = df
        sampled = False
        if len(df) > 1000:
            df_plot = df.sample(n=1000, random_state=42)
            sampled = True

        fig = px.scatter(
            df_plot,
            x=x_col,
            y=y_col,
            title=config.get("title", f"{x_col.replace('_', ' ').title()} vs {y_col.replace('_', ' ').title()}"),
            template="plotly_white",
            trendline="ols",  # Add trend line
            opacity=0.6
        )

        fig.update_traces(marker=dict(size=8))
        fig.update_layout(
            hovermode='closest',
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
            height=500
        )

        metadata = {
            "chart_type": "scatter",
            "sampled": sampled,
            "sample_size": 1000 if sampled else len(df)
        }

        return fig, metadata

    def _create_histogram(self, df: pd.DataFrame, config: Dict) -> tuple:
        """Create interactive histogram"""

        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not numerical_cols:
            return None, {}

        num_col = numerical_cols[0]

        fig = px.histogram(
            df,
            x=num_col,
            title=config.get("title", f"Distribution of {num_col.replace('_', ' ').title()}"),
            template="plotly_white",
            nbins=30,
            marginal="box"  # Add box plot on top
        )

        fig.update_layout(
            xaxis_title=num_col.replace('_', ' ').title(),
            yaxis_title="Frequency",
            height=500,
            showlegend=False
        )

        return fig, {"chart_type": "histogram"}

    def _generate_insights(self, df: pd.DataFrame, chart_type: str, query: str) -> str:  # noqa: ARG002 - query reserved for future NLP insights
        """Generate natural language insights about the data"""

        try:
            insights = []

            # Basic stats
            insights.append(f"📊 Showing {len(df)} data points")

            # Chart-specific insights
            if chart_type == "bar":
                categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
                numerical_cols = df.select_dtypes(include=['number']).columns.tolist()

                if categorical_cols and numerical_cols:
                    cat_col = categorical_cols[0]
                    num_col = numerical_cols[0]

                    top_value = df.loc[df[num_col].idxmax()]
                    insights.append(f"🏆 Highest: {top_value[cat_col]} with {top_value[num_col]:,.0f}")

                    if len(df) > 1:
                        bottom_value = df.loc[df[num_col].idxmin()]
                        insights.append(f"📉 Lowest: {bottom_value[cat_col]} with {bottom_value[num_col]:,.0f}")

            elif chart_type == "line":
                numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
                if numerical_cols:
                    num_col = numerical_cols[0]
                    trend = "increasing" if df[num_col].iloc[-1] > df[num_col].iloc[0] else "decreasing"
                    insights.append(f"📈 Overall trend is {trend}")

            elif chart_type == "pie":
                categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
                numerical_cols = df.select_dtypes(include=['number']).columns.tolist()

                if categorical_cols and numerical_cols:
                    cat_col = categorical_cols[0]
                    num_col = numerical_cols[0]

                    total = df[num_col].sum()
                    top_value = df.loc[df[num_col].idxmax()]
                    percentage = (top_value[num_col] / total) * 100
                    insights.append(f"🥇 {top_value[cat_col]} accounts for {percentage:.1f}% of total")

            return " • ".join(insights)

        except Exception as e:
            logger.warning(f"Could not generate insights: {e}")
            return f"📊 Showing {len(df)} results"
