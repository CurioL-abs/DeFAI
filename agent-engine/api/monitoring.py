from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from models import (
    Agent, AgentStatus, AgentPerformance, PortfolioSnapshot, StrategyExecution,
    LeaderboardEntry, get_db_session
)
from middleware.auth import get_current_user

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user)
):
    """Get dashboard statistics for user's agents"""
    try:
        # Get user's agents
        agents = await Agent.get_by_owner(session, current_user)
        
        # Count by status
        status_counts = {}
        for status in AgentStatus:
            status_counts[status.value] = sum(1 for agent in agents if agent.status == status)
        
        # Calculate total metrics
        total_profit = sum(agent.total_profit for agent in agents)
        total_trades = sum(agent.total_trades for agent in agents)
        avg_success_rate = (
            sum(agent.success_rate for agent in agents) / len(agents)
        ) if agents else 0
        
        # Get recent performance
        recent_executions = []
        for agent in agents[:5]:  # Top 5 agents by recent activity
            agent_executions = await StrategyExecution.get_by_agent(session, agent.id, limit=5)
            recent_executions.extend(agent_executions)
        
        # Sort by start time, most recent first
        recent_executions.sort(key=lambda x: x.start_time, reverse=True)
        recent_executions = recent_executions[:10]  # Limit to 10 most recent
        
        return {
            "user_stats": {
                "total_agents": len(agents),
                "active_agents": status_counts.get("active", 0),
                "paused_agents": status_counts.get("paused", 0),
                "stopped_agents": status_counts.get("stopped", 0),
                "total_profit": round(total_profit, 4),
                "total_trades": total_trades,
                "avg_success_rate": round(avg_success_rate, 2)
            },
            "agent_status_breakdown": status_counts,
            "top_performing_agents": [
                {
                    "id": agent.id,
                    "name": agent.name,
                    "total_profit": agent.total_profit,
                    "success_rate": agent.success_rate,
                    "total_trades": agent.total_trades,
                    "status": agent.status
                }
                for agent in sorted(agents, key=lambda x: x.total_profit, reverse=True)[:5]
            ],
            "recent_executions": [
                {
                    "id": execution.id,
                    "agent_id": execution.agent_id,
                    "strategy_type": execution.strategy_type,
                    "start_time": execution.start_time.isoformat(),
                    "profit": execution.profit,
                    "success": execution.success
                }
                for execution in recent_executions
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard stats: {str(e)}"
        )

@router.get("/leaderboard")
async def get_leaderboard(
    session: AsyncSession = Depends(get_db_session),
    period_days: int = Query(7, le=365, description="Period for leaderboard calculation"),
    limit: int = Query(20, le=100, description="Number of top agents to return")
):
    """Get leaderboard of top performing agents"""
    try:
        # Get top performers from performance records
        performance_records = await AgentPerformance.get_top_performers(session, period_days, limit * 2)
        
        # Group by agent and calculate totals
        agent_performance = {}
        for record in performance_records:
            agent_id = record.agent_id
            if agent_id not in agent_performance:
                agent_performance[agent_id] = {
                    "agent_id": agent_id,
                    "total_profit": 0,
                    "total_trades": 0,
                    "successful_trades": 0,
                    "roi_percent": 0,
                    "days_active": 0
                }
            
            agent_performance[agent_id]["total_profit"] += record.total_profit
            agent_performance[agent_id]["total_trades"] += record.trades_count
            agent_performance[agent_id]["successful_trades"] += record.successful_trades
            agent_performance[agent_id]["roi_percent"] += record.roi_percent
            agent_performance[agent_id]["days_active"] += 1
        
        # Calculate averages and get agent details
        leaderboard_entries = []
        for agent_id, perf in agent_performance.items():
            agent = await Agent.get(session, agent_id)
            if not agent:
                continue
                
            # Only include public agents or user's own agents in leaderboard
            # For simplicity, including all for now
            
            avg_roi = perf["roi_percent"] / perf["days_active"] if perf["days_active"] > 0 else 0
            success_rate = (
                (perf["successful_trades"] / perf["total_trades"]) * 100 
                if perf["total_trades"] > 0 else 0
            )
            
            # Simple risk score calculation
            risk_score = {
                "low": 0.2,
                "medium": 0.5,
                "high": 0.8
            }.get(agent.risk_level.value.lower(), 0.5)
            
            leaderboard_entries.append({
                "agent_id": agent_id,
                "agent_name": agent.name,
                "owner_id": agent.owner_id,
                "period_return": perf["total_profit"],
                "total_trades": perf["total_trades"],
                "success_rate": round(success_rate, 2),
                "avg_daily_roi": round(avg_roi, 2),
                "risk_score": risk_score,
                "strategy_type": agent.strategy_type
            })
        
        # Sort by total profit descending
        leaderboard_entries.sort(key=lambda x: x["period_return"], reverse=True)
        
        # Add rank
        for i, entry in enumerate(leaderboard_entries[:limit], 1):
            entry["rank"] = i
        
        return {
            "period_days": period_days,
            "leaderboard": leaderboard_entries[:limit],
            "last_updated": "2025-01-01T00:00:00"  # In production, track actual update time
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get leaderboard: {str(e)}"
        )

@router.get("/system-health")
async def get_system_health(
    session: AsyncSession = Depends(get_db_session)
):
    """Get overall system health metrics"""
    try:
        # Get all agents
        active_agents = await Agent.get_active_agents(session)
        
        # Get recent executions to check system activity
        recent_executions = await StrategyExecution.get_recent(session, hours=1, limit=100)
        
        # Calculate health metrics
        total_active_agents = len(active_agents)
        executions_last_hour = len(recent_executions)
        successful_executions = sum(1 for ex in recent_executions if ex.success)
        success_rate = (
            (successful_executions / executions_last_hour) * 100 
            if executions_last_hour > 0 else 0
        )
        
        # System health score (simplified)
        health_score = 100
        if total_active_agents == 0:
            health_score -= 30
        if executions_last_hour < 5:
            health_score -= 20
        if success_rate < 80:
            health_score -= 25
        
        health_status = "healthy"
        if health_score < 70:
            health_status = "degraded"
        if health_score < 50:
            health_status = "unhealthy"
        
        return {
            "system_status": health_status,
            "health_score": max(health_score, 0),
            "metrics": {
                "total_agents": total_active_agents,
                "active_agents": total_active_agents,
                "executions_last_hour": executions_last_hour,
                "success_rate_last_hour": round(success_rate, 2),
                "total_profit_last_hour": round(
                    sum(ex.profit for ex in recent_executions), 4
                )
            },
            "services": {
                "database": "healthy",  # Would implement actual health checks
                "ai_service": "healthy",
                "solana_rpc": "healthy",
                "data_feeds": "healthy"
            },
            "last_updated": "2025-01-01T00:00:00"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}"
        )

@router.get("/alerts")
async def get_system_alerts(
    session: AsyncSession = Depends(get_db_session),
    severity: str = Query("all", description="Filter by severity: all, high, medium, low"),
    limit: int = Query(50, le=100, description="Maximum number of alerts to return")
):
    """Get system alerts and notifications"""
    try:
        # In a real implementation, this would fetch from an alerts/notifications table
        # For now, we'll generate mock alerts based on recent activity
        
        alerts = []
        
        # Check for agents with errors
        agents = await Agent.get_active_agents(session)
        for agent in agents:
            recent_executions = await StrategyExecution.get_by_agent(session, agent.id, limit=5)
            failed_executions = [ex for ex in recent_executions if not ex.success]
            
            if len(failed_executions) >= 3:  # 3 or more recent failures
                alerts.append({
                    "id": f"agent_failures_{agent.id}",
                    "type": "agent_performance",
                    "severity": "high",
                    "title": f"Agent {agent.name} experiencing failures",
                    "message": f"Agent has {len(failed_executions)} failed executions recently",
                    "agent_id": agent.id,
                    "timestamp": "2025-01-01T00:00:00",
                    "resolved": False
                })
        
        # Check for agents with unusual profit/loss
        for agent in agents:
            if agent.total_profit < -100:  # Significant losses
                alerts.append({
                    "id": f"agent_losses_{agent.id}",
                    "type": "financial",
                    "severity": "medium",
                    "title": f"Agent {agent.name} has significant losses",
                    "message": f"Total losses: ${abs(agent.total_profit):.2f}",
                    "agent_id": agent.id,
                    "timestamp": "2025-01-01T00:00:00",
                    "resolved": False
                })
        
        # Mock system alerts
        if len(agents) == 0:
            alerts.append({
                "id": "no_active_agents",
                "type": "system",
                "severity": "medium",
                "title": "No active agents",
                "message": "No agents are currently active in the system",
                "timestamp": "2025-01-01T00:00:00",
                "resolved": False
            })
        
        # Filter by severity
        if severity != "all":
            alerts = [alert for alert in alerts if alert["severity"] == severity]
        
        # Apply limit
        alerts = alerts[:limit]
        
        return {
            "alerts": alerts,
            "total_count": len(alerts),
            "unresolved_count": sum(1 for alert in alerts if not alert["resolved"]),
            "severity_counts": {
                "high": sum(1 for alert in alerts if alert["severity"] == "high"),
                "medium": sum(1 for alert in alerts if alert["severity"] == "medium"),
                "low": sum(1 for alert in alerts if alert["severity"] == "low")
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alerts: {str(e)}"
        )

@router.get("/portfolio-overview")
async def get_portfolio_overview(
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user)
):
    """Get portfolio overview across all user's agents"""
    try:
        # Get user's agents
        agents = await Agent.get_by_owner(session, current_user)
        
        total_portfolio_value = 0
        total_agents = len(agents)
        agent_portfolios = []
        
        # Get latest portfolio snapshot for each agent
        for agent in agents:
            latest_snapshot = await PortfolioSnapshot.get_latest_by_agent(session, agent.id)
            
            portfolio_value = latest_snapshot.total_value_usd if latest_snapshot else 0
            total_portfolio_value += portfolio_value
            
            agent_portfolios.append({
                "agent_id": agent.id,
                "agent_name": agent.name,
                "status": agent.status,
                "portfolio_value": portfolio_value,
                "total_profit": agent.total_profit,
                "success_rate": agent.success_rate,
                "last_active": agent.last_active_at.isoformat() if agent.last_active_at else None,
                "positions": latest_snapshot.positions if latest_snapshot else {},
                "sol_balance": latest_snapshot.sol_balance if latest_snapshot else 0
            })
        
        # Sort by portfolio value
        agent_portfolios.sort(key=lambda x: x["portfolio_value"], reverse=True)
        
        # Calculate allocation breakdown
        active_agents_value = sum(
            p["portfolio_value"] for p in agent_portfolios 
            if p["status"] == AgentStatus.ACTIVE
        )
        
        return {
            "total_portfolio_value": round(total_portfolio_value, 2),
            "total_agents": total_agents,
            "active_agents": sum(1 for p in agent_portfolios if p["status"] == AgentStatus.ACTIVE),
            "total_profit": round(sum(agent.total_profit for agent in agents), 4),
            "allocation": {
                "active_trading": round(active_agents_value, 2),
                "inactive": round(total_portfolio_value - active_agents_value, 2)
            },
            "agent_portfolios": agent_portfolios[:10],  # Top 10 by value
            "last_updated": "2025-01-01T00:00:00"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio overview: {str(e)}"
        )

@router.get("/performance-metrics")
async def get_performance_metrics(
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user),
    days: int = Query(30, le=365, description="Number of days for performance calculation")
):
    """Get detailed performance metrics for user's agents"""
    try:
        # Get user's agents
        agents = await Agent.get_by_owner(session, current_user)
        
        if not agents:
            return {
                "period_days": days,
                "total_profit": 0,
                "total_trades": 0,
                "avg_success_rate": 0,
                "best_performer": None,
                "worst_performer": None,
                "daily_performance": [],
                "strategy_performance": {}
            }
        
        # Get performance data for all agents
        all_performance = []
        for agent in agents:
            performance_records = await AgentPerformance.get_agent_history(session, agent.id, days)
            all_performance.extend(performance_records)
        
        # Calculate total metrics
        total_profit = sum(record.total_profit for record in all_performance)
        total_trades = sum(record.trades_count for record in all_performance)
        total_successful = sum(record.successful_trades for record in all_performance)
        avg_success_rate = (total_successful / total_trades * 100) if total_trades > 0 else 0
        
        # Find best and worst performers
        agents_by_profit = sorted(agents, key=lambda x: x.total_profit, reverse=True)
        best_performer = {
            "agent_id": agents_by_profit[0].id,
            "agent_name": agents_by_profit[0].name,
            "total_profit": agents_by_profit[0].total_profit
        } if agents_by_profit else None
        
        worst_performer = {
            "agent_id": agents_by_profit[-1].id,
            "agent_name": agents_by_profit[-1].name,
            "total_profit": agents_by_profit[-1].total_profit
        } if agents_by_profit else None
        
        # Daily performance aggregation (simplified)
        daily_performance = {}
        for record in all_performance:
            date_str = record.date.isoformat()
            if date_str not in daily_performance:
                daily_performance[date_str] = {
                    "date": date_str,
                    "total_profit": 0,
                    "total_trades": 0,
                    "successful_trades": 0
                }
            daily_performance[date_str]["total_profit"] += record.total_profit
            daily_performance[date_str]["total_trades"] += record.trades_count
            daily_performance[date_str]["successful_trades"] += record.successful_trades
        
        # Sort daily performance by date
        daily_performance_list = sorted(daily_performance.values(), key=lambda x: x["date"])
        
        # Strategy performance breakdown
        strategy_performance = {}
        for agent in agents:
            strategy_type = agent.strategy_type
            if strategy_type not in strategy_performance:
                strategy_performance[strategy_type] = {
                    "total_profit": 0,
                    "agent_count": 0,
                    "avg_profit": 0
                }
            strategy_performance[strategy_type]["total_profit"] += agent.total_profit
            strategy_performance[strategy_type]["agent_count"] += 1
        
        # Calculate averages
        for strategy, data in strategy_performance.items():
            if data["agent_count"] > 0:
                data["avg_profit"] = data["total_profit"] / data["agent_count"]
        
        return {
            "period_days": days,
            "total_profit": round(total_profit, 4),
            "total_trades": total_trades,
            "avg_success_rate": round(avg_success_rate, 2),
            "best_performer": best_performer,
            "worst_performer": worst_performer,
            "daily_performance": daily_performance_list[-30:],  # Last 30 days
            "strategy_performance": {
                k: {
                    "total_profit": round(v["total_profit"], 4),
                    "agent_count": v["agent_count"],
                    "avg_profit": round(v["avg_profit"], 4)
                }
                for k, v in strategy_performance.items()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )
