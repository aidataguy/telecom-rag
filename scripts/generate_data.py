import json
import random
import uuid
import os
from datetime import datetime, timedelta
from faker import Faker
from tqdm import tqdm

fake = Faker()
random.seed(42)

# ── Domain vocabulary ──────────────────────────────────────────────────────────

NETWORK_ELEMENTS = [
    "BTS", "BSC", "NodeB", "eNodeB", "gNodeB", "MME", "SGW", "PGW",
    "HSS", "PCRF", "OCS", "DRA", "MSC", "HLR", "SGSN", "GGSN",
    "AMF", "SMF", "UPF", "NRF", "AUSF", "UDM", "PCF"
]

ALARM_TYPES = [
    "High CPU utilization", "Low disk space", "Interface down",
    "Packet loss exceeding threshold", "Latency spike detected",
    "Link flapping", "Power unit failure", "Fan failure",
    "Temperature threshold exceeded", "Software crash detected",
    "License expiry warning", "Sync loss on port",
    "VLAN misconfiguration", "BGP session down", "OSPF adjacency lost"
]

RESOLUTION_STEPS = [
    "Restarted the affected process using systemctl restart {svc}",
    "Rolled back configuration to last known good state",
    "Replaced faulty SFP module on port {port}",
    "Cleared ARP cache and re-established BGP session",
    "Escalated to vendor L3 support, TAC case #{case} raised",
    "Applied hotfix patch version {ver} as per vendor advisory",
    "Rerouted traffic to secondary link while primary restored",
    "Increased buffer size from {old}MB to {new}MB",
    "Disabled and re-enabled the NIC driver",
    "Ran diagnostic script, found and cleared stuck threads"
]

RUNBOOK_TYPES = [
    "Incident Response", "Change Management", "Capacity Planning",
    "Disaster Recovery", "Routine Maintenance", "Performance Tuning",
    "Security Patching", "New Site Commissioning", "Decommissioning",
    "Vendor Upgrade Procedure"
]

TECHNOLOGIES = ["2G", "3G", "4G LTE", "5G NR", "VoLTE", "VoNR", "MPLS", "SD-WAN"]

SEVERITIES = ["P1", "P2", "P3", "P4"]
REGIONS = ["North", "South", "East", "West", "Central"]
VENDORS = ["Ericsson", "Nokia", "Huawei", "Cisco", "Juniper", "ZTE"]

# ── Document generators ────────────────────────────────────────────────────────

def generate_incident_report():
    element = random.choice(NETWORK_ELEMENTS)
    alarm = random.choice(ALARM_TYPES)
    severity = random.choice(SEVERITIES)
    region = random.choice(REGIONS)
    vendor = random.choice(VENDORS)
    tech = random.choice(TECHNOLOGIES)
    start = fake.date_time_between(start_date="-2y", end_date="now")
    duration_mins = random.randint(5, 480)
    end = start + timedelta(minutes=duration_mins)
    resolution = random.choice(RESOLUTION_STEPS).format(
        svc=fake.word(), port=f"eth{random.randint(0,48)}",
        case=random.randint(10000, 99999),
        ver=f"{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,9)}",
        old=random.randint(128, 512), new=random.randint(512, 2048)
    )

    return {
        "doc_id": str(uuid.uuid4()),
        "doc_type": "incident_report",
        "title": f"{severity} Incident: {alarm} on {element} [{region}]",
        "content": f"""
INCIDENT REPORT
===============
Incident ID: INC-{random.randint(100000, 999999)}
Severity: {severity}
Technology: {tech}
Network Element: {element} (Vendor: {vendor})
Region: {region}
Affected Site ID: SITE-{random.randint(1000, 9999)}

TIMELINE
--------
Detection Time: {start.strftime('%Y-%m-%d %H:%M:%S')}
Resolution Time: {end.strftime('%Y-%m-%d %H:%M:%S')}
Total Duration: {duration_mins} minutes

DESCRIPTION
-----------
Alarm Type: {alarm}
A {severity} priority incident was triggered when {alarm.lower()} was detected on
{element} unit in the {region} region. The affected equipment is supplied by {vendor}
and supports {tech} services. Downstream impact was observed on approximately
{random.randint(100, 50000)} subscribers.

ROOT CAUSE ANALYSIS
-------------------
Root cause identified as {fake.sentence(nb_words=12).lower().rstrip('.')} leading to
degradation of {tech} services. The issue was traced to the {element} subsystem
responsible for {fake.bs()}.

RESOLUTION
----------
{resolution}
Post-resolution validation confirmed all KPIs returned to baseline within
{random.randint(2, 30)} minutes of fix application.

PREVENTIVE ACTIONS
------------------
1. {fake.sentence(nb_words=10)}
2. Monitoring threshold adjusted from {random.randint(70,85)}% to {random.randint(60,75)}%
3. Runbook updated to include this scenario.
        """.strip(),
        "metadata": {
            "severity": severity, "region": region, "vendor": vendor,
            "technology": tech, "network_element": element,
            "duration_minutes": duration_mins,
            "created_at": start.isoformat()
        }
    }


def generate_runbook():
    runbook_type = random.choice(RUNBOOK_TYPES)
    element = random.choice(NETWORK_ELEMENTS)
    vendor = random.choice(VENDORS)
    tech = random.choice(TECHNOLOGIES)
    steps = random.randint(5, 15)

    step_list = "\n".join([
        f"Step {i+1}: {fake.sentence(nb_words=random.randint(8,15))}"
        for i in range(steps)
    ])

    return {
        "doc_id": str(uuid.uuid4()),
        "doc_type": "runbook",
        "title": f"Runbook: {runbook_type} for {element} ({vendor}) [{tech}]",
        "content": f"""
OPERATIONAL RUNBOOK
===================
Runbook ID: RBK-{random.randint(10000, 99999)}
Type: {runbook_type}
Applicable Element: {element}
Vendor: {vendor}
Technology: {tech}
Last Reviewed: {fake.date_this_year().strftime('%Y-%m-%d')}
Author: {fake.name()} ({fake.job()})

PURPOSE
-------
This runbook describes the standard procedure for {runbook_type.lower()} of
{element} nodes in a {tech} environment, as deployed by {vendor}.

PREREQUISITES
-------------
- Access to NMS/EMS portal with write privileges
- VPN connected to management network
- Maintenance window approved (Change ID: CHG-{random.randint(10000,99999)})
- Backup of current configuration taken

PROCEDURE
---------
{step_list}

ROLLBACK PROCEDURE
------------------
Step 1: {fake.sentence(nb_words=10)}
Step 2: Restore configuration from backup taken in prerequisites.
Step 3: Validate service restoration using drive test or OMC KPIs.

VALIDATION CHECKLIST
--------------------
[ ] All alarms cleared in NMS
[ ] KPI thresholds within normal range
[ ] No subscriber complaints in last 15 minutes
[ ] Log entry created in change management system
        """.strip(),
        "metadata": {
            "runbook_type": runbook_type, "vendor": vendor,
            "technology": tech, "network_element": element,
            "created_at": fake.date_time_this_year().isoformat()
        }
    }


def generate_capacity_report():
    region = random.choice(REGIONS)
    tech = random.choice(TECHNOLOGIES)

    return {
        "doc_id": str(uuid.uuid4()),
        "doc_type": "capacity_report",
        "title": f"Capacity Planning Report: {tech} Network — {region} Region Q{random.randint(1,4)}/{datetime.now().year}",
        "content": f"""
CAPACITY PLANNING REPORT
========================
Region: {region}
Technology: {tech}
Reporting Quarter: Q{random.randint(1,4)} {datetime.now().year}
Prepared By: {fake.name()}

EXECUTIVE SUMMARY
-----------------
Current network utilization in the {region} region stands at {random.randint(55,89)}%
of total installed capacity for {tech}. Traffic growth rate is {random.randint(8,35)}%
year-over-year. Based on current trajectory, capacity exhaustion is projected
in {random.randint(6, 36)} months without expansion.

TRAFFIC ANALYSIS
----------------
Peak Throughput: {random.randint(10,500)} Gbps
Average Throughput: {random.randint(5,300)} Gbps
Busy Hour Traffic Volume: {random.randint(50,2000)} TB/day
Number of Active Sites: {random.randint(200,5000)}
Subscriber Base: {random.randint(100000, 5000000)}

BOTTLENECKS IDENTIFIED
----------------------
1. {random.choice(NETWORK_ELEMENTS)} nodes in sub-region {fake.city()} at {random.randint(85,99)}% utilization
2. Backhaul links on {random.choice(['Ring-A', 'Ring-B', 'Ring-C'])} saturating during peak hours
3. {fake.sentence(nb_words=12)}

RECOMMENDATIONS
---------------
1. Add {random.randint(10,100)} new {random.choice(NETWORK_ELEMENTS)} nodes in {region} region
2. Upgrade backhaul from {random.randint(1,10)}G to {random.randint(10,100)}G on critical links
3. Deploy carrier aggregation on {tech} to improve spectral efficiency
4. Estimated CAPEX: INR {random.randint(10,500)} Cr
        """.strip(),
        "metadata": {
            "region": region, "technology": tech,
            "doc_subtype": "capacity",
            "created_at": fake.date_time_this_year().isoformat()
        }
    }


# ── Main generation loop ───────────────────────────────────────────────────────

GENERATORS = [generate_incident_report, generate_runbook, generate_capacity_report]
WEIGHTS = [0.5, 0.3, 0.2]  # 50% incidents, 30% runbooks, 20% capacity

def generate_dataset(total_records: int, output_dir: str, batch_size: int = 10000):
    os.makedirs(output_dir, exist_ok=True)
    batch_num = 0
    batch = []

    print(f"Generating {total_records:,} records...")

    for i in tqdm(range(total_records)):
        generator = random.choices(GENERATORS, weights=WEIGHTS, k=1)[0]
        batch.append(generator())

        if len(batch) >= batch_size:
            out_path = os.path.join(output_dir, f"batch_{batch_num:05d}.jsonl")
            with open(out_path, "w") as f:
                for doc in batch:
                    f.write(json.dumps(doc) + "\n")
            batch = []
            batch_num += 1

    # Write remaining
    if batch:
        out_path = os.path.join(output_dir, f"batch_{batch_num:05d}.jsonl")
        with open(out_path, "w") as f:
            for doc in batch:
                f.write(json.dumps(doc) + "\n")

    print(f"Done. {batch_num + 1} batch files written to {output_dir}/")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=100000, help="Total records to generate")
    parser.add_argument("--output", type=str, default="data/raw", help="Output directory")
    parser.add_argument("--batch-size", type=int, default=10000)
    args = parser.parse_args()

    generate_dataset(args.records, args.output, args.batch_size)
