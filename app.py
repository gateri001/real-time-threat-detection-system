import streamlit as st
import threading, queue, time, json
from data_generator import stream_events
from model import train_model, load_model, score_event
from explainer import rule_explain, llm_prompt
import pandas as pd, numpy as np

st.set_page_config(layout="wide", page_title="SentinelLite")

if "events" not in st.session_state:
    st.session_state.events = []
if "alerts" not in st.session_state:
    st.session_state.alerts = []

q = queue.Queue()

def enqueue(e):
    q.put(e)

# start data stream in background thread
if "stream_thread" not in st.session_state:
    t = threading.Thread(target=stream_events, args=(enqueue,0.15), daemon=True)
    t.start()
    st.session_state.stream_thread = t

# bootstrap training on synthetic normal data
if "model" not in st.session_state:
    # create normal data
    normal = []
    for _ in range(2000):
        e = {"bytes": int(np.random.exponential(300)), "pkts": max(1,int(np.random.exponential(2)))}
        normal.append(e)
    normal_df = pd.DataFrame(normal)
    model = train_model(normal_df)
    st.session_state.model = model

col1, col2 = st.columns([2,1])
with col1:
    st.header("Live Event Stream")
    placeholder = st.empty()
with col2:
    st.header("Alerts")
    alert_box = st.empty()

# pull events from queue
new = []
while not q.empty():
    e = q.get()
    new.append(e)
    # score
    score = score_event(st.session_state.model, e)
    e["score"] = score
    st.session_state.events.append(e)
    # simple threshold for alert
    if score > 0.1:
        expl = rule_explain(e, score)
        e["explanation"] = expl
        st.session_state.alerts.insert(0, e)  # newest first
# show stream
df = pd.DataFrame(st.session_state.events[-200:])[["timestamp","src_ip","dst_ip","bytes","pkts","proto","flags","score"]]
placeholder.dataframe(df)

# show alerts
alerts_df = pd.DataFrame(st.session_state.alerts[:20])
if not alerts_df.empty:
    alert_box.dataframe(alerts_df[["timestamp","src_ip","dst_ip","bytes","pkts","score","explanation"]])
else:
    alert_box.write("No alerts yet")

st.sidebar.markdown("## Controls")
threshold = st.sidebar.slider("Alert threshold (anomaly score)", 0.0, 1.0, 0.1)
st.sidebar.write("Alerts show events with score above threshold")
