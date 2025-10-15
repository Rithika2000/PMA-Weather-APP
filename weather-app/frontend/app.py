import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime
from io import BytesIO
from typing import Optional, Tuple
import streamlit.components.v1 as components
from fpdf import FPDF
import json
import urllib.parse

# ---------- Config ----------
BACKEND = st.secrets.get("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Weather App", page_icon="⛅")
st.title("⛅ Weather App")
st.caption("Built by **Rithika Gurram**")

with st.expander("ℹ️ About PM Accelerator"):
    st.write("Product Manager Accelerator — see LinkedIn page **Product Manager Accelerator** for the company’s description.")
    st.link_button("**Product Manager Accelerator Linkedin Page**", "https://www.linkedin.com/school/pmaccelerator/")
# ---------- Weather code added icons ----------
WEATHER_MAP = [
    (set([0]), ("☀️", "Clear sky")),
    (set([1, 2]), ("🌤️", "Mostly clear / Partly cloudy")),
    (set([3]), ("☁️", "Overcast")),
    (set([45, 48]), ("🌫️", "Fog / Depositing rime fog")),
    (set([51, 53, 55]), ("🌦️", "Drizzle")),
    (set([56, 57]), ("🌧️", "Freezing drizzle")),
    (set([61, 63, 65]), ("🌧️", "Rain")),
    (set([66, 67]), ("🌧️❄️", "Freezing rain")),
    (set([71, 73, 75]), ("❄️", "Snowfall")),
    (set([77]), ("🌨️", "Snow grains")),
    (set([80, 81, 82]), ("🌧️🌦️", "Rain showers")),
    (set([85, 86]), ("🌨️", "Snow showers")),
    (set([95]), ("⛈️", "Thunderstorm")),
    (set([96, 97, 99]), ("⛈️❄️", "Thunderstorm with hail")),
]
def icon_and_label_from_code(code: int) -> Tuple[str, str]:
    for codes, (icon, label) in WEATHER_MAP:
        if code in codes:
            return icon, label
    return "❓", "Unknown"

# ---------- Backend helpers ----------
def api(path: str, params=None, method="GET", json_body=None, timeout=20):
    url = f"{BACKEND}{path}"
    if method == "GET":
        r = requests.get(url, params=params, timeout=timeout)
    elif method == "POST":
        r = requests.post(url, params=params, json=json_body, timeout=timeout)
    elif method == "PATCH":
        r = requests.patch(url, params=params, json=json_body, timeout=timeout)
    elif method == "DELETE":
        r = requests.delete(url, params=params, timeout=timeout)
    else:
        raise ValueError("unsupported method")
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


# Tech Assessment 1 — Live Weather 
# -----------------------------------------------------------
st.header("Live Weather Updates")

left, right = st.columns([3, 1])
with left:
    location = st.text_input(
        "Location",
        placeholder="e.g., 78701 or 'Austin, TX' or 'Eiffel Tower' or '40.7128,-74.0060'",
        key="ta1_loc",
    )
with right:
    use_ip = st.button("📍 Use my current location (IP)")

show_forecast = st.checkbox("Show 5-day forecast", value=True)

resolved = None
if use_ip:
    with st.spinner("Detecting approximate location from IP..."):
        resolved = api("/weather/ip")
        if not resolved:
            st.error("Couldn’t detect your location by IP. Try entering a city or GPS like '40.7,-74.0'.")
else:
    if st.button("Get Weather"):
        if not (location or "").strip():
            st.error("Please enter a location.")
            st.stop()
        with st.spinner("Resolving location..."):
            resolved = api("/weather/geocode", params={"q": location.strip()})
        if not resolved:
            st.error("Couldn't find that location. Try a more specific place or GPS like '40.7,-74.0'.")

if resolved:
    st.success(f"Resolved location: **{resolved['name']}** ({resolved['lat']:.4f}, {resolved['lon']:.4f})")

    with st.spinner("Fetching current weather..."):
        try:
            cur_payload = api("/weather/current", params={"lat": resolved["lat"], "lon": resolved["lon"]})["payload"].get("current_weather", {})
        except Exception as e:
            st.error(f"API error (current weather): {e}")
            st.stop()

    if cur_payload:
        code = cur_payload.get("weathercode")
        icon, label = icon_and_label_from_code(int(code)) if code is not None else ("❓", "Unknown")

        st.subheader("Current Weather")
        st.markdown(f"<div style='font-size: 48px; line-height:1'>{icon}</div>", unsafe_allow_html=True)
        st.write(label)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temperature (°C)", cur_payload.get("temperature"))
        col2.metric("Wind (km/h)", cur_payload.get("windspeed"))
        col3.metric("Direction (°)", cur_payload.get("winddirection"))

        as_of = cur_payload.get("time")
        try:
            t = datetime.fromisoformat(as_of)
            as_of_fmt = t.strftime("%b %d, %Y %H:%M")
        except Exception:
            as_of_fmt = as_of
        col4.metric("As of", as_of_fmt)

    if show_forecast:
        with st.spinner("Fetching 5-day forecast..."):
            try:
                daily = api("/weather/forecast", params={"lat": resolved["lat"], "lon": resolved["lon"], "days": 5})["payload"].get("daily", {})
            except Exception as e:
                st.error(f"API error (forecast): {e}")
                st.stop()

        if daily:
            st.subheader("5-Day Forecast")
            df = pd.DataFrame(daily)
            if "time" in df.columns and not df.empty:
                df = df.head(5)

                def _icon_label(c):
                    try:
                        ic, lab = icon_and_label_from_code(int(c))
                        return ic, lab
                    except Exception:
                        return "❓", "Unknown"

                icons, labels = zip(*df["weathercode"].map(_icon_label))
                df.insert(1, "Icon", list(icons))
                df.insert(2, "Summary", list(labels))
                df.rename(
                    columns={
                        "time": "Date",
                        "temperature_2m_max": "Max °C",
                        "temperature_2m_min": "Min °C",
                        "precipitation_sum": "Precip (mm)",
                        "windspeed_10m_max": "Max Wind (km/h)",
                    },
                    inplace=True,
                )
                st.dataframe(
                    df[["Date", "Icon", "Summary", "Max °C", "Min °C", "Precip (mm)", "Max Wind (km/h)"]],
                    use_container_width=True
                )


# Tech Assessment 2 — CRUD & Integrations & Export data
# -----------------------------------------------------------
st.header("CRUD Operations — Advanced")

tab_create, tab_read, tab_update, tab_delete, tab_integrations, tab_export = st.tabs(
    ["CREATE", "READ", "UPDATE", "DELETE", "Integrations", "Export"]
)

# -------------------- CREATE --------------------
with tab_create:
    st.subheader("Save a range query to DB")
    c1, c2 = st.columns(2)
    with c1:
        create_loc = st.text_input("Location (for DB save)", key="create_loc")
    with c2:
        today = date.today()
        start_d = st.date_input("Start date", value=today, key="create_start")
        end_d = st.date_input("End date", value=today, key="create_end")
    if st.button("Fetch range & Save"):
        if not create_loc.strip():
            st.error("Please enter a location.")
            st.stop()
        if end_d < start_d:
            st.error("End date must be after or equal to Start date.")
            st.stop()
        try:
            body = {"input_location": create_loc.strip(), "start_date": str(start_d), "end_date": str(end_d)}
            # call range to validate and get payload
            resp = api("/weather/range", method="POST", json_body=body)
            if resp is None:
                st.error("Create failed: location not found or backend returned 404")
                st.stop()
            payload = resp.get("payload")
            if payload is None:
                st.error("Create failed: unexpected response from backend")
                st.stop()
            # store in DB
            body2 = {
                "input_location": create_loc.strip(),
                "start_date": str(start_d),
                "end_date": str(end_d),
                "kind": "range",
                "resolved_name": payload.get("resolved", {}).get("name"),
                "lat": payload.get("resolved", {}).get("lat"),
                "lon": payload.get("resolved", {}).get("lon"),
                "result_payload": payload,
            }
            rec = api("/records", method="POST", json_body=body2)
            st.success(f"Saved record #{rec['id']} ✅")
            if payload.get("daily"):
                st.write("**Saved Daily Summary (first rows)**")
                st.dataframe(pd.DataFrame(payload["daily"]).head(10), use_container_width=True)
        except Exception as e:
            st.error(f"Create failed: {e}")

# -------------------- READ --------------------
with tab_read:
    st.subheader("Browse saved records")
    try:
        rows = api("/records")
    except Exception as e:
        rows = []
        st.error(f"Read failed: {e}")
    if not rows:
        st.info("No records yet. Use CREATE to save one.")
    else:
        table = [{
            "id": r["id"],
            "when_saved": r["created_at"].replace("T", " ").split(".")[0],
            "input_location": r["input_location"],
            "resolved_name": r["resolved_name"],
            "lat": round(r["lat"], 4),
            "lon": round(r["lon"], 4),
            "kind": r["kind"],
            "start_date": r["start_date"],
            "end_date": r["end_date"],
        } for r in rows]
        df_rows = pd.DataFrame(table)
        st.dataframe(df_rows, use_container_width=True)

        sel = st.selectbox(
            "Select a record to view payload",
            options=[(r["id"], r["resolved_name"] or r["input_location"], r["kind"]) for r in rows],
            format_func=lambda x: f"#{x[0]} — {x[1]} ({x[2]})",
            key="read_sel"
        )
        if sel:
            rid = sel[0]
            try:
                rfull = api(f"/records/{rid}")
                # We only stored a subset of fields in the RecordOut, fetch payload with a second call if needed
                # It just display record fields, payload is large and already visible at creation time.
                # react-json-view (used by st.json) expects a JSON object/array as src.
                # If the backend returns a string or other type, render safely.
                if isinstance(rfull, (dict, list)):
                    st.json(rfull)
                else:
                    try:
                        parsed = json.loads(rfull) if isinstance(rfull, str) else None
                        if isinstance(parsed, (dict, list)):
                            st.json(parsed)
                        else:
                            st.text(str(rfull))
                    except Exception:
                        st.text(str(rfull))
            except Exception as e:
                st.error(f"Fetch record failed: {e}")

# -------------------- UPDATE --------------------
with tab_update:
    st.subheader("Update a record")
    u1, u2, u3, u4 = st.columns(4)
    with u1:
        upd_id = st.number_input("Record ID", min_value=1, step=1, key="upd_id")
    with u2:
        upd_input_loc = st.text_input("New input_location (optional)", key="upd_inploc")
    with u3:
        upd_kind = st.selectbox("Kind", options=["range", "current", "forecast"], key="upd_kind")
    with u4:
        refetch = st.checkbox("Re-fetch payload", value=True, key="upd_refetch")
    d1, d2 = st.columns(2)
    with d1:
        upd_start = st.date_input("New start_date (optional)", value=today, key="upd_start")
    with d2:
        upd_end = st.date_input("New end_date (optional)", value=today, key="upd_end")

    if st.button("Apply Update"):
        body = {
            "input_location": upd_input_loc or None,
            "kind": upd_kind,
            "start_date": str(upd_start) if upd_start else None,
            "end_date": str(upd_end) if upd_end else None,
            "refetch": refetch
        }
        try:
            rec = api(f"/records/{int(upd_id)}", method="PATCH", json_body=body)
            st.success("Record updated ✅")
            # react-json-view (used by st.json) expects a JSON object/array as src.
            # If the backend returns a string or other type, render safely.
            if isinstance(rec, (dict, list)):
                st.json(rec)
            else:
                try:
                    parsed = json.loads(rec) if isinstance(rec, str) else None
                    if isinstance(parsed, (dict, list)):
                        st.json(parsed)
                    else:
                        st.text(str(rec))
                except Exception:
                    st.text(str(rec))
        except Exception as e:
            st.error(f"Update failed: {e}")

# -------------------- DELETE --------------------
with tab_delete:
    st.subheader("Delete a record")
    del_id = st.number_input("Record ID to delete", min_value=1, step=1, key="del_id")
    if st.button("Delete"):
        try:
            api(f"/records/{int(del_id)}", method="DELETE")
            st.success("Record deleted 🗑️")
        except Exception as e:
            st.error(f"Delete failed: {e}")

# -------------------- INTEGRATIONS --------------------
with tab_integrations:
    st.subheader("YouTube, Google Search, Map")
    q_default = st.session_state.get("create_loc") or st.session_state.get("ta1_loc") or "Austin, TX"
    q = st.text_input("Query / Location", value=q_default)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Search YouTube"):
            try:
                data = api("/integrations/youtube", params={"q": q})
                items = data.get("items", [])
                if not items:
                    st.info("No videos found.")
                else:
                    for it in items:
                        vid = it["id"]["videoId"]
                        title = it["snippet"]["title"]
                        ch = it["snippet"]["channelTitle"]
                        st.markdown(f"**{title}**  \n_{ch}_")
                        components.html(
                            f"""
                            <div style="position:relative;padding-top:56.25%;margin-bottom:12px;">
                              <iframe src="https://www.youtube.com/embed/{vid}" title="{title}"
                                      style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;"
                                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                      allowfullscreen></iframe>
                            </div>
                            """,
                            height=360,
                        )
            except Exception as e:
                st.error(f"YouTube error: {e}")
    with c2:
        if st.button("Google Search"):
            try:
                data = api("/integrations/google-search", params={"q": q})
                items = data.get("items", [])
                if not items:
                    st.info("No results from Google Custom Search.")
                else:
                    for it in items:
                        title = it.get("title", "Untitled")
                        link = it.get("link", "#")
                        snippet = it.get("snippet", "")
                        st.markdown(f"**[{title}]({link})**  \n{snippet}")
                        st.divider()
            except Exception as e:
                st.error(f"Google CSE error: {e}")
    with c3:
        if st.button("Map Embed"):
            try:
                # Try to geocode first for precise lat/lon
                g = api("/weather/geocode", params={"q": q})
                if g:
                    ms = api("/integrations/map-embed", params={"lat": g["lat"], "lon": g["lon"]})
                else:
                    ms = api("/integrations/map-embed", params={"q": q})
                src = ms["embed"]
                components.html(
                    f"""
                    <div style="position:relative;padding-top:56.25%;">
                      <iframe src="{src}" title="Map"
                              style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;"
                              loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
                    </div>
                    """,
                    height=430,
                )
                # Button to open directly in Google Maps
                if g:
                    st.link_button("Open in Google Maps", f"https://www.google.com/maps/search/?api=1&query={g['lat']}%2C{g['lon']}")
                else:
                    st.link_button("Open in Google Maps", f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(q)}")
            except Exception as e:
                st.error(f"Map error: {e}")

# -------------------- EXPORT --------------------
with tab_export:
    st.subheader("Export saved records")
    try:
        rows = api("/records")
    except Exception as e:
        rows = []
        st.error(f"Load failed: {e}")

    if not rows:
        st.info("No records yet.")
    else:
        df = pd.DataFrame([{
            "id": r["id"],
            "created_at": r["created_at"].replace("T"," ").split(".")[0],
            "input_location": r["input_location"],
            "resolved_name": r["resolved_name"],
            "lat": r["lat"], "lon": r["lon"],
            "kind": r["kind"],
            "start_date": r["start_date"],
            "end_date": r["end_date"],
        } for r in rows])
        st.dataframe(df, use_container_width=True)

        # JSON
        json_bytes = json.dumps(rows, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button("Download JSON", json_bytes, file_name="weather_records.json", mime="application/json")

        # CSV
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv_bytes, file_name="weather_records.csv", mime="text/csv")

        # Markdown
        try:
            md = df.to_markdown(index=False)
            st.download_button("Download Markdown", md.encode("utf-8"), file_name="weather_records.md", mime="text/markdown")
        except Exception as e:
            st.warning(f"Markdown export needs 'tabulate'. Error: {e}")

        # XML
        def to_xml(rows_dict):
            from xml.sax.saxutils import escape
            parts = ["<records>"]
            for row in rows_dict:
                parts.append("  <record>")
                for k, v in row.items():
                    parts.append(f"    <{k}>{escape(str(v))}</{k}>")
                parts.append("  </record>")
            parts.append("</records>")
            return "\n".join(parts)
        xml_str = to_xml(rows).encode("utf-8")
        st.download_button("Download XML", xml_str, file_name="weather_records.xml", mime="application/xml")

        # PDF simple table
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=12)
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, "Weather Records", ln=1)
        headers = ["id","created_at","input_location","resolved_name","lat","lon","kind","start_date","end_date"]
        colw = [10, 36, 34, 34, 16, 16, 18, 22, 22]
        for h, w in zip(headers, colw):
            pdf.cell(w, 8, h, border=1)
        pdf.ln(8)
        for r in rows:
            cells = [str(r.get(h, "")) for h in headers]
            for text, w in zip(cells, colw):
                text = (text[:int(w*1.6)] + "…") if len(text) > int(w*1.6) else text
                pdf.cell(w, 8, text, border=1)
            pdf.ln(8)
        pdf_bytes = pdf.output(dest="S").encode("latin1", "ignore")
        st.download_button("Download PDF", pdf_bytes, file_name="weather_records.pdf", mime="application/pdf")

st.markdown("---")

