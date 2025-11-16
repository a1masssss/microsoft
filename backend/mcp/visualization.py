"""
Modern Interactive Data Visualization Generator using Plotly
Automatically generates professional, interactive visualizations from SQL query results
Uses intelligent data structure analysis and AI to select optimal chart types
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field
from typing_extensions import Literal

# Initialize logger first
logger = logging.getLogger(__name__)

# Try to import scipy for advanced statistics (optional)
try:
    from scipy import stats
    from scipy.stats import normaltest, skew, kurtosis
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy not available, some advanced statistical features will be disabled")

# Try to import OpenAI for AI features
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ============================================================================
# Pydantic Models for Structured AI Outputs
# ============================================================================

class ChartRecommendation(BaseModel):
    """AI-generated chart type recommendation"""
    primary_chart_type: Literal["bar", "line", "pie", "scatter", "histogram", "heatmap", "box", "treemap"] = Field(
        description="The recommended primary chart type"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score from 0.0 to 1.0"
    )
    reasoning: str = Field(
        description="Explanation of why this chart type was selected"
    )
    alternative_charts: List[Literal["bar", "line", "pie", "scatter", "histogram", "heatmap", "box", "treemap"]] = Field(
        default_factory=list,
        description="Alternative chart types that could also work"
    )
    suggested_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Suggested chart configuration options"
    )


class DataInsights(BaseModel):
    """AI-generated data insights"""
    summary: str = Field(
        description="Brief 2-3 sentence summary of key findings"
    )
    key_findings: List[str] = Field(
        description="3-5 key insights from the data"
    )
    anomalies: List[str] = Field(
        default_factory=list,
        description="Notable anomalies or outliers"
    )
    trends: List[str] = Field(
        default_factory=list,
        description="Identified trends"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations"
    )


# ============================================================================
# Data Profiler - Statistical Analysis
# ============================================================================

class DataProfiler:
    """Advanced statistical analysis of data for visualization context"""
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive data analysis
        
        Returns:
            Dictionary with statistical insights
        """
        if df is None or df.empty:
            return {"is_empty": True}
        
        analysis = {
            "num_rows": len(df),
            "num_columns": len(df.columns),
            "column_names": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "numeric_columns": [],
            "categorical_columns": [],
            "datetime_columns": [],
            "statistics": {},
            "patterns": [],
            "correlations": {},
            "outliers": {},
            "distributions": {},
            "data_quality": {}
        }
        
        # Categorize columns
        for col in df.columns:
            dtype = str(df[col].dtype)
            
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                analysis["datetime_columns"].append(col)
            elif df[col].dtype in ['object', 'category', 'bool']:
                analysis["categorical_columns"].append(col)
                # Try to detect if it's actually a date string
                if df[col].dtype == 'object':
                    try:
                        sample = df[col].dropna().head(5)
                        if len(sample) > 0:
                            # Try parsing with explicit format handling to avoid warnings
                            pd.to_datetime(sample, errors='raise', format='mixed')
                            analysis["datetime_columns"].append(col)
                            if col in analysis["categorical_columns"]:
                                analysis["categorical_columns"].remove(col)
                    except (ValueError, TypeError):
                        pass
            elif pd.api.types.is_numeric_dtype(df[col]):
                analysis["numeric_columns"].append(col)
        
        # Statistical analysis for numeric columns (optimized - only essential stats)
        for col in analysis["numeric_columns"]:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                # Calculate only essential statistics for speed
                stats_dict = {
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "q25": float(col_data.quantile(0.25)),
                    "q75": float(col_data.quantile(0.75)),
                    "iqr": float(col_data.quantile(0.75) - col_data.quantile(0.25)),
                }
                
                # Only calculate skewness if needed (it's slower)
                if len(col_data) > 2:
                    try:
                        stats_dict["skewness"] = float(col_data.skew())
                    except:
                        stats_dict["skewness"] = 0.0
                
                # Advanced stats only if scipy available and data is substantial
                if SCIPY_AVAILABLE and len(col_data) > 10:
                    try:
                        stats_dict["kurtosis"] = float(kurtosis(col_data))
                    except:
                        pass
                
                analysis["statistics"][col] = stats_dict
                
                # Distribution detection (fast)
                analysis["distributions"][col] = self._detect_distribution(col_data)
                
                # Outlier detection (only if IQR is meaningful)
                if stats_dict["iqr"] > 0:
                    outliers = self._detect_outliers(col_data, stats_dict)
                    if outliers:
                        analysis["outliers"][col] = outliers
        
        # Correlation analysis
        if len(analysis["numeric_columns"]) > 1:
            numeric_df = df[analysis["numeric_columns"]].select_dtypes(include=[np.number])
            if len(numeric_df.columns) > 1:
                corr_matrix = numeric_df.corr()
                # Convert to dict format
                analysis["correlations"] = {
                    col: {
                        other_col: float(corr_matrix.loc[col, other_col])
                        for other_col in corr_matrix.columns
                        if col != other_col
                    }
                    for col in corr_matrix.columns
                }
        
        # Pattern detection
        analysis["patterns"] = self.detect_patterns(df, analysis)
        
        # Data quality metrics
        analysis["data_quality"] = {
            "missing_values": {col: int(df[col].isna().sum()) for col in df.columns},
            "duplicate_rows": int(df.duplicated().sum()),
            "completeness": float(1 - (df.isna().sum().sum() / (len(df) * len(df.columns))))
        }
        
        return analysis
    
    def _detect_distribution(self, data: pd.Series) -> str:
        """Detect distribution type"""
        if len(data) < 3:
            return "unknown"
        
        skewness = abs(data.skew())
        
        if skewness < 0.5:
            return "normal"
        elif skewness < 1.0:
            return "slightly_skewed"
        elif skewness < 2.0:
            return "moderately_skewed"
        else:
            return "highly_skewed"
    
    def _detect_outliers(self, data: pd.Series, stats_dict: Dict) -> Dict[str, Any]:
        """Detect outliers using IQR method"""
        if "iqr" not in stats_dict or stats_dict["iqr"] == 0:
            return {}
        
        q1 = stats_dict["q25"]
        q3 = stats_dict["q75"]
        iqr = stats_dict["iqr"]
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        
        if len(outliers) > 0:
            return {
                "count": int(len(outliers)),
                "percentage": float(len(outliers) / len(data) * 100),
                "values": [float(v) for v in outliers.head(10).tolist()]  # Limit to 10
            }
        return {}
    
    def detect_patterns(self, df: pd.DataFrame, analysis: Dict) -> List[str]:
        """Detect data patterns"""
        patterns = []
        
        # Time series pattern
        if analysis["datetime_columns"]:
            patterns.append("time_series")
        
        # High cardinality categorical
        for col in analysis["categorical_columns"]:
            unique_count = df[col].nunique()
            if unique_count > len(df) * 0.9:
                patterns.append("high_cardinality_categorical")
            elif unique_count < 10:
                patterns.append("low_cardinality_categorical")
        
        # Strong correlation
        for col, correlations in analysis.get("correlations", {}).items():
            for other_col, corr in correlations.items():
                if abs(corr) > 0.7:
                    patterns.append(f"strong_correlation_{col}_{other_col}")
        
        # Outliers present
        if analysis.get("outliers"):
            patterns.append("has_outliers")
        
        # Normal distribution
        for col, dist in analysis.get("distributions", {}).items():
            if dist == "normal":
                patterns.append(f"normal_distribution_{col}")
        
        return patterns


# ============================================================================
# AI-Powered Chart Selector
# ============================================================================

class IntelligentChartSelector:
    """Uses AI to intelligently select chart types based on query and data"""
    
    def __init__(self, openai_client: Optional[Any] = None):
        """
        Initialize with optional OpenAI client
        
        Args:
            openai_client: OpenAI client instance (optional)
        """
        self.client = openai_client
        self._cache = {}  # Simple in-memory cache
    
    def select_chart_type(
        self,
        query: str,
        df: pd.DataFrame,
        profiler_results: Dict[str, Any]
    ) -> ChartRecommendation:
        """
        Use AI to select optimal chart type (with fast fallback)
        
        Args:
            query: User's natural language query
            df: DataFrame with data
            profiler_results: Results from DataProfiler.analyze()
            
        Returns:
            ChartRecommendation with AI's recommendation
        """
        # Check cache first
        cache_key = self._get_cache_key(query, df, profiler_results)
        if cache_key in self._cache:
            logger.debug("Using cached chart recommendation")
            return self._cache[cache_key]
        
        # If no OpenAI client or data is too simple, use rule-based (faster)
        if not self.client or len(df) < 3:
            return self._rule_based_recommendation(query, df, profiler_results)
        
        try:
            # Build prompt
            prompt = self._build_selection_prompt(query, df, profiler_results)
            
            # Call OpenAI API with optimized timeout
            try:
                import httpx
                timeout_config = httpx.Timeout(connect=2.0, read=5.0, write=2.0, pool=5.0)
            except ImportError:
                timeout_config = 5.0  # Fallback to simple timeout
            
            response = self.client.with_options(
                timeout=timeout_config
            ).chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {
                        "role": "system",
                        "content": CHART_SELECTION_SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,  # Lower temperature for consistent recommendations
                max_tokens=200  # Limit response size for faster generation
            )
            
            # Parse response
            content = response.choices[0].message.content
            result_dict = json.loads(content)
            
            # Validate and clean alternative_charts
            if "alternative_charts" in result_dict:
                valid_chart_types = ["bar", "line", "pie", "scatter", "histogram", "heatmap", "box", "treemap"]
                result_dict["alternative_charts"] = [
                    chart for chart in result_dict["alternative_charts"]
                    if chart in valid_chart_types
                ]
            
            # Create recommendation object
            recommendation = ChartRecommendation(**result_dict)
            
            # Cache result
            self._cache[cache_key] = recommendation
            
            return recommendation
            
        except Exception as e:
            logger.warning(f"AI chart selection failed: {e}, using rule-based fallback")
            return self._rule_based_recommendation(query, df, profiler_results)
    
    def _build_selection_prompt(
        self,
        query: str,
        df: pd.DataFrame,
        profiler_results: Dict[str, Any]
    ) -> str:
        """Build prompt for AI chart selection (optimized for speed)"""
        # Prepare minimal data summary (reduce tokens)
        data_summary = {
            "rows": profiler_results.get("num_rows", 0),
            "cols": profiler_results.get("num_columns", 0),
            "numeric": len(profiler_results.get("numeric_columns", [])),
            "categorical": len(profiler_results.get("categorical_columns", [])),
            "datetime": len(profiler_results.get("datetime_columns", [])),
        }
        
        # Only include first 3 rows and first 3 columns to reduce tokens
        sample_data = []
        if not df.empty:
            sample_df = df.head(3)[df.columns[:3]]
            sample_data = sample_df.to_dict('records')
        
        prompt = f"""Query: "{query}"

Data: {json.dumps(data_summary)} | Sample: {json.dumps(sample_data[:2], default=str)[:200]}

Return JSON: {{"primary_chart_type": "bar|line|pie|scatter|histogram|heatmap|box|treemap", "confidence": 0.0-1.0, "reasoning": "brief", "alternative_charts": [], "suggested_config": {{}}}}"""
        return prompt
    
    def _rule_based_recommendation(
        self,
        query: str,
        df: pd.DataFrame,
        profiler_results: Dict[str, Any]
    ) -> ChartRecommendation:
        """Fallback rule-based recommendation"""
        query_lower = query.lower()
        
        # Simple rule-based logic
        if profiler_results.get("datetime_columns"):
            chart_type = "line"
            reasoning = "Time series data detected, line chart recommended"
        elif len(profiler_results.get("numeric_columns", [])) >= 2:
            chart_type = "scatter"
            reasoning = "Multiple numeric columns, scatter plot recommended"
        elif len(profiler_results.get("categorical_columns", [])) >= 1:
            if "pie" in query_lower or "proportion" in query_lower:
                chart_type = "pie"
                reasoning = "Pie chart requested for proportions"
            else:
                chart_type = "bar"
                reasoning = "Categorical data with numeric values, bar chart recommended"
        elif len(profiler_results.get("numeric_columns", [])) == 1:
            chart_type = "histogram"
            reasoning = "Single numeric column, histogram recommended"
        else:
            chart_type = "bar"
            reasoning = "Default bar chart recommendation"
        
        return ChartRecommendation(
            primary_chart_type=chart_type,
            confidence=0.7,
            reasoning=reasoning,
            alternative_charts=[],
            suggested_config={}
        )
    
    def _get_cache_key(self, query: str, df: pd.DataFrame, profiler_results: Dict) -> str:
        """Generate cache key"""
        # Use query + data shape + column names for cache key
        key_str = f"{query}_{len(df)}_{len(df.columns)}_{'_'.join(df.columns)}"
        return hashlib.md5(key_str.encode()).hexdigest()


# ============================================================================
# AI Insights Generator
# ============================================================================

class AIInsightsGenerator:
    """Uses AI to generate data insights and narratives"""
    
    def __init__(self, openai_client: Optional[Any] = None):
        """
        Initialize with optional OpenAI client
        
        Args:
            openai_client: OpenAI client instance (optional)
        """
        self.client = openai_client
    
    def generate_insights(
        self,
        df: pd.DataFrame,
        chart_type: str,
        query: str,
        stats: Dict[str, Any]
    ) -> DataInsights:
        """
        Generate AI-powered insights
        
        Args:
            df: DataFrame with data
            chart_type: Type of chart being displayed
            query: User's original query
            stats: Statistical analysis results
        
        Returns:
            DataInsights with AI-generated narrative
        """
        if not self.client:
            return self._generate_basic_insights(df, chart_type)
        
        try:
            # Prepare data summary for LLM
            data_summary = self._prepare_data_summary(df, stats)
            
            # Optimized prompt - shorter and more direct
            prompt = f"""Query: "{query}" | Chart: {chart_type} | Data: {json.dumps(data_summary, default=str)[:500]}

Return JSON: {{"summary": "2-3 sentences", "key_findings": ["insight1", "insight2"], "anomalies": [], "trends": [], "recommendations": []}}"""
            
            try:
                import httpx
                timeout_config = httpx.Timeout(connect=2.0, read=5.0, write=2.0, pool=5.0)
            except ImportError:
                timeout_config = 5.0  # Fallback to simple timeout
            
            response = self.client.with_options(
                timeout=timeout_config
            ).chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": INSIGHTS_SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7,  # Slightly higher for creative insights
                max_tokens=300  # Limit response size
            )
            
            content = response.choices[0].message.content
            result_dict = json.loads(content)
            
            return DataInsights(**result_dict)
            
        except Exception as e:
            logger.warning(f"AI insights generation failed: {e}, using basic insights")
            return self._generate_basic_insights(df, chart_type)
    
    def _prepare_data_summary(self, df: pd.DataFrame, stats: Dict) -> Dict[str, Any]:
        """Prepare concise data summary for LLM (optimized for speed)"""
        # Minimal summary to reduce tokens and processing time
        summary = {
            "rows": len(df),
            "cols": len(df.columns),
            "col_names": list(df.columns)[:5],  # Limit to 5 columns
            "sample": df.head(2)[df.columns[:3]].to_dict('records'),  # Only 2 rows, 3 cols
        }
        
        # Add only essential statistics (limit to 2 columns)
        if "statistics" in stats:
            summary["stats"] = {}
            for col, stat_dict in list(stats["statistics"].items())[:2]:  # Limit to 2 columns
                summary["stats"][col] = {
                    "mean": round(stat_dict.get("mean", 0), 2),
                    "max": round(stat_dict.get("max", 0), 2),
                }
        
        # Add only first 3 patterns
        if "patterns" in stats:
            summary["patterns"] = stats["patterns"][:3]
        
        return summary
    
    def _generate_basic_insights(self, df: pd.DataFrame, chart_type: str) -> DataInsights:
        """Generate basic rule-based insights"""
        summary = f"Visualization shows {len(df)} data points using a {chart_type} chart."
        
        findings = [f"Dataset contains {len(df)} rows and {len(df.columns)} columns"]
        
        if chart_type == "bar":
            categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
            numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
            if categorical_cols and numerical_cols:
                top = df.loc[df[numerical_cols[0]].idxmax()]
                findings.append(f"Highest value: {top[categorical_cols[0]]} with {top[numerical_cols[0]]:,.0f}")
        
        return DataInsights(
            summary=summary,
            key_findings=findings,
            anomalies=[],
            trends=[],
            recommendations=[]
        )


# ============================================================================
# System Prompts
# ============================================================================

CHART_SELECTION_SYSTEM_PROMPT = """You are an expert data visualization consultant. Your task is to analyze user queries and data characteristics to recommend the most appropriate chart type.

Consider:
- User's intent (comparison, trend, distribution, relationship, composition)
- Data structure (categorical, numerical, temporal, hierarchical)
- Data volume and cardinality
- Best practices for data visualization

Available chart types: bar, line, pie, scatter, histogram, heatmap, box, treemap

Return your recommendation as a JSON object with primary_chart_type, confidence (0-1), reasoning, alternative_charts, and suggested_config."""

INSIGHTS_SYSTEM_PROMPT = """You are a data analyst expert. Your task is to analyze data visualizations and generate clear, actionable insights.

Focus on:
- What the data actually shows
- Key patterns, trends, and anomalies
- Actionable recommendations
- Be concise but informative
- Use plain language that non-technical users can understand

Return insights as a JSON object with summary, key_findings, anomalies, trends, and recommendations."""


# ============================================================================
# Enhanced Visualization Generator
# ============================================================================

class VisualizationGenerator:
    """
    Intelligent visualization generator that:
    1. Analyzes data structure to select optimal chart type (with AI support)
    2. Generates interactive Plotly visualizations
    3. Returns JSON for frontend rendering
    4. Provides AI-powered insights for non-technical users
    """
    
    def __init__(self, openai_client: Optional[Any] = None):
        """
        Initialize visualization generator
        
        Args:
            openai_client: Optional OpenAI client for AI features
        """
        self.openai_client = openai_client
        self.data_profiler = DataProfiler()
        self.chart_selector = IntelligentChartSelector(openai_client) if openai_client else None
        self.insights_generator = AIInsightsGenerator(openai_client) if openai_client else None

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

    def determine_chart_type(self, df: pd.DataFrame, query: str, sql_query: str = "") -> str:
        """
        Intelligent chart type selection (with AI support)

        Args:
            df: DataFrame with query results
            query: User's natural language query
            sql_query: Generated SQL query (optional)

        Returns:
            Chart type string
        """
        # Get data profile
        profiler_results = self.data_profiler.analyze(df)
        
        # Try AI-powered selection if available
        if self.chart_selector:
            try:
                recommendation = self.chart_selector.select_chart_type(query, df, profiler_results)
                return recommendation.primary_chart_type
            except Exception as e:
                logger.warning(f"AI chart selection failed: {e}, using rule-based")
        
        # Fallback to rule-based selection
        return self._rule_based_chart_selection(df, query, profiler_results)
    
    def _rule_based_chart_selection(
        self,
        df: pd.DataFrame,
        query: str,
        profiler_results: Dict[str, Any]
    ) -> str:
        """Rule-based chart type selection (fallback)"""
        query_lower = query.lower()

        # Analyze data structure
        numeric_cols = profiler_results.get("numeric_columns", [])
        categorical_cols = profiler_results.get("categorical_columns", [])
        datetime_cols = profiler_results.get("datetime_columns", [])

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
        if datetime_cols:
            return "line"

        if len(numeric_cols) >= 2 and len(categorical_cols) == 0:
            if len(df) > 50:
                return "scatter"

        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            cardinality = df[categorical_cols[0]].nunique() if categorical_cols else 0
            if cardinality <= 8 and any(kw in query_lower for kw in ["percentage", "proportion", "share", "distribution"]):
                return "pie"
            return "bar"

        if len(numeric_cols) == 1 and len(categorical_cols) == 0:
            return "histogram"

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

            # Get data profile for enhanced analysis
            profiler_results = self.data_profiler.analyze(df)

            # Determine chart type (with AI support)
            chart_type = self.determine_chart_type(df, query, sql_query)

            # Generate chart with enhanced features
            fig, metadata = self._create_chart(df, chart_type, query, config, profiler_results)

            if fig is None:
                return None

            # Generate insights (AI-powered if available, but don't block on it)
            insights_text = self._generate_basic_insights(df, chart_type, query)  # Start with basic (fast)
            
            # Try AI insights in background if available (non-blocking)
            if self.insights_generator and len(df) > 5:  # Only for substantial datasets
                try:
                    # Use a quick timeout for insights
                    insights_obj = self.insights_generator.generate_insights(
                        df, chart_type, query, profiler_results
                    )
                    if insights_obj and insights_obj.summary:
                        insights_text = insights_obj.summary + " | " + " | ".join(insights_obj.key_findings[:3])
                except Exception as e:
                    logger.debug(f"AI insights skipped: {e}, using basic insights")
                    # Already have basic insights, so continue

            return {
                "enabled": True,
                "chart_type": chart_type,
                "plotly_json": fig.to_json(),  # Interactive Plotly JSON
                "config": {
                    "title": fig.layout.title.text if fig.layout.title else "Data Visualization",
                    **(config or {})
                },
                "metadata": metadata,
                "insights": insights_text
            }

        except Exception as e:
            logger.error(f"Error generating visualization: {e}", exc_info=True)
            return None

    def _create_chart(
        self,
        df: pd.DataFrame,
        chart_type: str,
        query: str,
        config: Optional[Dict[str, Any]],
        profiler_results: Dict[str, Any]
    ) -> Tuple[Optional[go.Figure], Dict[str, Any]]:
        """Generate Plotly chart based on type with enhanced features"""
        
        if config is None:
            config = {}
        
        try:
            if chart_type == "bar":
                return self._create_enhanced_bar_chart(df, config, profiler_results)
            elif chart_type == "line":
                return self._create_enhanced_line_chart(df, config, profiler_results)
            elif chart_type == "pie":
                return self._create_enhanced_pie_chart(df, config, profiler_results)
            elif chart_type == "scatter":
                return self._create_enhanced_scatter_chart(df, config, profiler_results)
            elif chart_type == "histogram":
                return self._create_enhanced_histogram(df, config, profiler_results)
            elif chart_type == "heatmap":
                return self._create_heatmap(df, config, profiler_results)
            elif chart_type == "box":
                return self._create_boxplot(df, config, profiler_results)
            else:
                return self._create_enhanced_bar_chart(df, config, profiler_results)
        except Exception as e:
            logger.error(f"Error creating {chart_type} chart: {e}")
            return None, {}

    def _create_enhanced_bar_chart(
        self,
        df: pd.DataFrame,
        config: Dict[str, Any],
        profiler_results: Dict[str, Any]
    ) -> Tuple[go.Figure, Dict[str, Any]]:
        """Create enhanced interactive bar chart with annotations"""
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

        # Determine color scheme based on data
        stats_dict = profiler_results.get("statistics", {}).get(num_col, {})
        mean_val = stats_dict.get("mean", df_plot[num_col].mean())
        
        # Use diverging color if data spans both sides of mean significantly
        if df_plot[num_col].min() < mean_val * 0.5 and df_plot[num_col].max() > mean_val * 1.5:
            color_scale = "RdYlGn"
        else:
            color_scale = "Blues"

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
                color_continuous_scale=color_scale
            )
        else:
            fig = px.bar(
                df_plot,
                x=cat_col,
                y=num_col,
                title=config.get("title", f"{num_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}"),
                template="plotly_white",
                color=num_col,
                color_continuous_scale=color_scale
            )

        # Add value labels
        fig.update_traces(
            texttemplate='%{y:,.0f}' if len(df_plot) <= 10 else '%{x:,.0f}',
            textposition='outside'
        )

        # Add statistical annotations
        if stats_dict:
            mean_val = stats_dict.get("mean")
            if mean_val:
                if len(df_plot) <= 10:
                    # Add mean line for vertical bars
                    fig.add_hline(
                        y=mean_val,
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Mean: {mean_val:,.0f}",
                        annotation_position="right"
                    )
                else:
                    # Add mean line for horizontal bars
                    fig.add_vline(
                        x=mean_val,
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Mean: {mean_val:,.0f}",
                        annotation_position="top"
                    )

        # Highlight outliers if present
        outliers = profiler_results.get("outliers", {}).get(num_col, {})
        if outliers and outliers.get("count", 0) > 0:
            outlier_values = outliers.get("values", [])
            for val in outlier_values[:5]:  # Limit to 5 annotations
                if len(df_plot) <= 10:
                    fig.add_annotation(
                        x=df_plot[df_plot[num_col] == val][cat_col].iloc[0] if len(df_plot[df_plot[num_col] == val]) > 0 else None,
                        y=val,
                        text="Outlier",
                        showarrow=True,
                        arrowhead=2,
                        bgcolor="yellow",
                        opacity=0.7
                    )

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

    def _create_enhanced_line_chart(
        self,
        df: pd.DataFrame,
        config: Dict[str, Any],
        profiler_results: Dict[str, Any]
    ) -> Tuple[go.Figure, Dict[str, Any]]:
        """Create enhanced interactive line chart with trend analysis"""
        # Find datetime column
        datetime_cols = profiler_results.get("datetime_columns", [])
        if not datetime_cols:
            # Try to detect
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    datetime_cols.append(col)
                elif df[col].dtype == 'object':
                    try:
                        df[col] = pd.to_datetime(df[col], errors='raise', format='mixed')
                        datetime_cols.append(col)
                    except (ValueError, TypeError):
                        pass

        if not datetime_cols:
            datetime_cols = [df.columns[0]]
        
        datetime_col = datetime_cols[0]
        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if not numerical_cols:
            return None, {}
        
        # Sort by datetime
        df_plot = df.sort_values(by=datetime_col).copy()

        # Create figure with subplots if multiple series
        if len(numerical_cols) > 1:
            fig = make_subplots(
                rows=len(numerical_cols),
                cols=1,
                subplot_titles=[col.replace('_', ' ').title() for col in numerical_cols],
                vertical_spacing=0.1
            )
            for i, num_col in enumerate(numerical_cols, 1):
                fig.add_trace(
                    go.Scatter(
                        x=df_plot[datetime_col],
                        y=df_plot[num_col],
                        mode='lines+markers',
                        name=num_col.replace('_', ' ').title(),
                        line=dict(width=3),
                        marker=dict(size=6)
                    ),
                    row=i, col=1
                )
            fig.update_layout(
                title=config.get("title", "Trend Over Time"),
                height=300 * len(numerical_cols),
                showlegend=True
            )
        else:
            fig = px.line(
                df_plot,
                x=datetime_col,
                y=numerical_cols[0],
                title=config.get("title", "Trend Over Time"),
                template="plotly_white",
                markers=True
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=8))

        # Add trend line if enough data points
        if len(df_plot) > 3 and len(numerical_cols) == 1:
            num_col = numerical_cols[0]
            # Simple linear trend
            x_numeric = pd.to_numeric(pd.to_datetime(df_plot[datetime_col]))
            z = np.polyfit(x_numeric, df_plot[num_col], 1)
            p = np.poly1d(z)
            
            fig.add_trace(
                go.Scatter(
                    x=df_plot[datetime_col],
                    y=p(x_numeric),
                    mode='lines',
                    name='Trend',
                    line=dict(dash='dash', color='red', width=2),
                    showlegend=True
                )
            )

        # Add annotations for peaks/valleys if data is not too large
        if len(df_plot) < 100 and len(numerical_cols) == 1:
            num_col = numerical_cols[0]
            max_idx = df_plot[num_col].idxmax()
            min_idx = df_plot[num_col].idxmin()
            
            fig.add_annotation(
                x=df_plot.loc[max_idx, datetime_col],
                y=df_plot.loc[max_idx, num_col],
                text=f"Peak: {df_plot.loc[max_idx, num_col]:,.0f}",
                showarrow=True,
                arrowhead=2,
                bgcolor="green",
                opacity=0.7
            )
            
            if max_idx != min_idx:
                fig.add_annotation(
                    x=df_plot.loc[min_idx, datetime_col],
                    y=df_plot.loc[min_idx, num_col],
                    text=f"Low: {df_plot.loc[min_idx, num_col]:,.0f}",
                    showarrow=True,
                    arrowhead=2,
                    bgcolor="red",
                    opacity=0.7
                )

        fig.update_layout(
            hovermode='x unified',
            xaxis_title=datetime_col.replace('_', ' ').title(),
            yaxis_title="Value" if len(numerical_cols) == 1 else "",
            height=500 if len(numerical_cols) == 1 else 300 * len(numerical_cols),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig, {"chart_type": "line"}

    def _create_enhanced_pie_chart(
        self,
        df: pd.DataFrame,
        config: Dict[str, Any],
        profiler_results: Dict[str, Any]
    ) -> Tuple[go.Figure, Dict[str, Any]]:
        """Create enhanced interactive pie chart"""
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
            hole=0.3
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Value: %{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
        )
        fig.update_layout(height=500)

        return fig, {"chart_type": "pie"}

    def _create_enhanced_scatter_chart(
        self,
        df: pd.DataFrame,
        config: Dict[str, Any],
        profiler_results: Dict[str, Any]
    ) -> Tuple[go.Figure, Dict[str, Any]]:
        """Create enhanced interactive scatter plot with correlation"""
        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()

        if len(numerical_cols) < 2:
            return None, {}

        x_col, y_col = numerical_cols[0], numerical_cols[1]

        # Sample if too many points
        df_plot = df.copy()
        sampled = False
        if len(df_plot) > 1000:
            df_plot = df_plot.sample(n=1000, random_state=42)
            sampled = True

        fig = px.scatter(
            df_plot,
            x=x_col,
            y=y_col,
            title=config.get("title", f"{x_col.replace('_', ' ').title()} vs {y_col.replace('_', ' ').title()}"),
            template="plotly_white",
            trendline="ols",
            opacity=0.6
        )

        # Add correlation coefficient annotation
        corr = df_plot[x_col].corr(df_plot[y_col])
        fig.add_annotation(
            x=0.02,
            y=0.98,
            xref="paper",
            yref="paper",
            text=f"Correlation: {corr:.2f}",
            showarrow=False,
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
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
            "sample_size": 1000 if sampled else len(df),
            "correlation": float(corr)
        }

        return fig, metadata

    def _create_enhanced_histogram(
        self,
        df: pd.DataFrame,
        config: Dict[str, Any],
        profiler_results: Dict[str, Any]
    ) -> Tuple[go.Figure, Dict[str, Any]]:
        """Create enhanced interactive histogram with statistical markers"""
        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not numerical_cols:
            return None, {}

        num_col = numerical_cols[0]
        stats_dict = profiler_results.get("statistics", {}).get(num_col, {})

        fig = px.histogram(
            df,
            x=num_col,
            title=config.get("title", f"Distribution of {num_col.replace('_', ' ').title()}"),
            template="plotly_white",
            nbins=30,
            marginal="box"
        )

        # Add statistical markers
        if stats_dict:
            mean_val = stats_dict.get("mean")
            median_val = stats_dict.get("median")
            
            if mean_val:
                fig.add_vline(
                    x=mean_val,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Mean: {mean_val:,.0f}",
                    annotation_position="top"
                )
            
            if median_val and median_val != mean_val:
                fig.add_vline(
                    x=median_val,
                    line_dash="dot",
                    line_color="blue",
                    annotation_text=f"Median: {median_val:,.0f}",
                    annotation_position="bottom"
                )

        fig.update_layout(
            xaxis_title=num_col.replace('_', ' ').title(),
            yaxis_title="Frequency",
            height=500,
            showlegend=False
        )

        return fig, {"chart_type": "histogram"}

    def _create_heatmap(
        self,
        df: pd.DataFrame,
        config: Dict[str, Any],
        profiler_results: Dict[str, Any]
    ) -> Tuple[go.Figure, Dict[str, Any]]:
        """Create correlation heatmap"""
        numerical_cols = profiler_results.get("numeric_columns", [])
        
        if len(numerical_cols) < 2:
            return None, {}

        numeric_df = df[numerical_cols].select_dtypes(include=[np.number])
        corr_matrix = numeric_df.corr()

        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title=config.get("title", "Correlation Matrix"),
            template="plotly_white",
            color_continuous_scale="RdBu",
            color_continuous_midpoint=0
        )

        fig.update_layout(height=500)

        return fig, {"chart_type": "heatmap"}

    def _create_boxplot(
        self,
        df: pd.DataFrame,
        config: Dict[str, Any],
        profiler_results: Dict[str, Any]
    ) -> Tuple[go.Figure, Dict[str, Any]]:
        """Create box plot"""
        categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()

        if len(categorical_cols) == 0 or len(numerical_cols) == 0:
            return None, {}

        cat_col = categorical_cols[0]
        num_col = numerical_cols[0]

        fig = px.box(
            df,
            x=cat_col,
            y=num_col,
            title=config.get("title", f"Distribution of {num_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}"),
            template="plotly_white"
        )

        fig.update_layout(
            xaxis_title=cat_col.replace('_', ' ').title(),
            yaxis_title=num_col.replace('_', ' ').title(),
            height=500
        )

        return fig, {"chart_type": "box"}

    def _generate_basic_insights(self, df: pd.DataFrame, chart_type: str, query: str) -> str:
        """Generate basic rule-based insights"""
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
