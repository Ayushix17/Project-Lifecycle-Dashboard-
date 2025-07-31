import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import random

# Set page config
st.set_page_config(
    page_title="Project Lifecycle Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem;
}
.risk-high { color: #ff4444; }
.risk-medium { color: #ffaa00; }
.risk-low { color: #00aa00; }
.status-delayed { color: #ff4444; }
.status-on-track { color: #00aa00; }
.status-at-risk { color: #ffaa00; }
</style>
""", unsafe_allow_html=True)

class ProjectAnalyticsDashboard:
    def __init__(self):
        self.projects = self.generate_sample_data()
        self.stakeholder_feedback = self.generate_feedback_data()
    
    def generate_sample_data(self):
        """Generate sample project data"""
        np.random.seed(42)
        projects = []
        
        project_names = [
            "Digital Transformation Initiative", "Customer Portal Upgrade", 
            "Mobile App Development", "Data Analytics Platform", 
            "Cloud Migration Project", "Security Enhancement", 
            "AI/ML Implementation", "Process Automation", 
            "Infrastructure Modernization", "User Experience Redesign"
        ]
        
        statuses = ["On Track", "At Risk", "Delayed", "Completed"]
        phases = ["Planning", "Development", "Testing", "Deployment", "Maintenance"]
        risk_levels = ["Low", "Medium", "High"]
        
        for i, name in enumerate(project_names):
            start_date = datetime.now() - timedelta(days=random.randint(30, 365))
            duration = random.randint(90, 365)
            end_date = start_date + timedelta(days=duration)
            
            project = {
                "project_id": f"PRJ-{1000 + i}",
                "project_name": name,
                "status": random.choice(statuses),
                "phase": random.choice(phases),
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "budget": random.randint(50000, 500000),
                "spent": random.randint(20000, 400000),
                "progress": random.randint(10, 100),
                "risk_level": random.choice(risk_levels),
                "team_size": random.randint(3, 15),
                "stakeholder_satisfaction": random.uniform(2.5, 5.0),
                "delay_days": random.randint(-10, 60) if random.choice([True, False]) else 0
            }
            
            # Calculate derived metrics
            project["budget_utilization"] = (project["spent"] / project["budget"]) * 100
            project["days_remaining"] = (end_date - datetime.now()).days
            project["cost_overrun"] = max(0, project["spent"] - project["budget"])
            
            projects.append(project)
        
        df = pd.DataFrame(projects)
        # Convert date strings back to datetime for calculations
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['end_date'] = pd.to_datetime(df['end_date'])
        
        return df
    
    def generate_feedback_data(self):
        """Generate sample stakeholder feedback data"""
        feedback_types = ["Quality", "Timeline", "Communication", "Budget", "Scope"]
        sentiments = ["Positive", "Neutral", "Negative"]
        
        feedback = []
        for _ in range(50):
            feedback.append({
                "project_id": random.choice(self.projects["project_id"].tolist()),
                "feedback_type": random.choice(feedback_types),
                "sentiment": random.choice(sentiments),
                "rating": random.randint(1, 5),
                "date": datetime.now() - timedelta(days=random.randint(1, 90)),
                "comment": f"Sample feedback comment {random.randint(1, 100)}"
            })
        
        return pd.DataFrame(feedback)
    
    def calculate_health_score(self, row):
        """Calculate project health score based on multiple factors"""
        score = 100
        
        # Budget factor
        if row["budget_utilization"] > 100:
            score -= 30
        elif row["budget_utilization"] > 80:
            score -= 15
        
        # Risk factor
        risk_penalties = {"High": 25, "Medium": 15, "Low": 5}
        score -= risk_penalties.get(row["risk_level"], 0)
        
        # Progress vs time factor (simplified calculation)
        if row["progress"] < 50 and row["days_remaining"] < 30:
            score -= 20
        
        # Delay factor
        if row["delay_days"] > 0:
            score -= min(20, row["delay_days"] / 5)
        
        return max(0, score)
    
    def render_overview_metrics(self):
        """Render key performance indicators"""
        st.subheader("📈 Key Performance Indicators")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_projects = len(self.projects)
        active_projects = len(self.projects[self.projects["status"] != "Completed"])
        avg_health = self.projects.apply(self.calculate_health_score, axis=1).mean()
        total_budget = self.projects["budget"].sum()
        total_spent = self.projects["spent"].sum()
        
        with col1:
            st.metric("Total Projects", total_projects)
        
        with col2:
            st.metric("Active Projects", active_projects)
        
        with col3:
            st.metric("Avg Health Score", f"{avg_health:.1f}")
        
        with col4:
            st.metric("Total Budget", f"${total_budget:,.0f}")
        
        with col5:
            st.metric("Budget Utilization", f"{(total_spent/total_budget)*100:.1f}%")
    
    def render_project_health_overview(self):
        """Render project health overview charts"""
        st.subheader("🎯 Project Health Overview")
        
        # Calculate health scores
        self.projects["health_score"] = self.projects.apply(self.calculate_health_score, axis=1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Health score distribution
            fig_health = px.histogram(
                self.projects, 
                x="health_score",
                nbins=10,
                title="Project Health Score Distribution",
                color_discrete_sequence=["#3498db"]
            )
            fig_health.update_layout(
                xaxis_title="Health Score",
                yaxis_title="Number of Projects"
            )
            st.plotly_chart(fig_health, use_container_width=True)
        
        with col2:
            # Risk level distribution
            risk_counts = self.projects["risk_level"].value_counts()
            fig_risk = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                title="Project Risk Distribution",
                color_discrete_map={"High": "#e74c3c", "Medium": "#f39c12", "Low": "#27ae60"}
            )
            st.plotly_chart(fig_risk, use_container_width=True)
    
    def render_cost_analysis(self):
        """Render cost and budget analysis"""
        st.subheader("💰 Cost & Budget Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Budget vs Spent
            fig_budget = go.Figure()
            fig_budget.add_trace(go.Bar(
                name='Budget',
                x=self.projects["project_name"],
                y=self.projects["budget"],
                marker_color='lightblue'
            ))
            fig_budget.add_trace(go.Bar(
                name='Spent',
                x=self.projects["project_name"],
                y=self.projects["spent"],
                marker_color='darkblue'
            ))
            
            fig_budget.update_layout(
                title="Budget vs Actual Spending by Project",
                xaxis_title="Projects",
                yaxis_title="Amount ($)",
                barmode='group',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_budget, use_container_width=True)
        
        with col2:
            # Budget utilization scatter
            fig_util = px.scatter(
                self.projects,
                x="progress",
                y="budget_utilization",
                size="team_size",
                color="risk_level",
                hover_data=["project_name"],
                title="Progress vs Budget Utilization",
                color_discrete_map={"High": "#e74c3c", "Medium": "#f39c12", "Low": "#27ae60"}
            )
            fig_util.add_hline(y=100, line_dash="dash", line_color="red", 
                              annotation_text="Budget Limit")
            st.plotly_chart(fig_util, use_container_width=True)
    
    def render_timeline_analysis(self):
        """Render timeline and delay analysis"""
        st.subheader("⏱️ Timeline & Delay Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Project status distribution over time
            status_counts = self.projects['status'].value_counts()
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Project Status Distribution",
                color_discrete_map={
                    "On Track": "#27ae60",
                    "At Risk": "#f39c12",
                    "Delayed": "#e74c3c",
                    "Completed": "#95a5a6"
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Delay analysis
            delayed_projects = self.projects[self.projects["delay_days"] > 0]
            if not delayed_projects.empty:
                fig_delay = px.bar(
                    delayed_projects,
                    x="project_name",
                    y="delay_days",
                    title="Project Delays (Days)",
                    color="delay_days",
                    color_continuous_scale="Reds"
                )
                fig_delay.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_delay, use_container_width=True)
            else:
                st.info("No projects are currently delayed!")
        
        # Project timeline table
        st.subheader("📅 Project Timeline Details")
        timeline_data = self.projects[['project_name', 'status', 'phase', 'progress', 'days_remaining']].copy()
        timeline_data['days_remaining'] = timeline_data['days_remaining'].astype(int)
        timeline_data = timeline_data.sort_values('days_remaining')
        st.dataframe(timeline_data, use_container_width=True)
    
    def render_stakeholder_feedback(self):
        """Render stakeholder feedback analysis"""
        st.subheader("👥 Stakeholder Feedback Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Feedback sentiment over time
            feedback_timeline = self.stakeholder_feedback.groupby([
                self.stakeholder_feedback["date"].dt.date, "sentiment"
            ]).size().reset_index(name="count")
            
            fig_sentiment = px.line(
                feedback_timeline,
                x="date",
                y="count",
                color="sentiment",
                title="Stakeholder Feedback Sentiment Trends",
                color_discrete_map={
                    "Positive": "#27ae60",
                    "Neutral": "#3498db",
                    "Negative": "#e74c3c"
                }
            )
            st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with col2:
            # Feedback by category
            feedback_category = self.stakeholder_feedback.groupby([
                "feedback_type", "sentiment"
            ]).size().reset_index(name="count")
            
            fig_category = px.bar(
                feedback_category,
                x="feedback_type",
                y="count",
                color="sentiment",
                title="Feedback Distribution by Category",
                color_discrete_map={
                    "Positive": "#27ae60",
                    "Neutral": "#3498db",
                    "Negative": "#e74c3c"
                }
            )
            st.plotly_chart(fig_category, use_container_width=True)
    
    def render_risk_analysis(self):
        """Render detailed risk analysis"""
        st.subheader("⚠️ Risk Analysis & Early Warning System")
        
        # Identify high-risk projects
        high_risk_projects = self.projects[
            (self.projects["risk_level"] == "High") |
            (self.projects["budget_utilization"] > 90) |
            (self.projects["delay_days"] > 30)
        ].copy()
        
        if not high_risk_projects.empty:
            st.warning(f"🚨 {len(high_risk_projects)} projects require immediate attention!")
            
            # Risk matrix
            fig_risk_matrix = px.scatter(
                self.projects,
                x="budget_utilization",
                y="delay_days",
                size="team_size",
                color="risk_level",
                hover_data=["project_name", "health_score"],
                title="Risk Matrix: Budget Utilization vs Delays",
                color_discrete_map={"High": "#e74c3c", "Medium": "#f39c12", "Low": "#27ae60"}
            )
            
            fig_risk_matrix.add_vline(x=100, line_dash="dash", line_color="red")
            fig_risk_matrix.add_hline(y=30, line_dash="dash", line_color="red")
            fig_risk_matrix.add_annotation(x=110, y=45, text="High Risk Zone", 
                                         showarrow=False, bgcolor="rgba(255,0,0,0.1)")
            
            st.plotly_chart(fig_risk_matrix, use_container_width=True)
            
            # High-risk projects table
            st.subheader("High-Risk Projects Details")
            risk_display = high_risk_projects[[
                "project_name", "status", "risk_level", "budget_utilization", 
                "delay_days", "health_score"
            ]].copy()
            risk_display["health_score"] = risk_display["health_score"].round(1)
            risk_display["budget_utilization"] = risk_display["budget_utilization"].round(1)
            
            st.dataframe(risk_display, use_container_width=True)
        else:
            st.success("✅ No high-risk projects identified!")
    
    def render_project_details(self):
        """Render detailed project information"""
        st.subheader("📋 Project Details")
        
        # Project selector
        selected_project = st.selectbox(
            "Select a project for detailed analysis:",
            self.projects["project_name"].tolist()
        )
        
        project_data = self.projects[self.projects["project_name"] == selected_project].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", project_data["status"])
            st.metric("Progress", f"{project_data['progress']}%")
            st.metric("Team Size", project_data["team_size"])
        
        with col2:
            st.metric("Budget", f"${project_data['budget']:,.0f}")
            st.metric("Spent", f"${project_data['spent']:,.0f}")
            st.metric("Utilization", f"{project_data['budget_utilization']:.1f}%")
        
        with col3:
            st.metric("Risk Level", project_data["risk_level"])
            st.metric("Health Score", f"{self.calculate_health_score(project_data):.1f}")
            st.metric("Days Remaining", project_data["days_remaining"])
        
        # Project-specific feedback
        project_feedback = self.stakeholder_feedback[
            self.stakeholder_feedback["project_id"] == project_data["project_id"]
        ]
        
        if not project_feedback.empty:
            st.subheader("Recent Stakeholder Feedback")
            for _, feedback in project_feedback.head(3).iterrows():
                sentiment_color = {"Positive": "🟢", "Neutral": "🟡", "Negative": "🔴"}
                st.write(f"{sentiment_color[feedback['sentiment']]} **{feedback['feedback_type']}** "
                        f"(Rating: {feedback['rating']}/5) - {feedback['comment']}")

def main():
    st.title("📊 Project Lifecycle Analytics Dashboard")
    st.markdown("Monitor project health metrics, stakeholder feedback, and identify risks early")
    
    # Initialize dashboard
    dashboard = ProjectAnalyticsDashboard()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Status filter
    status_filter = st.sidebar.multiselect(
        "Project Status",
        options=dashboard.projects["status"].unique(),
        default=dashboard.projects["status"].unique()
    )
    
    # Risk filter
    risk_filter = st.sidebar.multiselect(
        "Risk Level",
        options=dashboard.projects["risk_level"].unique(),
        default=dashboard.projects["risk_level"].unique()
    )
    
    # Apply filters
    filtered_projects = dashboard.projects[
        (dashboard.projects["status"].isin(status_filter)) &
        (dashboard.projects["risk_level"].isin(risk_filter))
    ]
    dashboard.projects = filtered_projects
    
    # Main dashboard sections
    dashboard.render_overview_metrics()
    
    st.divider()
    dashboard.render_project_health_overview()
    
    st.divider()
    dashboard.render_cost_analysis()
    
    st.divider()
    dashboard.render_timeline_analysis()
    
    st.divider()
    dashboard.render_stakeholder_feedback()
    
    st.divider()
    dashboard.render_risk_analysis()
    
    st.divider()
    dashboard.render_project_details()
    
    # Footer
    st.markdown("---")
    st.markdown("*Dashboard last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*")

if __name__ == "__main__":
    main()