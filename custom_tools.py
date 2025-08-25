"""
Custom Tools for Agent Farms

This module contains custom tool implementations that can be used
in agent farm configurations.
"""

from crewai.tools import BaseTool
from typing import Type, Any, List
import os
import ast
import subprocess


class CodeAnalysisTool(BaseTool):
    """Tool for analyzing code quality, structure, and patterns."""
    
    name: str = "Code Analysis Tool"
    description: str = "Analyzes code for quality, structure, security issues, and best practices."
    
    def _run(self, code: str, language: str = "python") -> str:
        """Analyze the provided code."""
        try:
            if language.lower() == "python":
                return self._analyze_python_code(code)
            else:
                return self._analyze_generic_code(code, language)
        except Exception as e:
            return f"Error analyzing code: {str(e)}"
    
    def _analyze_python_code(self, code: str) -> str:
        """Analyze Python code specifically."""
        analysis = []
        
        try:
            # Parse the code
            tree = ast.parse(code)
            
            # Count different elements
            functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
            classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
            imports = len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])
            
            analysis.append(f"📊 Code Structure Analysis:")
            analysis.append(f"   • Functions: {functions}")
            analysis.append(f"   • Classes: {classes}")
            analysis.append(f"   • Import statements: {imports}")
            
            # Check for common issues
            issues = []
            
            # Check for long functions (simple heuristic)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                        length = node.end_lineno - node.lineno
                        if length > 50:
                            issues.append(f"Function '{node.name}' is very long ({length} lines)")
            
            # Check for missing docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        issues.append(f"{node.__class__.__name__.replace('Def', '')} '{node.name}' missing docstring")
            
            if issues:
                analysis.append(f"\n⚠️  Potential Issues:")
                for issue in issues[:10]:  # Limit to first 10 issues
                    analysis.append(f"   • {issue}")
            
            # Basic complexity estimation
            complexity_indicators = {
                'if_statements': len([n for n in ast.walk(tree) if isinstance(n, ast.If)]),
                'loops': len([n for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While))]),
                'try_blocks': len([n for n in ast.walk(tree) if isinstance(n, ast.Try)])
            }
            
            analysis.append(f"\n🧮 Complexity Indicators:")
            for indicator, count in complexity_indicators.items():
                analysis.append(f"   • {indicator.replace('_', ' ').title()}: {count}")
            
        except SyntaxError as e:
            analysis.append(f"❌ Syntax Error: {e}")
        
        return "\n".join(analysis)
    
    def _analyze_generic_code(self, code: str, language: str) -> str:
        """Analyze code for non-Python languages."""
        lines = code.split('\n')
        analysis = []
        
        analysis.append(f"📊 General Code Analysis ({language}):")
        analysis.append(f"   • Total lines: {len(lines)}")
        analysis.append(f"   • Non-empty lines: {len([l for l in lines if l.strip()])}")
        analysis.append(f"   • Comment lines: {len([l for l in lines if l.strip().startswith(('//','#','/*','*'))])}")
        
        # Basic pattern detection
        patterns = {
            'function_keywords': ['function', 'def', 'func', 'method', 'procedure'],
            'class_keywords': ['class', 'interface', 'struct'],
            'control_flow': ['if', 'else', 'while', 'for', 'switch', 'case']
        }
        
        analysis.append(f"\n🔍 Pattern Detection:")
        for pattern_type, keywords in patterns.items():
            count = sum(1 for line in lines for keyword in keywords if keyword in line.lower())
            analysis.append(f"   • {pattern_type.replace('_', ' ').title()}: {count}")
        
        return "\n".join(analysis)


class DataAnalysisTool(BaseTool):
    """Tool for analyzing data and generating insights."""
    
    name: str = "Data Analysis Tool"
    description: str = "Analyzes datasets, identifies patterns, and generates statistical insights."
    
    def _run(self, data_description: str, analysis_type: str = "descriptive") -> str:
        """Perform data analysis based on description."""
        try:
            analysis = []
            
            analysis.append(f"📈 Data Analysis Report")
            analysis.append(f"Data: {data_description}")
            analysis.append(f"Analysis Type: {analysis_type}")
            analysis.append("=" * 50)
            
            if analysis_type.lower() == "descriptive":
                analysis.extend(self._descriptive_analysis(data_description))
            elif analysis_type.lower() == "statistical":
                analysis.extend(self._statistical_analysis(data_description))
            elif analysis_type.lower() == "trend":
                analysis.extend(self._trend_analysis(data_description))
            else:
                analysis.append("⚠️  Unknown analysis type. Performing basic analysis.")
                analysis.extend(self._basic_analysis(data_description))
            
            return "\n".join(analysis)
            
        except Exception as e:
            return f"Error in data analysis: {str(e)}"
    
    def _descriptive_analysis(self, data_description: str) -> List[str]:
        """Generate descriptive analysis suggestions."""
        return [
            "\n📊 Descriptive Analysis Recommendations:",
            "   • Calculate central tendency measures (mean, median, mode)",
            "   • Determine variability measures (standard deviation, range)",
            "   • Identify outliers and anomalies",
            "   • Generate frequency distributions",
            "   • Create summary statistics tables",
            "\n💡 Insights to look for:",
            "   • Data distribution patterns",
            "   • Missing or inconsistent values",
            "   • Unusual patterns or anomalies",
            "   • Key performance indicators"
        ]
    
    def _statistical_analysis(self, data_description: str) -> List[str]:
        """Generate statistical analysis suggestions."""
        return [
            "\n📈 Statistical Analysis Recommendations:",
            "   • Perform hypothesis testing",
            "   • Calculate correlation coefficients",
            "   • Conduct regression analysis",
            "   • Apply significance testing",
            "   • Generate confidence intervals",
            "\n🔬 Advanced techniques to consider:",
            "   • ANOVA for group comparisons",
            "   • Chi-square tests for categorical data",
            "   • Time series analysis for temporal data",
            "   • Multivariate analysis for complex relationships"
        ]
    
    def _trend_analysis(self, data_description: str) -> List[str]:
        """Generate trend analysis suggestions."""
        return [
            "\n📈 Trend Analysis Recommendations:",
            "   • Identify seasonal patterns",
            "   • Calculate growth rates and trends",
            "   • Detect cyclical behaviors",
            "   • Forecast future values",
            "   • Analyze trend significance",
            "\n🔮 Forecasting considerations:",
            "   • Moving averages for smoothing",
            "   • Exponential smoothing techniques",
            "   • ARIMA models for complex patterns",
            "   • Confidence intervals for predictions"
        ]
    
    def _basic_analysis(self, data_description: str) -> List[str]:
        """Generate basic analysis suggestions."""
        return [
            "\n📋 Basic Analysis Recommendations:",
            "   • Review data quality and completeness",
            "   • Understand data structure and format",
            "   • Identify key variables and relationships",
            "   • Create initial visualizations",
            "   • Document findings and observations"
        ]


class ChartGenerationTool(BaseTool):
    """Tool for generating chart and visualization recommendations."""
    
    name: str = "Chart Generation Tool"
    description: str = "Suggests appropriate charts and visualizations for different types of data and analysis goals."
    
    def _run(self, data_type: str, analysis_goal: str, data_description: str = "") -> str:
        """Generate chart recommendations."""
        try:
            recommendations = []
            
            recommendations.append(f"📊 Chart Recommendations")
            recommendations.append(f"Data Type: {data_type}")
            recommendations.append(f"Analysis Goal: {analysis_goal}")
            recommendations.append("=" * 50)
            
            # Chart recommendations based on data type and goal
            charts = self._get_chart_recommendations(data_type, analysis_goal)
            
            if charts:
                recommendations.append(f"\n🎨 Recommended Chart Types:")
                for chart in charts:
                    recommendations.append(f"   • {chart}")
            
            # Additional visualization tips
            tips = self._get_visualization_tips(data_type, analysis_goal)
            if tips:
                recommendations.append(f"\n💡 Visualization Tips:")
                for tip in tips:
                    recommendations.append(f"   • {tip}")
            
            # Tool suggestions
            tools = self._get_tool_suggestions()
            recommendations.append(f"\n🛠️  Recommended Tools:")
            for tool in tools:
                recommendations.append(f"   • {tool}")
            
            return "\n".join(recommendations)
            
        except Exception as e:
            return f"Error generating chart recommendations: {str(e)}"
    
    def _get_chart_recommendations(self, data_type: str, analysis_goal: str) -> List[str]:
        """Get specific chart recommendations."""
        charts = []
        
        data_type = data_type.lower()
        analysis_goal = analysis_goal.lower()
        
        if "time" in data_type or "temporal" in data_type:
            charts.extend([
                "Line Chart - Show trends over time",
                "Area Chart - Show cumulative changes",
                "Candlestick Chart - For financial data"
            ])
        
        if "categorical" in data_type or "category" in data_type:
            charts.extend([
                "Bar Chart - Compare categories",
                "Pie Chart - Show proportions (max 5-7 categories)",
                "Donut Chart - Alternative to pie chart"
            ])
        
        if "numerical" in data_type or "continuous" in data_type:
            charts.extend([
                "Histogram - Show distribution",
                "Box Plot - Show quartiles and outliers",
                "Scatter Plot - Show relationships"
            ])
        
        if "comparison" in analysis_goal:
            charts.extend([
                "Bar Chart - Direct comparison",
                "Radar Chart - Multi-dimensional comparison",
                "Parallel Coordinates - Complex comparisons"
            ])
        
        if "correlation" in analysis_goal or "relationship" in analysis_goal:
            charts.extend([
                "Scatter Plot - Show correlation",
                "Correlation Matrix Heatmap - Multiple relationships",
                "Bubble Chart - Three-dimensional relationships"
            ])
        
        if "distribution" in analysis_goal:
            charts.extend([
                "Histogram - Frequency distribution",
                "Violin Plot - Distribution shape",
                "Q-Q Plot - Compare with theoretical distribution"
            ])
        
        return charts[:6]  # Limit to top 6 recommendations
    
    def _get_visualization_tips(self, data_type: str, analysis_goal: str) -> List[str]:
        """Get visualization best practices."""
        return [
            "Use color meaningfully and consistently",
            "Keep titles and labels clear and descriptive",
            "Choose appropriate scales and ranges",
            "Avoid chart junk and unnecessary decorations",
            "Consider your audience when choosing complexity",
            "Use consistent styling across related charts",
            "Ensure accessibility with color-blind friendly palettes"
        ]
    
    def _get_tool_suggestions(self) -> List[str]:
        """Get tool suggestions for creating charts."""
        return [
            "Python: matplotlib, seaborn, plotly, altair",
            "R: ggplot2, plotly, lattice",
            "JavaScript: D3.js, Chart.js, Highcharts",
            "Online: Tableau Public, Google Charts, Canva",
            "Desktop: Excel, Tableau Desktop, Power BI"
        ]
