def rule_explain(event, score):
    reasons = []
    if event["bytes"] > 100000:
        reasons.append("unusually large bytes transferred")
    if event["pkts"] > 2000:
        reasons.append("very high packet count")
    if event["flags"] == "SYN":
        reasons.append("SYN flag present (possible scan or DDoS)")
    if not reasons:
        reasons = ["statistical anomaly compared to baseline"]
    text = f"Anomaly score {score:.3f}: " + "; ".join(reasons) + ". Recommended action: investigate source IP, block if malicious, and enrich with logs."
    return text

# If you have an LLM API, craft prompt like:
def llm_prompt(event, score):
    return f"""You are a cybersecurity analyst. An incoming network event has anomaly score {score:.3f}.
Event: {event}
Explain in 2 sentences why this is suspicious and suggest one immediate mitigation step."""
