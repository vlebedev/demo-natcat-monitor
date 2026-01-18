"""Streamlit UI for NatCat Event Monitor.

Displays earthquake events on an interactive map with treaty exposure zones
and highlights potential exposures.
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime

from .models import Earthquake, Treaty, ExposureAlert
from .services import find_exposed_treaties, summarize_exposure
from .data import fetch_earthquakes, load_treaties


def get_magnitude_color(magnitude: float) -> str:
    """Return color based on earthquake magnitude."""
    if magnitude >= 6.0:
        return "#dc2626"  # red
    elif magnitude >= 5.0:
        return "#f59e0b"  # amber
    else:
        return "#3b82f6"  # blue


def get_magnitude_radius(magnitude: float) -> int:
    """Return marker radius based on earthquake magnitude."""
    return int(magnitude * 3)


def create_map(
    earthquakes: list[Earthquake],
    treaties: list[Treaty],
    alerts: list[ExposureAlert]
) -> folium.Map:
    """Create Folium map with earthquakes and treaty zones."""
    # Center on Pacific (Ring of Fire)
    m = folium.Map(location=[20, 150], zoom_start=2, tiles="cartodbpositron")

    # Track affected treaty IDs for highlighting
    affected_treaty_ids = {alert.treaty.id for alert in alerts}

    # Add treaty zones as circles
    for treaty in treaties:
        is_affected = treaty.id in affected_treaty_ids
        folium.Circle(
            location=[treaty.latitude, treaty.longitude],
            radius=treaty.radius_km * 1000,  # Convert km to meters
            popup=f"<b>{treaty.name}</b><br>Limit: ${treaty.limit_usd:,}",
            tooltip=treaty.name,
            color="#ef4444" if is_affected else "#6366f1",
            fill=True,
            fill_color="#ef4444" if is_affected else "#6366f1",
            fill_opacity=0.3 if is_affected else 0.15,
            weight=3 if is_affected else 1,
        ).add_to(m)

    # Add earthquake markers
    for eq in earthquakes:
        # Check if this earthquake triggered any alerts
        eq_alerts = [a for a in alerts if a.earthquake.id == eq.id]
        is_triggering = len(eq_alerts) > 0

        popup_html = f"""
        <b>{eq.place}</b><br>
        Magnitude: {eq.magnitude}<br>
        Depth: {eq.depth_km} km<br>
        Time: {eq.time.strftime('%Y-%m-%d %H:%M UTC')}
        """
        if eq_alerts:
            popup_html += "<br><b>Affected treaties:</b><br>"
            for alert in eq_alerts:
                popup_html += f"- {alert.treaty.name}<br>"

        folium.CircleMarker(
            location=[eq.latitude, eq.longitude],
            radius=get_magnitude_radius(eq.magnitude),
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"M{eq.magnitude} - {eq.place}",
            color=get_magnitude_color(eq.magnitude),
            fill=True,
            fill_color=get_magnitude_color(eq.magnitude),
            fill_opacity=0.7,
            weight=2 if is_triggering else 1,
        ).add_to(m)

    return m


def render_summary_panel(
    earthquakes: list[Earthquake],
    alerts: list[ExposureAlert],
    treaties: list[Treaty]
) -> None:
    """Render the summary statistics panel."""
    st.subheader("Summary")

    # Event counts
    total_events = len(earthquakes)
    m4_5 = len([e for e in earthquakes if 4.0 <= e.magnitude < 5.0])
    m5_6 = len([e for e in earthquakes if 5.0 <= e.magnitude < 6.0])
    m6_plus = len([e for e in earthquakes if e.magnitude >= 6.0])

    st.metric("Total Events", total_events)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("M4-5", m4_5)
    with col2:
        st.metric("M5-6", m5_6)
    with col3:
        st.metric("M6+", m6_plus)

    # Exposure summary
    summary = summarize_exposure(alerts)
    affected_treaty_ids = set(a.treaty.id for a in alerts)

    st.metric("Treaties at Risk", len(affected_treaty_ids))
    st.metric("Total Exposure", f"${summary['total_exposure_usd']:,}")


def render_alerts_panel(alerts: list[ExposureAlert]) -> None:
    """Render the exposure alerts panel."""
    st.subheader("Exposure Alerts")

    if not alerts:
        st.info("No exposure alerts at this time.")
        return

    # Sort alerts by exposure (treaty limit) descending
    sorted_alerts = sorted(alerts, key=lambda a: a.treaty.limit_usd, reverse=True)

    for alert in sorted_alerts:
        magnitude_icon = "🔴" if alert.earthquake.magnitude >= 6.0 else "🟡" if alert.earthquake.magnitude >= 5.0 else "🟢"

        with st.container():
            st.markdown(f"""
**{magnitude_icon} M{alert.earthquake.magnitude} {alert.earthquake.place}**
→ {alert.treaty.name}
Exposure: **${alert.treaty.limit_usd:,}**
Distance: {alert.distance_km:.1f} km from zone center
            """)
            st.divider()


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="NatCat Event Monitor",
        page_icon="🌍",
        layout="wide"
    )

    st.title("🌍 NatCat Event Monitor")

    # Controls row
    col_refresh, col_days = st.columns([1, 2])

    with col_refresh:
        refresh_clicked = st.button("🔄 Refresh", type="primary")

    with col_days:
        days = st.selectbox(
            "Time Period",
            options=[7, 14, 30],
            format_func=lambda x: f"Last {x} days",
            index=0
        )

    # Clear cache on refresh
    if refresh_clicked:
        st.cache_data.clear()

    # Fetch data with caching
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def load_data(min_mag: float, num_days: int):
        earthquakes = fetch_earthquakes(min_magnitude=min_mag, days=num_days)
        treaties = load_treaties()
        return earthquakes, treaties

    # Load data
    with st.spinner("Fetching earthquake data from USGS..."):
        try:
            earthquakes, treaties = load_data(4.0, days)
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return

    # Calculate exposure alerts
    all_alerts = []
    for eq in earthquakes:
        alerts = find_exposed_treaties(eq, treaties)
        all_alerts.extend(alerts)

    # Layout: Map on left, panels on right
    map_col, panel_col = st.columns([2, 1])

    with map_col:
        # Create and display map
        m = create_map(earthquakes, treaties, all_alerts)
        st_folium(m, width=None, height=600, returned_objects=[])

    with panel_col:
        render_summary_panel(earthquakes, all_alerts, treaties)
        st.divider()
        render_alerts_panel(all_alerts)

    # Footer
    st.caption(f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} | Data: USGS Earthquake API")


if __name__ == "__main__":
    main()
