def before_send(event, hint):
    log_entry = event.get("logentry", {})
    message = log_entry.get("message", "")

    # Remove the unwanted string if it exists at the beginning of the message
    unwanted_prefix = "============================================================"
    if message.startswith(unwanted_prefix):
        log_entry["message"] = message[len(unwanted_prefix):]

    return event
