import pandas as pd
import matplotlib.pyplot as plt
from Evtx.Evtx import Evtx
import xml.etree.ElementTree as ET

evtx_file = r"C:\Users\lasse\Desktop\TraineeLand\Internship-TraineeLand\Alllog-16062026_users.evtx"
events = []

with Evtx(evtx_file) as log:
    for record in log.records():
        try:
            root = ET.fromstring(record.xml())

            system = root.find(".//{*}System")
            eventdata = root.find(".//{*}EventData")

            event_id = system.find(".//{*}EventID").text
            time = system.find(".//{*}TimeCreated").attrib.get("SystemTime") 
            data = {}
            if eventdata is not None:
                for d in eventdata:
                    data[d.attrib.get("Name")] = d.text

            events.append({
                "event_id": event_id,
                "time": time,
                "username": data.get("TargetUserName"),
                "ip": data.get("IpAddress"),
                "workstation": data.get("WorkstationName"),
                "logon_type": data.get("LogonType"),
                "status": data.get("Status"),
            })

        except Exception:
            continue

df = pd.DataFrame(events)

event_map = {
    "4624": "Login réussi",
    "4625": "Login échoué",
}

df["event_name"] = df["event_id"].map(event_map).fillna("Autre événement")

counts = df["event_name"].value_counts()

plt.bar(counts.index, counts.values)

plt.title("Windows Login Events")
plt.xlabel("Event Type")
plt.ylabel("Count")
plt.savefig(r"C:\Users\lasse\Desktop\TraineeLand\Internship-TraineeLand\graph_users.pdf")