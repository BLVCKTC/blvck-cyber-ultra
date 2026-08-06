import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import type { Scenario } from './soc-scenarios'

// Brand palette (RGB)
const INK: [number, number, number] = [15, 20, 30]
const CYBER: [number, number, number] = [0, 180, 216]
const MUTED: [number, number, number] = [110, 120, 135]
const LIGHT: [number, number, number] = [235, 240, 245]

function incidentId(scenario: Scenario) {
  const n = Math.abs(
    scenario.id.split('').reduce((a, c) => a + c.charCodeAt(0), 0) * 37 + 4021
  )
  return `BLVCK-IR-${n.toString().padStart(6, '0')}`
}

export function generateIncidentPdf(scenario: Scenario) {
  const doc = new jsPDF({ unit: 'pt', format: 'a4' })
  const pageW = doc.internal.pageSize.getWidth()
  const pageH = doc.internal.pageSize.getHeight()
  const margin = 40
  const id = incidentId(scenario)
  const generated = new Date().toLocaleString('en-GB', {
    dateStyle: 'medium',
    timeStyle: 'short',
  })

  // ---- Cover header band ----
  doc.setFillColor(...INK)
  doc.rect(0, 0, pageW, 120, 'F')
  doc.setFillColor(...CYBER)
  doc.rect(0, 120, pageW, 3, 'F')

  doc.setTextColor(...CYBER)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(20)
  doc.text('BLVCK CYBER', margin, 52)
  doc.setTextColor(...LIGHT)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(9)
  doc.text('AI-SOC  |  A BLVCK One Company', margin, 68)

  doc.setTextColor(...LIGHT)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(13)
  doc.text('INCIDENT RESPONSE REPORT', pageW - margin, 52, { align: 'right' })
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(9)
  doc.setTextColor(...CYBER)
  doc.text(id, pageW - margin, 68, { align: 'right' })
  doc.setTextColor(...LIGHT)
  doc.text(`Generated: ${generated}`, pageW - margin, 82, { align: 'right' })

  let y = 150

  // ---- Title block ----
  doc.setTextColor(...INK)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(18)
  doc.text(scenario.name, margin, y)
  y += 20
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.setTextColor(...MUTED)
  doc.text(`${scenario.category}  •  Severity: ${scenario.severity}`, margin, y)
  y += 14
  doc.text(
    `Detected by ${scenario.detectedBy}  •  AI Confidence: ${scenario.confidence}%`,
    margin,
    y
  )
  y += 22

  const sectionHeading = (title: string) => {
    if (y > pageH - 90) {
      doc.addPage()
      y = margin + 10
    }
    doc.setFillColor(...CYBER)
    doc.rect(margin, y - 9, 3, 13, 'F')
    doc.setTextColor(...INK)
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(12)
    doc.text(title, margin + 10, y)
    y += 12
  }

  const paragraph = (text: string) => {
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(10)
    doc.setTextColor(60, 68, 80)
    const lines = doc.splitTextToSize(text, pageW - margin * 2)
    if (y + lines.length * 13 > pageH - 60) {
      doc.addPage()
      y = margin + 10
    }
    doc.text(lines, margin, y)
    y += lines.length * 13 + 8
  }

  const bulletList = (items: string[]) => {
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(10)
    doc.setTextColor(60, 68, 80)
    items.forEach((item) => {
      const lines = doc.splitTextToSize(item, pageW - margin * 2 - 16)
      if (y + lines.length * 13 > pageH - 60) {
        doc.addPage()
        y = margin + 10
      }
      doc.setTextColor(...CYBER)
      doc.text('•', margin + 2, y)
      doc.setTextColor(60, 68, 80)
      doc.text(lines, margin + 16, y)
      y += lines.length * 13 + 4
    })
    y += 6
  }

  const afterTable = () => {
    // @ts-expect-error lastAutoTable is added by the plugin
    y = (doc.lastAutoTable?.finalY ?? y) + 20
  }

  // ---- Executive Summary ----
  sectionHeading('1. Executive Summary')
  paragraph(scenario.execSummary)

  // ---- Incident Timeline ----
  sectionHeading('2. Incident Timeline')
  autoTable(doc, {
    startY: y,
    margin: { left: margin, right: margin },
    head: [['Time', 'Event', 'Detail']],
    body: scenario.timeline.map((t) => [t.time, t.label, t.detail]),
    theme: 'grid',
    headStyles: { fillColor: INK, textColor: LIGHT, fontSize: 9 },
    bodyStyles: { fontSize: 9, textColor: [55, 62, 74] },
    alternateRowStyles: { fillColor: [244, 247, 250] },
    columnStyles: { 0: { cellWidth: 60, textColor: CYBER, fontStyle: 'bold' } },
  })
  afterTable()

  // ---- Root Cause Analysis ----
  sectionHeading('3. Root Cause Analysis')
  paragraph(scenario.rootCause)

  // ---- Attack Chain ----
  sectionHeading('4. Attack Chain')
  autoTable(doc, {
    startY: y,
    margin: { left: margin, right: margin },
    head: [['Phase', 'Technique', 'Detail']],
    body: scenario.attackChain.map((p) => [p.phase, p.technique, p.detail]),
    theme: 'grid',
    headStyles: { fillColor: INK, textColor: LIGHT, fontSize: 9 },
    bodyStyles: { fontSize: 9, textColor: [55, 62, 74] },
    alternateRowStyles: { fillColor: [244, 247, 250] },
    columnStyles: { 0: { cellWidth: 110, fontStyle: 'bold' } },
  })
  afterTable()

  // ---- MITRE ATT&CK Mapping ----
  sectionHeading('5. MITRE ATT&CK Mapping')
  autoTable(doc, {
    startY: y,
    margin: { left: margin, right: margin },
    head: [['ID', 'Tactic', 'Technique']],
    body: scenario.mitre.map((m) => [m.id, m.tactic, m.technique]),
    theme: 'grid',
    headStyles: { fillColor: INK, textColor: LIGHT, fontSize: 9 },
    bodyStyles: { fontSize: 9, textColor: [55, 62, 74] },
    alternateRowStyles: { fillColor: [244, 247, 250] },
    columnStyles: { 0: { cellWidth: 70, textColor: CYBER, fontStyle: 'bold' } },
  })
  afterTable()

  // ---- Systems & Accounts Affected ----
  sectionHeading('6. Systems & Accounts Affected')
  autoTable(doc, {
    startY: y,
    margin: { left: margin, right: margin },
    head: [['Asset', 'Type', 'Status']],
    body: [
      ...scenario.affectedSystems.map((s) => [s.name, s.type, s.status]),
      ...scenario.affectedAccounts.map((a) => [a.name, a.type, a.status]),
    ],
    theme: 'grid',
    headStyles: { fillColor: INK, textColor: LIGHT, fontSize: 9 },
    bodyStyles: { fontSize: 9, textColor: [55, 62, 74] },
    alternateRowStyles: { fillColor: [244, 247, 250] },
    columnStyles: { 2: { fontStyle: 'bold' } },
  })
  afterTable()

  // ---- Indicators of Compromise ----
  sectionHeading('7. Indicators of Compromise (IOCs)')
  autoTable(doc, {
    startY: y,
    margin: { left: margin, right: margin },
    head: [['Type', 'Indicator']],
    body: scenario.iocs.map((i) => [i.type, i.value]),
    theme: 'grid',
    headStyles: { fillColor: INK, textColor: LIGHT, fontSize: 9 },
    bodyStyles: { fontSize: 9, textColor: [55, 62, 74], font: 'courier' },
    alternateRowStyles: { fillColor: [244, 247, 250] },
    columnStyles: { 0: { cellWidth: 110, fontStyle: 'bold', textColor: CYBER } },
  })
  afterTable()

  // ---- Containment ----
  sectionHeading('8. Containment Recommendations')
  bulletList(scenario.containment)

  // ---- Recovery ----
  sectionHeading('9. Recovery Steps')
  bulletList(scenario.recovery)

  // ---- Lessons Learned ----
  sectionHeading('10. Lessons Learned')
  bulletList(scenario.lessons)

  // ---- Footer on every page ----
  const pageCount = doc.getNumberOfPages()
  for (let p = 1; p <= pageCount; p++) {
    doc.setPage(p)
    doc.setDrawColor(220, 226, 232)
    doc.line(margin, pageH - 34, pageW - margin, pageH - 34)
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(8)
    doc.setTextColor(...MUTED)
    doc.text(
      `${id}  •  CONFIDENTIAL — BLVCK CYBER Incident Response`,
      margin,
      pageH - 20
    )
    doc.text(`Page ${p} of ${pageCount}`, pageW - margin, pageH - 20, { align: 'right' })
  }

  doc.save(`${id}-${scenario.id}-incident-report.pdf`)
}
