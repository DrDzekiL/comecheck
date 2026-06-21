"""
ComeCheck MVP: Local-first alert replay journal for traders.

Alert → Review → Verdict → Learn
"""

import streamlit as st
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# ============================================================================
# CONFIG & PATHS
# ============================================================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
ALERTS_FILE = DATA_DIR / "alerts.jsonl"

VERDICTS = [
    "PENDING_REVIEW",
    "GOOD_ALERT",
    "FALSE_ALERT",
    "MISSED_MOVE",
    "FAILED_SETUP",
    "CLOSED",
]

DIRECTIONS = ["UP", "DOWN"]
ALERT_TYPES = [
    "SUPPORT_BOUNCE",
    "RESISTANCE_BREAK",
    "VOLUME_SPIKE",
    "CHART_PATTERN",
    "LEVEL_TOUCH",
    "OTHER",
]

# ============================================================================
# STORAGE HELPERS
# ============================================================================

def load_alerts() -> List[Dict]:
    """Load all alerts from JSONL file."""
    if not ALERTS_FILE.exists():
        return []
    
    alerts = []
    with open(ALERTS_FILE, "r") as f:
        for line in f:
            if line.strip():
                alerts.append(json.loads(line))
    return alerts

def save_alert(alert: Dict) -> None:
    """Append alert to JSONL file."""
    with open(ALERTS_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")

def update_alert(alert_id: str, updated_fields: Dict) -> None:
    """Update an alert (rewrite entire file)."""
    alerts = load_alerts()
    for alert in alerts:
        if alert["id"] == alert_id:
            alert.update(updated_fields)
            alert["updated_at"] = datetime.utcnow().isoformat() + "Z"
            break
    
    # Rewrite file
    with open(ALERTS_FILE, "w") as f:
        for alert in alerts:
            f.write(json.dumps(alert) + "\n")

# ============================================================================
# BUSINESS LOGIC
# ============================================================================

def create_alert(
    asset: str,
    level: float,
    direction: str,
    alert_type: str,
    trigger_time: str,
    price_at_trigger: float,
    tags: str,
    notes: str,
) -> Dict:
    """Create new alert."""
    now = datetime.utcnow().isoformat() + "Z"
    alert = {
        "id": str(uuid.uuid4()),
        "asset": asset,
        "level": level,
        "direction": direction,
        "alert_type": alert_type,
        "trigger_time": trigger_time,
        "price_at_trigger": price_at_trigger,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "notes": notes,
        "was_user_available": None,
        "what_happened_after": None,
        "verdict": "PENDING_REVIEW",
        "lesson": None,
        "rule_update": None,
        "created_at": now,
        "updated_at": now,
    }
    return alert

def get_stats(alerts: List[Dict]) -> Dict:
    """Calculate dashboard statistics."""
    stats = {
        "total": len(alerts),
        "pending": sum(1 for a in alerts if a.get("verdict") == "PENDING_REVIEW"),
        "good": sum(1 for a in alerts if a.get("verdict") == "GOOD_ALERT"),
        "false": sum(1 for a in alerts if a.get("verdict") == "FALSE_ALERT"),
        "missed": sum(1 for a in alerts if a.get("verdict") == "MISSED_MOVE"),
        "failed": sum(1 for a in alerts if a.get("verdict") == "FAILED_SETUP"),
        "closed": sum(1 for a in alerts if a.get("verdict") == "CLOSED"),
    }
    return stats

def alert_to_markdown(alert: Dict) -> str:
    """Export alert as Markdown."""
    md = f"""# Alert: {alert['asset']} {alert['direction']}

**Trigger:** {alert['trigger_time']}  
**Level:** {alert['level']}  
**Price at Trigger:** {alert['price_at_trigger']}  
**Type:** {alert['alert_type']}  

## Tags
{', '.join(alert.get('tags', []))}

## Notes
{alert.get('notes', '')}

## Review

**Available?** {alert.get('was_user_available', '—')}  
**What Happened:** {alert.get('what_happened_after', '—')}  
**Verdict:** {alert.get('verdict', '—')}  

### Lesson
{alert.get('lesson', '—')}

### Rule Update
{alert.get('rule_update', '—')}

---
*Created: {alert['created_at']}*
"""
    return md

# ============================================================================
# STREAMLIT UI
# ============================================================================

st.set_page_config(page_title="ComeCheck", layout="wide")

st.title("🔔 ComeCheck")
st.markdown("**Local-first alert replay journal** — Did this alert actually matter?")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Add Alert", "Review Queue", "Dashboard", "Export"])

# ============================================================================
# TAB 1: ADD ALERT
# ============================================================================

with tab1:
    st.subheader("Record a New Alert")
    
    col1, col2 = st.columns(2)
    
    with col1:
        asset = st.text_input("Asset", placeholder="BTC/USD, SPY, AAPL")
        direction = st.selectbox("Direction", DIRECTIONS)
        level = st.number_input("Alert Level", step=0.1)
        price_at_trigger = st.number_input("Price at Trigger", step=0.1)
    
    with col2:
        alert_type = st.selectbox("Alert Type", ALERT_TYPES)
        trigger_time = st.text_input(
            "Trigger Time (ISO format)",
            placeholder="2025-06-13T14:30:00Z",
            value=datetime.utcnow().isoformat() + "Z"
        )
        tags = st.text_input("Tags (comma-separated)", placeholder="breakout, daily, support")
    
    notes = st.text_area("Notes", placeholder="Context, reasoning, market structure notes")
    
    if st.button("💾 Save Alert", type="primary"):
        if not asset:
            st.error("Asset is required")
        else:
            alert = create_alert(
                asset=asset,
                level=level,
                direction=direction,
                alert_type=alert_type,
                trigger_time=trigger_time,
                price_at_trigger=price_at_trigger,
                tags=tags,
                notes=notes,
            )
            save_alert(alert)
            st.success(f"✅ Alert saved: {asset} {direction} @ {level}")
            st.balloons()

# ============================================================================
# TAB 2: REVIEW QUEUE
# ============================================================================

with tab2:
    st.subheader("Pending Review Queue")
    
    alerts = load_alerts()
    pending = [a for a in alerts if a.get("verdict") == "PENDING_REVIEW"]
    
    if not pending:
        st.info("No pending alerts. Great job! 🎉")
    else:
        st.write(f"**{len(pending)} alerts pending review**")
        
        for i, alert in enumerate(pending):
            with st.expander(f"{alert['asset']} {alert['direction']} @ {alert['level']} — {alert['trigger_time']}"):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Alert Type:** {alert['alert_type']}")
                    st.write(f"**Notes:** {alert['notes']}")
                    st.write(f"**Tags:** {', '.join(alert.get('tags', []))}")
                
                with col2:
                    st.write(f"**Created:** {alert['created_at']}")
                
                st.divider()
                st.write("**Review This Alert:**")
                
                was_available = st.selectbox(
                    "Were you available when this alert triggered?",
                    [None, "YES", "NO"],
                    key=f"available_{alert['id']}"
                )
                
                what_happened = st.text_area(
                    "What happened after the alert?",
                    placeholder="Price action, validation, invalidation...",
                    key=f"happened_{alert['id']}"
                )
                
                verdict = st.selectbox(
                    "Verdict",
                    VERDICTS[1:],  # Exclude PENDING_REVIEW
                    key=f"verdict_{alert['id']}"
                )
                
                lesson = st.text_area(
                    "Lesson learned (optional)",
                    key=f"lesson_{alert['id']}"
                )
                
                rule_update = st.text_area(
                    "Rule update (optional)",
                    key=f"rule_{alert['id']}"
                )
                
                if st.button("✅ Save Review", key=f"save_{alert['id']}"):
                    update_alert(
                        alert['id'],
                        {
                            "was_user_available": was_available,
                            "what_happened_after": what_happened,
                            "verdict": verdict,
                            "lesson": lesson if lesson else None,
                            "rule_update": rule_update if rule_update else None,
                        }
                    )
                    st.success("Review saved!")
                    st.rerun()

# ============================================================================
# TAB 3: DASHBOARD
# ============================================================================

with tab3:
    st.subheader("Dashboard")
    
    alerts = load_alerts()
    stats = get_stats(alerts)
    
    # Counters
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    with col1:
        st.metric("Total", stats['total'])
    with col2:
        st.metric("⏳ Pending", stats['pending'])
    with col3:
        st.metric("✅ Good", stats['good'])
    with col4:
        st.metric("❌ False", stats['false'])
    with col5:
        st.metric("💤 Missed", stats['missed'])
    with col6:
        st.metric("🔴 Failed", stats['failed'])
    with col7:
        st.metric("🔒 Closed", stats['closed'])
    
    st.divider()
    
    # Recent alerts
    st.write("**Recent Alerts**")
    
    if alerts:
        for alert in reversed(alerts[-10:]):  # Last 10
            status_emoji = {
                "PENDING_REVIEW": "⏳",
                "GOOD_ALERT": "✅",
                "FALSE_ALERT": "❌",
                "MISSED_MOVE": "💤",
                "FAILED_SETUP": "🔴",
                "CLOSED": "🔒",
            }.get(alert.get("verdict"), "?")
            
            st.write(
                f"{status_emoji} **{alert['asset']} {alert['direction']}** @ {alert['level']} "
                f"| {alert['alert_type']} | {alert['trigger_time']}"
            )
    else:
        st.info("No alerts yet")

# ============================================================================
# TAB 4: EXPORT
# ============================================================================

with tab4:
    st.subheader("Export Alerts")
    
    alerts = load_alerts()
    
    if not alerts:
        st.info("No alerts to export")
    else:
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_asset = st.text_input("Filter by asset", placeholder="BTC, SPY...")
        with col2:
            filter_verdict = st.selectbox("Filter by verdict", ["All"] + VERDICTS)
        with col3:
            filter_direction = st.selectbox("Filter by direction", ["All"] + DIRECTIONS)
        
        # Apply filters
        filtered = alerts
        if filter_asset:
            filtered = [a for a in filtered if filter_asset.upper() in a['asset'].upper()]
        if filter_verdict != "All":
            filtered = [a for a in filtered if a.get('verdict') == filter_verdict]
        if filter_direction != "All":
            filtered = [a for a in filtered if a['direction'] == filter_direction]
        
        st.write(f"**{len(filtered)} alert(s) match filters**")
        
        # Select alerts to export
        selected_ids = []
        for alert in filtered:
            if st.checkbox(
                f"{alert['asset']} {alert['direction']} @ {alert['level']} — {alert.get('verdict', 'PENDING')}",
                key=f"export_{alert['id']}"
            ):
                selected_ids.append(alert['id'])
        
        if selected_ids:
            # Generate markdown
            markdown_export = "# ComeCheck Export\n\n"
            csv_export = "id,asset,level,direction,alert_type,trigger_time,price_at_trigger,tags,notes,what_happened_after,verdict,lesson,rule_update,created_at\n"
            for alert in alerts:
                if alert['id'] in selected_ids:
                    markdown_export += alert_to_markdown(alert)
                    markdown_export += "\n\n---\n\n"
                    dt_trigger_time = datetime.fromisoformat(alert['trigger_time'].replace("Z", "+00:00"))
                    formatted_trigger_time = dt_trigger_time.strftime("%Y-%m-%d %H:%M:%S")
                    dt_created_at = datetime.fromisoformat(alert['created_at'].replace("Z", "+00:00"))
                    formatted_created_at = dt_created_at.strftime("%Y-%m-%d %H:%M:%S")
                    csv_export += f"{alert['id']},{alert['asset']},{alert['level']},{alert['direction']},{alert['alert_type']},{formatted_trigger_time},{alert['price_at_trigger']},{','.join(alert.get('tags', []))},{alert.get('notes', '')},{alert.get('what_happened_after', '')},{alert.get('verdict', 'PENDING')},{alert.get('lesson', '')},{alert.get('rule_update', '')},{formatted_created_at}\n"
            
            st.download_button(
                "📥 Download as Markdown",
                markdown_export,
                "comecheck_export.md",
                "text/markdown"
            )
            st.download_button(
                "📥 Export as Csv",
                csv_export,
                "comecheck_export.csv",
                "text/csv"
            )

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown(
    """
    ---
    **ComeCheck** — Local-first alert replay journal  
    📍 Not financial advice  
    🔒 No cloud, no APIs, no signals  
    💾 Data stored locally in `data/alerts.jsonl`
    """
)
