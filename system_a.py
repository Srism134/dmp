# system_a.py — Exporter with JSON/XML "bundle"
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
import xml.etree.ElementTree as ET

app = FastAPI()
DUMMY_TOKEN = "dev-token"

# simple in-memory data
PATIENTS = {
    "P-001": {"id": "P-001", "name": [{"text": "Patient P-001"}], "birthDate": "1985-03-18"},
    "P-002": {"id": "P-002", "name": [{"text": "Patient P-002"}], "birthDate": "1990-05-12"},
    "P-003": {"id": "P-003", "name": [{"text": "Patient P-003"}], "birthDate": "1978-09-22"},
    "P-004": {"id": "P-004", "name": [{"text": "Patient P-004"}], "birthDate": "1988-01-10"},
    "P-005": {"id": "P-005", "name": [{"text": "Patient P-005"}], "birthDate": "1992-07-03"},
    "P-006": {"id": "P-006", "name": [{"text": "Patient P-006"}], "birthDate": "1981-11-25"},
    "P-007": {"id": "P-007", "name": [{"text": "Patient P-007"}], "birthDate": "1975-04-30"},
    "P-008": {"id": "P-008", "name": [{"text": "Patient P-008"}], "birthDate": "1996-02-14"},
    "P-009": {"id": "P-009", "name": [{"text": "Patient P-009"}], "birthDate": "1983-06-18"},
    "P-010": {"id": "P-010", "name": [{"text": "Patient P-010"}], "birthDate": "1979-12-05"},
}


def bundle_for(pid: str) -> dict:
    patient = PATIENTS.get(pid)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {
        "passportVersion": "0.1",
        "patient": {
            "resourceType": "Patient",
            "id": patient["id"],
            "name": patient.get("name", []),
            "birthDate": patient.get("birthDate", "")
        },
        "medications": [],
        "immunizations": [],
        "encounters": [],
        "observations": []
    }

def dict_to_xml(tag: str, d: dict) -> ET.Element:
    """Very simple dict->xml for our fixed bundle structure."""
    root = ET.Element(tag)
    # passportVersion
    pv = ET.SubElement(root, "passportVersion")
    pv.text = str(d.get("passportVersion", ""))
    # patient
    p = d.get("patient", {})
    pnode = ET.SubElement(root, "patient")
    for k in ("resourceType", "id", "birthDate"):
        c = ET.SubElement(pnode, k)
        c.text = str(p.get(k, ""))
    # name array -> name[0].text only (simple demo)
    names = p.get("name", [])
    name_text = names[0]["text"] if names else ""
    name_el = ET.SubElement(pnode, "nameText")
    name_el.text = name_text
    # arrays (empty)
    for arr_key in ("medications", "immunizations", "encounters", "observations"):
        ET.SubElement(root, arr_key)  # empty container
    return root

@app.get("/patients/{patient_id}/passport")
def export_passport(patient_id: str, request: Request, format: str = "json"):
    bundle = bundle_for(patient_id)
    wants_xml = (format.lower() == "xml") or (request.headers.get("accept", "").lower() == "application/xml")
    if wants_xml:
        xml_elem = dict_to_xml("passport", bundle)
        xml_bytes = ET.tostring(xml_elem, encoding="utf-8")
        return Response(content=xml_bytes, media_type="application/xml")
    return JSONResponse(bundle)
