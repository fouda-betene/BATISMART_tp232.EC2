"""
=============================================================
 BATISMART — Application de Collecte & Analyse des Données
 Établissement de Vente de Matériaux de Construction
 INF232 EC2 | Python Flask | Frontend + Backend
=============================================================
"""

from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import os, uuid, sqlite3
from contextlib import contextmanager

app = Flask(__name__)
app.secret_key = "batismart_inf232_2024"

# ─── TEMPLATE HTML PRINCIPAL ──────────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BATISMART — Gestion Matériaux de Construction</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {
    --primary: #D85A30;
    --primary-light: #F0997B;
    --primary-dark: #993C1D;
    --accent: #1D9E75;
    --accent-light: #9FE1CB;
    --bg: #F7F5F2;
    --surface: #FFFFFF;
    --surface2: #F0EDE8;
    --border: #E2DDD6;
    --text: #1A1714;
    --text2: #6B625A;
    --text3: #9E9890;
    --danger: #E24B4A;
    --warning: #BA7517;
    --success: #3B6D11;
    --info: #185FA5;
    --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.05);
    --shadow-hover: 0 4px 16px rgba(0,0,0,0.12);
    --radius: 12px;
    --radius-sm: 8px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }

  /* SIDEBAR */
  .sidebar {
    position: fixed; top: 0; left: 0; height: 100vh; width: 260px;
    background: var(--text); color: #fff; display: flex; flex-direction: column;
    z-index: 100; transition: transform 0.3s;
  }
  .sidebar-logo {
    padding: 28px 24px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
  }
  .logo-title { font-family: 'Space Grotesk', sans-serif; font-size: 22px; font-weight: 700; color: var(--primary-light); letter-spacing: -0.5px; }
  .logo-sub { font-size: 11px; color: rgba(255,255,255,0.45); text-transform: uppercase; letter-spacing: 1.5px; margin-top: 2px; }
  .sidebar-nav { flex: 1; padding: 16px 12px; overflow-y: auto; }
  .nav-section { font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: rgba(255,255,255,0.35); padding: 12px 12px 6px; }
  .nav-item {
    display: flex; align-items: center; gap: 10px; padding: 10px 12px;
    border-radius: var(--radius-sm); cursor: pointer; color: rgba(255,255,255,0.7);
    font-size: 14px; font-weight: 400; transition: all 0.2s; margin-bottom: 2px;
  }
  .nav-item:hover { background: rgba(255,255,255,0.08); color: #fff; }
  .nav-item.active { background: var(--primary); color: #fff; font-weight: 500; }
  .nav-icon { width: 18px; height: 18px; flex-shrink: 0; }
  .sidebar-footer { padding: 16px 20px; border-top: 1px solid rgba(255,255,255,0.1); }
  .store-badge { background: rgba(255,255,255,0.08); border-radius: var(--radius-sm); padding: 10px 12px; }
  .store-name { font-size: 13px; font-weight: 500; }
  .store-loc { font-size: 11px; color: rgba(255,255,255,0.45); margin-top: 2px; }

  /* MAIN CONTENT */
  .main { margin-left: 260px; min-height: 100vh; }
  .topbar {
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 16px 32px; display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 50;
  }
  .topbar-title { font-family: 'Space Grotesk', sans-serif; font-size: 20px; font-weight: 600; }
  .topbar-date { font-size: 13px; color: var(--text2); }
  .page { display: none; padding: 32px; }
  .page.active { display: block; }

  /* CARDS */
  .card { background: var(--surface); border-radius: var(--radius); padding: 24px; box-shadow: var(--shadow); border: 1px solid var(--border); }
  .card-title { font-family: 'Space Grotesk', sans-serif; font-size: 15px; font-weight: 600; margin-bottom: 16px; color: var(--text); }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
  .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }

  /* STAT CARDS */
  .stat-card { background: var(--surface); border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow); border: 1px solid var(--border); }
  .stat-label { font-size: 12px; color: var(--text2); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }
  .stat-value { font-family: 'Space Grotesk', sans-serif; font-size: 28px; font-weight: 700; color: var(--text); line-height: 1; }
  .stat-sub { font-size: 12px; color: var(--text3); margin-top: 6px; }
  .stat-up { color: var(--success); }
  .stat-down { color: var(--danger); }
  .stat-accent { border-left: 3px solid var(--primary); }
  .stat-green { border-left: 3px solid var(--accent); }
  .stat-blue { border-left: 3px solid var(--info); }
  .stat-warn { border-left: 3px solid var(--warning); }

  /* FORMS */
  .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .form-group { display: flex; flex-direction: column; gap: 6px; }
  .form-group.full { grid-column: 1 / -1; }
  label { font-size: 13px; font-weight: 500; color: var(--text2); }
  input, select, textarea {
    padding: 10px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm);
    font-family: 'DM Sans', sans-serif; font-size: 14px; color: var(--text);
    background: var(--surface); transition: border-color 0.2s, box-shadow 0.2s;
  }
  input:focus, select:focus, textarea:focus {
    outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(216,90,48,0.12);
  }
  textarea { resize: vertical; min-height: 80px; }

  /* BUTTONS */
  .btn { padding: 10px 20px; border: none; border-radius: var(--radius-sm); cursor: pointer; font-family: 'DM Sans', sans-serif; font-size: 14px; font-weight: 500; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; }
  .btn-primary { background: var(--primary); color: #fff; }
  .btn-primary:hover { background: var(--primary-dark); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(216,90,48,0.3); }
  .btn-ghost { background: transparent; color: var(--text); border: 1px solid var(--border); }
  .btn-ghost:hover { background: var(--surface2); }
  .btn-danger { background: var(--danger); color: #fff; }
  .btn-sm { padding: 6px 12px; font-size: 12px; }
  .btn-success { background: var(--accent); color: #fff; }

  /* TABLE */
  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  thead th { text-align: left; padding: 10px 14px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; color: var(--text2); border-bottom: 2px solid var(--border); font-weight: 600; }
  tbody tr { border-bottom: 1px solid var(--border); transition: background 0.15s; }
  tbody tr:hover { background: var(--surface2); }
  tbody td { padding: 12px 14px; color: var(--text); }
  .badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 500; }
  .badge-success { background: #EAF3DE; color: var(--success); }
  .badge-warning { background: #FAEEDA; color: var(--warning); }
  .badge-danger { background: #FCEBEB; color: var(--danger); }
  .badge-info { background: #E6F1FB; color: var(--info); }
  .badge-primary { background: #FAECE7; color: var(--primary); }

  /* ALERT */
  .alert { padding: 12px 16px; border-radius: var(--radius-sm); font-size: 13px; margin-bottom: 16px; display: none; }
  .alert-success { background: #EAF3DE; color: var(--success); border: 1px solid #C0DD97; }
  .alert-danger { background: #FCEBEB; color: var(--danger); border: 1px solid #F7C1C1; }
  .alert-warning { background: #FAEEDA; color: var(--warning); border: 1px solid #FAC775; }
  .alert.show { display: block; }

  /* SEARCH BAR */
  .search-bar { display: flex; gap: 12px; align-items: center; margin-bottom: 20px; flex-wrap: wrap; }
  .search-input { flex: 1; min-width: 200px; }

  /* PROGRESS BAR */
  .progress { background: var(--surface2); border-radius: 20px; height: 6px; overflow: hidden; }
  .progress-bar { height: 100%; border-radius: 20px; background: var(--primary); transition: width 0.4s; }

  /* SUMMARY ROW */
  .sum-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 14px; }
  .sum-row:last-child { border-bottom: none; font-weight: 600; font-size: 15px; padding-top: 12px; }

  /* MODAL */
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 200; display: none; align-items: center; justify-content: center; }
  .modal-overlay.open { display: flex; }
  .modal { background: var(--surface); border-radius: var(--radius); padding: 28px; width: 500px; max-width: 95vw; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
  .modal-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
  .modal-title { font-family: 'Space Grotesk', sans-serif; font-size: 18px; font-weight: 600; }
  .modal-close { background: none; border: none; cursor: pointer; font-size: 22px; color: var(--text2); }

  /* DIVIDER */
  .divider { height: 1px; background: var(--border); margin: 20px 0; }

  /* CHART CONTAINER */
  .chart-container { position: relative; height: 260px; }

  /* STOCK ALERT PILL */
  .stock-critical { color: var(--danger); font-weight: 600; }
  .stock-ok { color: var(--success); }

  /* RESPONSIVE */
  @media (max-width: 768px) {
    .sidebar { transform: translateX(-260px); }
    .main { margin-left: 0; }
    .grid-4 { grid-template-columns: 1fr 1fr; }
    .grid-3 { grid-template-columns: 1fr; }
    .grid-2 { grid-template-columns: 1fr; }
  }

  /* SCROLLBAR */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

  /* ANIMATIONS */
  @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
  .page.active { animation: fadeIn 0.25s ease; }
  .pulse { animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

  /* LOGO MARK */
  .logo-mark { display: inline-flex; align-items: center; gap: 8px; }
  .logo-icon { width: 32px; height: 32px; background: var(--primary); border-radius: 8px; display: flex; align-items: center; justify-content: center; }

  /* EMPTY STATE */
  .empty-state { text-align: center; padding: 60px 20px; color: var(--text3); }
  .empty-state h3 { font-size: 16px; font-weight: 500; margin-bottom: 8px; color: var(--text2); }

  /* PRINT */
  @media print {
    .sidebar, .topbar, .btn, .search-bar { display: none !important; }
    .main { margin-left: 0 !important; }
    .page.active { display: block !important; padding: 0 !important; }
  }
</style>
</head>
<body>

<!-- SIDEBAR -->
<aside class="sidebar">
  <div class="sidebar-logo">
    <div class="logo-mark">
      <div class="logo-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
      </div>
      <div>
        <div class="logo-title">BATISMART</div>
        <div class="logo-sub">Matériaux Construction</div>
      </div>
    </div>
  </div>
  <nav class="sidebar-nav">
    <div class="nav-section">Accueil</div>
    <div class="nav-item active" onclick="showPage('accueil')">
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
      Accueil
    </div>
    <div class="nav-section">Tableau de Bord</div>
    <div class="nav-item" onclick="showPage('dashboard')">
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
      Vue d'ensemble
    </div>

    <div class="nav-section">Collecte</div>
    <div class="nav-item" onclick="showPage('vente')">
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>
      Saisir une Vente
    </div>
    <div class="nav-item" onclick="showPage('client')">
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      Clients
    </div>
    <div class="nav-item" onclick="showPage('stock')">
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
      Stock Produits
    </div>
    <div class="nav-item" onclick="showPage('depense')">
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 100 7h5a3.5 3.5 0 110 7H6"/></svg>
      Dépenses
    </div>

    <div class="nav-section">Analyse</div>
    <div class="nav-item" onclick="showPage('analyse')">
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
      Statistiques
    </div>
    <div class="nav-item" onclick="showPage('historique')">
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
      Historique Ventes
    </div>
  </nav>
  <div class="sidebar-footer">
    <div class="store-badge">
      <div class="store-name">Magasin Principal</div>
      <div class="store-loc">Yaoundé, Cameroun</div>
    </div>
  </div>
</aside>

<!-- MAIN CONTENT -->
<div class="main">
  <div class="topbar">
    <div class="topbar-title" id="page-title">Tableau de Bord</div>
    <div class="topbar-date" id="current-date"></div>
  </div>

  <!-- ══════════════════ ACCUEIL ══════════════════ -->
  <div class="page active" id="page-accueil">
    <div style="min-height:80vh;display:flex;align-items:center;justify-content:center;">
      <div style="text-align:center;max-width:700px;padding:20px;">
        <div style="width:90px;height:90px;background:var(--primary);border-radius:22px;display:flex;align-items:center;justify-content:center;margin:0 auto 28px;">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
        </div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:13px;text-transform:uppercase;letter-spacing:3px;color:var(--text3);margin-bottom:12px;">Bienvenue à</div>
        <h1 style="font-family:'Space Grotesk',sans-serif;font-size:48px;font-weight:700;color:var(--text);line-height:1.1;margin-bottom:8px;">BATISMART</h1>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:18px;color:var(--primary);font-weight:600;margin-bottom:12px;">Matériaux de Construction</div>
        <p style="font-size:15px;color:var(--text2);line-height:1.7;margin-bottom:48px;">
          Votre plateforme de gestion complète pour la collecte et l'analyse<br>des données de votre établissement — Yaoundé, Cameroun.
        </p>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">
          <button onclick="showPage('stock')" style="background:var(--surface);border:2px solid var(--border);border-radius:16px;padding:28px 20px;cursor:pointer;transition:all 0.2s;text-align:center;" onmouseover="this.style.borderColor='var(--primary)';this.style.transform='translateY(-3px)';this.style.boxShadow='0 8px 24px rgba(216,90,48,0.15)'" onmouseout="this.style.borderColor='var(--border)';this.style.transform='';this.style.boxShadow=''">
            <div style="width:52px;height:52px;background:#FAECE7;border-radius:14px;display:flex;align-items:center;justify-content:center;margin:0 auto 14px;">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#D85A30" stroke-width="2">
                <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
              </svg>
            </div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:600;color:var(--text);margin-bottom:6px;">Gestion du Stock</div>
            <div style="font-size:13px;color:var(--text2);">Consulter et mettre à jour les niveaux de stock des produits</div>
          </button>
          <button onclick="showPage('vente')" style="background:var(--surface);border:2px solid var(--border);border-radius:16px;padding:28px 20px;cursor:pointer;transition:all 0.2s;text-align:center;" onmouseover="this.style.borderColor='var(--accent)';this.style.transform='translateY(-3px)';this.style.boxShadow='0 8px 24px rgba(29,158,117,0.15)'" onmouseout="this.style.borderColor='var(--border)';this.style.transform='';this.style.boxShadow=''">
            <div style="width:52px;height:52px;background:#E1F5EE;border-radius:14px;display:flex;align-items:center;justify-content:center;margin:0 auto 14px;">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#1D9E75" stroke-width="2">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
              </svg>
            </div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:600;color:var(--text);margin-bottom:6px;">Créer une Facture</div>
            <div style="font-size:13px;color:var(--text2);">Enregistrer une vente et générer une facture client</div>
          </button>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:36px;">
          <button onclick="showPage('dashboard')" style="background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:16px;cursor:pointer;transition:all 0.2s;text-align:center;" onmouseover="this.style.background='var(--surface)'" onmouseout="this.style.background='var(--surface2)'">
            <div style="font-size:22px;margin-bottom:6px;">&#128202;</div>
            <div style="font-size:13px;font-weight:500;color:var(--text)">Tableau de Bord</div>
          </button>
          <button onclick="showPage('client')" style="background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:16px;cursor:pointer;transition:all 0.2s;text-align:center;" onmouseover="this.style.background='var(--surface)'" onmouseout="this.style.background='var(--surface2)'">
            <div style="font-size:22px;margin-bottom:6px;">&#128101;</div>
            <div style="font-size:13px;font-weight:500;color:var(--text)">Clients</div>
          </button>
          <button onclick="showPage('analyse')" style="background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:16px;cursor:pointer;transition:all 0.2s;text-align:center;" onmouseover="this.style.background='var(--surface)'" onmouseout="this.style.background='var(--surface2)'">
            <div style="font-size:22px;margin-bottom:6px;">&#128200;</div>
            <div style="font-size:13px;font-weight:500;color:var(--text)">Statistiques</div>
          </button>
        </div>
        <div style="font-size:12px;color:var(--text3);">INF232 EC2 — Application de collecte &amp; analyse des données</div>
      </div>
    </div>
  </div>

  <!-- ══════════════════ DASHBOARD ══════════════════ -->
  <div class="page" id="page-dashboard">
    <div id="alert-dashboard" class="alert"></div>

    <div class="grid-4" style="margin-bottom:24px;">
      <div class="stat-card stat-accent">
        <div class="stat-label">Chiffre d'Affaires (Mois)</div>
        <div class="stat-value" id="kpi-ca">—</div>
        <div class="stat-sub" id="kpi-ca-sub">Calculé sur les 30 derniers jours</div>
      </div>
      <div class="stat-card stat-green">
        <div class="stat-label">Ventes Aujourd'hui</div>
        <div class="stat-value" id="kpi-today">—</div>
        <div class="stat-sub" id="kpi-today-sub">Transactions journalières</div>
      </div>
      <div class="stat-card stat-blue">
        <div class="stat-label">Clients Enregistrés</div>
        <div class="stat-value" id="kpi-clients">—</div>
        <div class="stat-sub">Base clientèle totale</div>
      </div>
      <div class="stat-card stat-warn">
        <div class="stat-label">Alertes Stock</div>
        <div class="stat-value" id="kpi-alerts">—</div>
        <div class="stat-sub">Produits sous seuil critique</div>
      </div>
    </div>

    <div class="grid-2" style="margin-bottom:24px;">
      <div class="card">
        <div class="card-title">Évolution des Ventes (7 derniers jours)</div>
        <div class="chart-container"><canvas id="chart-sales"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">Répartition par Catégorie</div>
        <div class="chart-container"><canvas id="chart-cat"></canvas></div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-title">⚠ Alertes de Stock Critique</div>
        <div id="stock-alerts-list"></div>
      </div>
      <div class="card">
        <div class="card-title">🕐 Dernières Transactions</div>
        <div id="recent-ventes"></div>
      </div>
    </div>
  </div>

  <!-- ══════════════════ SAISIE VENTE ══════════════════ -->
  <div class="page" id="page-vente">
    <div id="alert-vente" class="alert"></div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Nouvelle Transaction de Vente</div>
        <div class="form-grid">
          <div class="form-group">
            <label>Date de la Vente</label>
            <input type="date" id="v-date">
          </div>
          <div class="form-group">
            <label>Heure</label>
            <input type="time" id="v-heure">
          </div>
          <div class="form-group">
            <label>Client</label>
            <select id="v-client">
              <option value="">-- Client non enregistré --</option>
            </select>
          </div>
          <div class="form-group">
            <label>Mode de Paiement</label>
            <select id="v-paiement">
              <option value="especes">Espèces</option>
              <option value="mobile_money">Mobile Money (MTN/Orange)</option>
              <option value="cheque">Chèque</option>
              <option value="virement">Virement Bancaire</option>
              <option value="credit">Crédit / Doit</option>
            </select>
          </div>
          <div class="form-group full">
            <label>Produit</label>
            <select id="v-produit" onchange="fillPrix()">
              <option value="">-- Sélectionner un produit --</option>
            </select>
          </div>
          <div class="form-group">
            <label>Quantité</label>
            <input type="number" id="v-quantite" min="1" value="1" oninput="calcTotal()">
          </div>
          <div class="form-group">
            <label>Prix Unitaire (FCFA)</label>
            <input type="number" id="v-prix" oninput="calcTotal()">
          </div>
          <div class="form-group full">
            <label>Remise (%)</label>
            <input type="number" id="v-remise" min="0" max="100" value="0" oninput="calcTotal()">
          </div>
          <div class="form-group full">
            <label>Observations</label>
            <textarea id="v-notes" placeholder="Remarques, conditions spéciales..."></textarea>
          </div>
        </div>
        <div class="divider"></div>
        <div style="background: var(--surface2); border-radius: var(--radius-sm); padding: 16px; margin-bottom: 16px;">
          <div class="sum-row"><span>Sous-total :</span> <span id="v-subtotal">0 FCFA</span></div>
          <div class="sum-row"><span>Remise :</span> <span id="v-remise-val">0 FCFA</span></div>
          <div class="sum-row"><span>TOTAL NET :</span> <span id="v-total" style="color: var(--primary);">0 FCFA</span></div>
        </div>
        <div style="display: flex; gap: 12px;">
          <button class="btn btn-primary" onclick="saveVente()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            Valider la Vente
          </button>
          <button class="btn btn-ghost" onclick="clearVente()">Effacer</button>
        </div>
      </div>
      <div class="card">
        <div class="card-title">Statistiques Rapides de la Journée</div>
        <div id="daily-stats"></div>
      </div>
    </div>
  </div>

  <!-- ══════════════════ CLIENTS ══════════════════ -->
  <div class="page" id="page-client">
    <div id="alert-client" class="alert"></div>
    <div class="grid-2" style="margin-bottom: 20px;">
      <div class="card">
        <div class="card-title">Enregistrer un Nouveau Client</div>
        <div class="form-grid">
          <div class="form-group">
            <label>Nom</label>
            <input type="text" id="c-nom" placeholder="Nom du client / entreprise">
          </div>
          <div class="form-group">
            <label>Téléphone</label>
            <input type="tel" id="c-tel" placeholder="Ex: 6XXXXXXXX">
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" id="c-email" placeholder="email@exemple.com">
          </div>
          <div class="form-group">
            <label>Type de Client</label>
            <select id="c-type">
              <option value="particulier">Particulier</option>
              <option value="entreprise">Entreprise / Promoteur</option>
              <option value="revendeur">Revendeur</option>
              <option value="administration">Administration</option>
            </select>
          </div>
          <div class="form-group full">
            <label>Adresse</label>
            <input type="text" id="c-adresse" placeholder="Quartier, ville">
          </div>
        </div>
        <div class="divider"></div>
        <button class="btn btn-primary" onclick="saveClient()">Ajouter le Client</button>
      </div>
      <div class="card">
        <div class="card-title">Résumé Clientèle</div>
        <div class="chart-container"><canvas id="chart-clients"></canvas></div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Liste des Clients</div>
      <div class="search-bar">
        <input type="text" class="search-input" id="client-search" placeholder="🔍 Rechercher un client..." oninput="filterClients()">
      </div>
      <div class="table-wrap" id="clients-table"></div>
    </div>
  </div>

  <!-- ══════════════════ STOCK ══════════════════ -->
  <div class="page" id="page-stock">
    <div id="alert-stock" class="alert"></div>
    <div class="card" style="margin-bottom:20px;">
      <div class="card-title">Mettre à Jour le Stock</div>
      <div class="form-grid" style="grid-template-columns: repeat(4, 1fr); gap: 12px;">
        <div class="form-group">
          <label>Produit</label>
          <select id="s-produit">
            <option value="">-- Choisir --</option>
          </select>
        </div>
        <div class="form-group">
          <label>Opération</label>
          <select id="s-operation">
            <option value="entree">Entrée de Stock</option>
            <option value="correction">Correction Inventaire</option>
          </select>
        </div>
        <div class="form-group">
          <label>Quantité</label>
          <input type="number" id="s-quantite" min="1" placeholder="Qté">
        </div>
        <div class="form-group" style="justify-content: flex-end;">
          <label>&nbsp;</label>
          <button class="btn btn-success" onclick="updateStock()">Mettre à Jour</button>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">État du Stock</div>
      <div class="table-wrap" id="stock-table"></div>
    </div>
  </div>

  <!-- ══════════════════ DÉPENSES ══════════════════ -->
  <div class="page" id="page-depense">
    <div id="alert-depense" class="alert"></div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Saisir une Dépense</div>
        <div class="form-grid">
          <div class="form-group">
            <label>Date</label>
            <input type="date" id="d-date">
          </div>
          <div class="form-group">
            <label>Catégorie</label>
            <select id="d-categorie">
              <option value="loyer">Loyer / Bail</option>
              <option value="salaire">Salaires</option>
              <option value="transport">Transport / Livraison</option>
              <option value="achat_stock">Achat de Stock</option>
              <option value="entretien">Entretien / Réparations</option>
              <option value="electricite">Électricité / Eau</option>
              <option value="communication">Téléphone / Internet</option>
              <option value="impot">Impôts / Taxes</option>
              <option value="autre">Autre</option>
            </select>
          </div>
          <div class="form-group">
            <label>Montant (FCFA)</label>
            <input type="number" id="d-montant" min="0" placeholder="0">
          </div>
          <div class="form-group">
            <label>Bénéficiaire</label>
            <input type="text" id="d-beneficiaire" placeholder="Nom / Fournisseur">
          </div>
          <div class="form-group full">
            <label>Description</label>
            <textarea id="d-description" placeholder="Détails de la dépense..."></textarea>
          </div>
        </div>
        <div class="divider"></div>
        <button class="btn btn-primary" onclick="saveDepense()">Enregistrer la Dépense</button>
      </div>
      <div class="card">
        <div class="card-title">Résumé des Dépenses</div>
        <div class="chart-container"><canvas id="chart-depenses"></canvas></div>
        <div class="divider"></div>
        <div id="depenses-summary"></div>
      </div>
    </div>
  </div>

  <!-- ══════════════════ ANALYSES ══════════════════ -->
  <div class="page" id="page-analyse">
    <div class="grid-4" style="margin-bottom:24px;" id="analyse-kpis"></div>
    <div class="grid-2" style="margin-bottom:24px;">
      <div class="card">
        <div class="card-title">Distribution des Montants de Ventes</div>
        <div class="chart-container"><canvas id="chart-distrib"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">Top 5 Produits Vendus</div>
        <div class="chart-container"><canvas id="chart-top-prod"></canvas></div>
      </div>
    </div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Revenus vs Dépenses (Mensuel)</div>
        <div class="chart-container"><canvas id="chart-rd"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">Indicateurs Statistiques Descriptifs</div>
        <div id="stats-table"></div>
      </div>
    </div>
  </div>

  <!-- ══════════════════ HISTORIQUE ══════════════════ -->
  <div class="page" id="page-historique">
    <div class="card">
      <div class="card-title">Historique de Toutes les Ventes</div>
      <div class="search-bar">
        <input type="text" class="search-input" id="hist-search" placeholder="🔍 Rechercher par produit, client, mode de paiement..." oninput="filterHistorique()">
        <select id="hist-periode" onchange="filterHistorique()" style="min-width:160px;">
          <option value="all">Toutes les périodes</option>
          <option value="today">Aujourd'hui</option>
          <option value="week">Cette semaine</option>
          <option value="month">Ce mois</option>
        </select>
        <button class="btn btn-ghost btn-sm" onclick="exportCSV()">
          ⬇ Exporter CSV
        </button>
      </div>
      <div class="table-wrap" id="historique-table"></div>
    </div>
  </div>

</div><!-- /main -->

<!-- MODAL CONFIRMATION -->
<div class="modal-overlay" id="modal">
  <div class="modal">
    <div class="modal-header">
      <div class="modal-title" id="modal-title">Confirmation</div>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div id="modal-body"></div>
    <div style="display:flex; gap:12px; margin-top:20px;">
      <button class="btn btn-primary" id="modal-ok">Confirmer</button>
      <button class="btn btn-ghost" onclick="closeModal()">Annuler</button>
    </div>
  </div>
</div>

<script>
// ─── STATE ────────────────────────────────────────────────────────────────────
let state = { ventes:[], clients:[], stocks:[], depenses:[] };
let charts = {};

// ─── INIT ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateClock();
  setInterval(updateClock, 60000);
  setDefaultDates();
  // Afficher la page d'accueil au démarrage
  showPage('accueil');
  // Charger les données en arrière-plan SANS changer de page
  fetchData();
});

function updateClock() {
  const now = new Date();
  document.getElementById('current-date').textContent =
    now.toLocaleDateString('fr-FR', {weekday:'long', year:'numeric', month:'long', day:'numeric'}) +
    ' — ' + now.toLocaleTimeString('fr-FR', {hour:'2-digit', minute:'2-digit'});
}

function setDefaultDates() {
  const today = new Date().toISOString().split('T')[0];
  const time = new Date().toTimeString().slice(0,5);
  ['v-date','d-date'].forEach(id => { const el = document.getElementById(id); if(el) el.value = today; });
  const el = document.getElementById('v-heure'); if(el) el.value = time;
}

// ─── NAVIGATION ───────────────────────────────────────────────────────────────
const PAGE_TITLES = {
  accueil: 'Accueil', dashboard: 'Tableau de Bord', vente: 'Saisie de Vente',
  client: 'Gestion Clients', stock: 'Gestion du Stock',
  depense: 'Saisie de Dépense', analyse: 'Analyse Descriptive',
  historique: 'Historique des Ventes'
};

function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  const navEl = document.querySelector(`.nav-item[onclick="showPage('${name}')"]`);
  if(navEl) navEl.classList.add('active');
  document.getElementById('page-title').textContent = PAGE_TITLES[name] || name;
  if(name === 'dashboard') renderDashboard();
  if(name === 'client') renderClients();
  if(name === 'stock') renderStock();
  if(name === 'analyse') renderAnalyse();
  if(name === 'historique') renderHistorique();
  if(name === 'depense') renderDepenseChart();
  if(name === 'vente') renderDailyStats();
}

// ─── API ──────────────────────────────────────────────────────────────────────
async function fetchData() {
  try {
    const r = await fetch('/api/data');
    state = await r.json();
    populateSelects();
    // Rafraîchir uniquement la page actuellement visible
    const activePage = document.querySelector('.page.active');
    if(activePage) {
      const name = activePage.id.replace('page-', '');
      if(name === 'dashboard') renderDashboard();
      else if(name === 'client') renderClients();
      else if(name === 'stock') renderStock();
      else if(name === 'analyse') renderAnalyse();
      else if(name === 'historique') renderHistorique();
      else if(name === 'depense') renderDepenseChart();
      else if(name === 'vente') renderDailyStats();
      // accueil : rien à rafraîchir
    }
  } catch(e) { console.error('Erreur chargement:', e); }
}

async function post(endpoint, data) {
  const r = await fetch(endpoint, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });
  return r.json();
}

// ─── POPULATE SELECTS ─────────────────────────────────────────────────────────
function populateSelects() {
  const vp = document.getElementById('v-produit');
  const sp = document.getElementById('s-produit');
  const vc = document.getElementById('v-client');
  if(vp) { vp.innerHTML = '<option value="">-- Sélectionner un produit --</option>';
    state.stocks.forEach(s => vp.innerHTML += `<option value="${s.id}" data-prix="${s.prix_unitaire}">${s.produit} (${s.quantite} en stock)</option>`); }
  if(sp) { sp.innerHTML = '<option value="">-- Choisir --</option>';
    state.stocks.forEach(s => sp.innerHTML += `<option value="${s.id}">${s.produit}</option>`); }
  if(vc) { vc.innerHTML = '<option value="">-- Client non enregistré --</option>';
    state.clients.forEach(c => vc.innerHTML += `<option value="${c.id}">${c.nom} (${c.telephone})</option>`); }
}

// ─── VENTE ────────────────────────────────────────────────────────────────────
function fillPrix() {
  const sel = document.getElementById('v-produit');
  const opt = sel.options[sel.selectedIndex];
  const prix = opt.getAttribute('data-prix') || '';
  document.getElementById('v-prix').value = prix;
  calcTotal();
}

function calcTotal() {
  const qty = parseFloat(document.getElementById('v-quantite').value) || 0;
  const prix = parseFloat(document.getElementById('v-prix').value) || 0;
  const remise = parseFloat(document.getElementById('v-remise').value) || 0;
  const sub = qty * prix;
  const remiseVal = sub * remise / 100;
  const total = sub - remiseVal;
  document.getElementById('v-subtotal').textContent = fmt(sub);
  document.getElementById('v-remise-val').textContent = '-' + fmt(remiseVal);
  document.getElementById('v-total').textContent = fmt(total);
}

function fmt(n) { return new Intl.NumberFormat('fr-FR').format(Math.round(n)) + ' FCFA'; }

async function saveVente() {
  const produitId = document.getElementById('v-produit').value;
  const produit = state.stocks.find(s => s.id === produitId);
  if(!produitId) return showAlert('vente','Veuillez sélectionner un produit.','danger');
  const qty = parseFloat(document.getElementById('v-quantite').value);
  if(!qty || qty <= 0) return showAlert('vente','Quantité invalide.','danger');
  if(produit && qty > produit.quantite) return showAlert('vente',`Stock insuffisant. Disponible: ${produit.quantite}`, 'danger');

  const data = {
    date: document.getElementById('v-date').value,
    heure: document.getElementById('v-heure').value,
    client_id: document.getElementById('v-client').value,
    produit_id: produitId,
    produit_nom: produit ? produit.produit : '',
    categorie: produit ? produit.categorie : '',
    quantite: qty,
    prix_unitaire: parseFloat(document.getElementById('v-prix').value),
    remise: parseFloat(document.getElementById('v-remise').value) || 0,
    paiement: document.getElementById('v-paiement').value,
    notes: document.getElementById('v-notes').value
  };
  data.total = data.quantite * data.prix_unitaire * (1 - data.remise/100);

  const res = await post('/api/vente', data);
  if(res.success) {
    showAlert('vente', `✅ Vente enregistrée avec succès ! Total: ${fmt(data.total)}`, 'success');
    clearVente(); fetchData();
  } else { showAlert('vente', res.error || 'Erreur lors de l\'enregistrement.', 'danger'); }
}

function clearVente() {
  ['v-client','v-produit','v-paiement'].forEach(id => document.getElementById(id).value = document.getElementById(id).options[0].value);
  ['v-quantite'].forEach(id => document.getElementById(id).value = '1');
  ['v-remise'].forEach(id => document.getElementById(id).value = '0');
  ['v-prix','v-notes'].forEach(id => document.getElementById(id).value = '');
  setDefaultDates(); calcTotal();
}

// ─── CLIENT ───────────────────────────────────────────────────────────────────
async function saveClient() {
  const nom = document.getElementById('c-nom').value.trim();
  if(!nom) return showAlert('client','Le nom du client est obligatoire.','danger');
  const data = { nom, telephone: document.getElementById('c-tel').value, email: document.getElementById('c-email').value, adresse: document.getElementById('c-adresse').value, type: document.getElementById('c-type').value };
  const res = await post('/api/client', data);
  if(res.success) {
    showAlert('client','✅ Client enregistré avec succès !','success');
    ['c-nom','c-tel','c-email','c-adresse'].forEach(id => document.getElementById(id).value = '');
    fetchData(); renderClients();
  } else { showAlert('client', res.error || 'Erreur.', 'danger'); }
}

function renderClients() {
  const search = (document.getElementById('client-search')?.value || '').toLowerCase();
  const filtered = state.clients.filter(c => c.nom.toLowerCase().includes(search) || (c.telephone||'').includes(search));
  const el = document.getElementById('clients-table');
  if(!el) return;
  if(!filtered.length) { el.innerHTML = '<div class="empty-state"><h3>Aucun client trouvé</h3></div>'; return; }
  el.innerHTML = `<table><thead><tr><th>Nom</th><th>Téléphone</th><th>Type</th><th>Adresse</th><th>CA Total</th></tr></thead><tbody>${
    filtered.map(c => {
      const ca = state.ventes.filter(v => v.client_id === c.id).reduce((s,v) => s + (v.total||0), 0);
      const badge = {particulier:'info',entreprise:'success',revendeur:'warning',administration:'primary'}[c.type] || 'info';
      return `<tr><td><strong>${c.nom}</strong></td><td>${c.telephone||'—'}</td><td><span class="badge badge-${badge}">${c.type}</span></td><td>${c.adresse||'—'}</td><td style="font-weight:600;color:var(--primary)">${fmt(ca)}</td></tr>`;
    }).join('')
  }</tbody></table>`;

  // Client type chart
  const types = {};
  state.clients.forEach(c => types[c.type] = (types[c.type]||0) + 1);
  renderChart('chart-clients', 'doughnut', Object.keys(types), Object.values(types), 'Types de Clients');
}

function filterClients() { renderClients(); }

// ─── STOCK ────────────────────────────────────────────────────────────────────
function renderStock() {
  const el = document.getElementById('stock-table');
  if(!el) return;
  el.innerHTML = `<table><thead><tr><th>Réf.</th><th>Produit</th><th>Catégorie</th><th>Prix Unitaire</th><th>En Stock</th><th>Seuil Alerte</th><th>Statut</th></tr></thead><tbody>${
    state.stocks.map(s => {
      const pct = Math.min(100, (s.quantite / (s.seuil_alerte * 3)) * 100);
      const status = s.quantite <= s.seuil_alerte ? `<span class="badge badge-danger">⚠ Critique</span>` : s.quantite <= s.seuil_alerte * 1.5 ? `<span class="badge badge-warning">Faible</span>` : `<span class="badge badge-success">OK</span>`;
      const qtyClass = s.quantite <= s.seuil_alerte ? 'stock-critical' : 'stock-ok';
      return `<tr><td style="color:var(--text2);font-size:12px">${s.id}</td><td><strong>${s.produit}</strong></td><td>${s.categorie}</td><td>${fmt(s.prix_unitaire)}</td><td class="${qtyClass}">${s.quantite}</td><td>${s.seuil_alerte}</td><td>${status}</td></tr>`;
    }).join('')
  }</tbody></table>`;
}

async function updateStock() {
  const produit_id = document.getElementById('s-produit').value;
  const operation = document.getElementById('s-operation').value;
  const quantite = parseInt(document.getElementById('s-quantite').value);
  if(!produit_id) return showAlert('stock','Sélectionnez un produit.','danger');
  if(!quantite || quantite <= 0) return showAlert('stock','Quantité invalide.','danger');
  const res = await post('/api/stock', {produit_id, operation, quantite});
  if(res.success) { showAlert('stock','✅ Stock mis à jour avec succès.','success'); fetchData(); renderStock(); }
  else { showAlert('stock', res.error || 'Erreur.', 'danger'); }
}

// ─── DÉPENSES ─────────────────────────────────────────────────────────────────
async function saveDepense() {
  const montant = parseFloat(document.getElementById('d-montant').value);
  if(!montant || montant <= 0) return showAlert('depense','Montant invalide.','danger');
  const data = {
    date: document.getElementById('d-date').value,
    categorie: document.getElementById('d-categorie').value,
    montant,
    beneficiaire: document.getElementById('d-beneficiaire').value,
    description: document.getElementById('d-description').value
  };
  const res = await post('/api/depense', data);
  if(res.success) {
    showAlert('depense','✅ Dépense enregistrée.','success');
    document.getElementById('d-montant').value = '';
    document.getElementById('d-beneficiaire').value = '';
    document.getElementById('d-description').value = '';
    fetchData(); renderDepenseChart();
  }
}

function renderDepenseChart() {
  const cats = {};
  state.depenses.forEach(d => cats[d.categorie] = (cats[d.categorie]||0) + d.montant);
  renderChart('chart-depenses', 'doughnut', Object.keys(cats), Object.values(cats), 'Dépenses par catégorie');
  const total = Object.values(cats).reduce((s,v) => s+v, 0);
  const el = document.getElementById('depenses-summary');
  if(el) { el.innerHTML = Object.entries(cats).sort((a,b)=>b[1]-a[1]).map(([k,v]) => `<div class="sum-row"><span>${k}</span><span>${fmt(v)}</span></div>`).join('') + `<div class="sum-row"><span>TOTAL</span><span style="color:var(--danger)">${fmt(total)}</span></div>`; }
}

// ─── DASHBOARD ────────────────────────────────────────────────────────────────
function renderDashboard() {
  const today = new Date().toISOString().split('T')[0];
  const month = today.slice(0,7);
  const ventesToday = state.ventes.filter(v => v.date === today);
  const ventesMonth = state.ventes.filter(v => (v.date||'').startsWith(month));
  const caMonth = ventesMonth.reduce((s,v) => s+(v.total||0), 0);
  const alerts = state.stocks.filter(s => s.quantite <= s.seuil_alerte);

  document.getElementById('kpi-ca').textContent = new Intl.NumberFormat('fr-FR').format(Math.round(caMonth)) + ' FCFA';
  document.getElementById('kpi-today').textContent = ventesToday.length;
  document.getElementById('kpi-today-sub').textContent = `${fmt(ventesToday.reduce((s,v)=>s+(v.total||0),0))} aujourd'hui`;
  document.getElementById('kpi-clients').textContent = state.clients.length;
  document.getElementById('kpi-alerts').textContent = alerts.length;

  // Sales 7 days
  const days = []; const labels = []; const vals = [];
  for(let i=6; i>=0; i--) {
    const d = new Date(); d.setDate(d.getDate()-i);
    const ds = d.toISOString().split('T')[0];
    days.push(ds);
    labels.push(d.toLocaleDateString('fr-FR', {weekday:'short', day:'numeric'}));
    vals.push(state.ventes.filter(v=>v.date===ds).reduce((s,v)=>s+(v.total||0),0));
  }
  renderChart('chart-sales','bar', labels, vals, 'CA (FCFA)', '#D85A30');

  // By category
  const cats = {};
  state.ventes.forEach(v => cats[v.categorie||'Autre'] = (cats[v.categorie||'Autre']||0) + (v.total||0));
  renderChart('chart-cat','doughnut', Object.keys(cats), Object.values(cats));

  // Alerts
  const alertEl = document.getElementById('stock-alerts-list');
  if(alertEl) {
    if(!alerts.length) { alertEl.innerHTML = '<div class="empty-state" style="padding:20px"><h3>✅ Aucune alerte</h3><p>Tous les stocks sont suffisants</p></div>'; }
    else { alertEl.innerHTML = alerts.map(s => `<div class="sum-row"><span>${s.produit}</span><span class="stock-critical">⚠ ${s.quantite} restants</span></div>`).join(''); }
  }

  // Recent transactions
  const recentEl = document.getElementById('recent-ventes');
  if(recentEl) {
    const recent = [...state.ventes].sort((a,b) => b.id?.localeCompare(a.id)||0).slice(0,5);
    if(!recent.length) { recentEl.innerHTML = '<div class="empty-state" style="padding:20px"><h3>Aucune vente enregistrée</h3></div>'; }
    else { recentEl.innerHTML = recent.map(v => `<div class="sum-row"><span><strong>${v.produit_nom||'—'}</strong><br><small style="color:var(--text3)">${v.date} ${v.heure||''}</small></span><span style="color:var(--primary);font-weight:600">${fmt(v.total||0)}</span></div>`).join(''); }
  }
}

function renderDailyStats() {
  const today = new Date().toISOString().split('T')[0];
  const ventesDuJour = state.ventes.filter(v => v.date === today);
  const ca = ventesDuJour.reduce((s,v)=>s+(v.total||0),0);
  const el = document.getElementById('daily-stats');
  if(!el) return;
  const moy = ventesDuJour.length ? ca/ventesDuJour.length : 0;
  const max = ventesDuJour.length ? Math.max(...ventesDuJour.map(v=>v.total||0)) : 0;
  el.innerHTML = `
    <div class="stat-card stat-accent" style="margin-bottom:12px"><div class="stat-label">CA du jour</div><div class="stat-value">${fmt(ca)}</div></div>
    <div class="stat-card stat-green" style="margin-bottom:12px"><div class="stat-label">Nombre de transactions</div><div class="stat-value">${ventesDuJour.length}</div></div>
    <div class="stat-card stat-blue" style="margin-bottom:12px"><div class="stat-label">Panier moyen</div><div class="stat-value">${fmt(moy)}</div></div>
    <div class="stat-card stat-warn"><div class="stat-label">Plus grande vente</div><div class="stat-value">${fmt(max)}</div></div>
  `;
}

// ─── ANALYSE ──────────────────────────────────────────────────────────────────
function renderAnalyse() {
  const totaux = state.ventes.map(v => v.total||0);
  const n = totaux.length;
  const mean = n ? totaux.reduce((a,b)=>a+b,0)/n : 0;
  const sorted = [...totaux].sort((a,b)=>a-b);
  const median = n ? (n%2===0 ? (sorted[n/2-1]+sorted[n/2])/2 : sorted[Math.floor(n/2)]) : 0;
  const variance = n ? totaux.reduce((s,v)=>s+Math.pow(v-mean,2),0)/n : 0;
  const stddev = Math.sqrt(variance);
  const min = n ? Math.min(...totaux) : 0;
  const max = n ? Math.max(...totaux) : 0;

  const kpis = document.getElementById('analyse-kpis');
  if(kpis) kpis.innerHTML = `
    <div class="stat-card stat-accent"><div class="stat-label">Moyenne</div><div class="stat-value" style="font-size:20px">${fmt(mean)}</div></div>
    <div class="stat-card stat-green"><div class="stat-label">Médiane</div><div class="stat-value" style="font-size:20px">${fmt(median)}</div></div>
    <div class="stat-card stat-blue"><div class="stat-label">Écart-Type</div><div class="stat-value" style="font-size:20px">${fmt(stddev)}</div></div>
    <div class="stat-card stat-warn"><div class="stat-label">Total Transactions</div><div class="stat-value">${n}</div></div>
  `;

  // Distribution
  const buckets = [0,10000,50000,100000,200000,500000,Infinity];
  const labels = ['<10k','10-50k','50-100k','100-200k','200-500k','>500k'];
  const counts = new Array(labels.length).fill(0);
  totaux.forEach(v => { for(let i=0;i<buckets.length-1;i++) { if(v>=buckets[i]&&v<buckets[i+1]) { counts[i]++; break; } } });
  renderChart('chart-distrib','bar', labels, counts, 'Nombre de ventes');

  // Top produits
  const prods = {};
  state.ventes.forEach(v => prods[v.produit_nom||'Inconnu'] = (prods[v.produit_nom||'Inconnu']||0)+(v.total||0));
  const top5 = Object.entries(prods).sort((a,b)=>b[1]-a[1]).slice(0,5);
  renderChart('chart-top-prod','horizontalBar', top5.map(([k])=>k), top5.map(([,v])=>v), 'CA par produit');

  // Rev vs Dep
  const months = {}; const depMon = {};
  state.ventes.forEach(v => { const m = (v.date||'').slice(0,7); months[m]=(months[m]||0)+(v.total||0); });
  state.depenses.forEach(d => { const m = (d.date||'').slice(0,7); depMon[m]=(depMon[m]||0)+d.montant; });
  const allMonths = [...new Set([...Object.keys(months),...Object.keys(depMon)])].sort().slice(-6);
  renderChartDouble('chart-rd', allMonths, allMonths.map(m=>months[m]||0), allMonths.map(m=>depMon[m]||0));

  // Stats table
  const statsEl = document.getElementById('stats-table');
  if(statsEl) statsEl.innerHTML = `
    <table><thead><tr><th>Indicateur</th><th>Valeur</th></tr></thead><tbody>
      <tr><td>Nombre de ventes</td><td><strong>${n}</strong></td></tr>
      <tr><td>CA Total</td><td><strong style="color:var(--primary)">${fmt(totaux.reduce((a,b)=>a+b,0))}</strong></td></tr>
      <tr><td>Moyenne (μ)</td><td>${fmt(mean)}</td></tr>
      <tr><td>Médiane</td><td>${fmt(median)}</td></tr>
      <tr><td>Minimum</td><td>${fmt(min)}</td></tr>
      <tr><td>Maximum</td><td>${fmt(max)}</td></tr>
      <tr><td>Étendue</td><td>${fmt(max-min)}</td></tr>
      <tr><td>Variance (σ²)</td><td>${fmt(variance)}</td></tr>
      <tr><td>Écart-Type (σ)</td><td>${fmt(stddev)}</td></tr>
      <tr><td>Coef. Variation</td><td>${mean>0?(stddev/mean*100).toFixed(1)+'%':'—'}</td></tr>
      <tr><td>Q1 (25e percentile)</td><td>${fmt(sorted[Math.floor(n*0.25)]||0)}</td></tr>
      <tr><td>Q3 (75e percentile)</td><td>${fmt(sorted[Math.floor(n*0.75)]||0)}</td></tr>
    </tbody></table>
  `;
}

// ─── HISTORIQUE ───────────────────────────────────────────────────────────────
function renderHistorique() {
  filterHistorique();
}

function filterHistorique() {
  const search = (document.getElementById('hist-search')?.value||'').toLowerCase();
  const periode = document.getElementById('hist-periode')?.value || 'all';
  const today = new Date().toISOString().split('T')[0];
  const weekAgo = new Date(); weekAgo.setDate(weekAgo.getDate()-7);
  const monthAgo = new Date(); monthAgo.setDate(monthAgo.getDate()-30);

  let filtered = state.ventes.filter(v => {
    const d = v.date || '';
    if(periode === 'today' && d !== today) return false;
    if(periode === 'week' && new Date(d) < weekAgo) return false;
    if(periode === 'month' && new Date(d) < monthAgo) return false;
    const term = search;
    return !term || (v.produit_nom||'').toLowerCase().includes(term) || (v.paiement||'').toLowerCase().includes(term) || (v.notes||'').toLowerCase().includes(term);
  }).sort((a,b) => (b.date+b.heure).localeCompare(a.date+a.heure));

  const el = document.getElementById('historique-table');
  if(!el) return;
  if(!filtered.length) { el.innerHTML = '<div class="empty-state"><h3>Aucune vente trouvée</h3></div>'; return; }

  const payBadge = {especes:'success',mobile_money:'info',cheque:'warning',virement:'primary',credit:'danger'};
  el.innerHTML = `<table><thead><tr><th>Date</th><th>Heure</th><th>Produit</th><th>Catégorie</th><th>Qté</th><th>Prix Unit.</th><th>Remise</th><th>Total</th><th>Paiement</th></tr></thead><tbody>${
    filtered.map(v => `<tr>
      <td>${v.date}</td><td>${v.heure||'—'}</td>
      <td><strong>${v.produit_nom||'—'}</strong></td>
      <td>${v.categorie||'—'}</td>
      <td style="text-align:center">${v.quantite}</td>
      <td>${fmt(v.prix_unitaire||0)}</td>
      <td>${v.remise||0}%</td>
      <td style="font-weight:600;color:var(--primary)">${fmt(v.total||0)}</td>
      <td><span class="badge badge-${payBadge[v.paiement]||'info'}">${v.paiement||'—'}</span></td>
    </tr>`).join('')
  }</tbody></table>`;
}

// ─── EXPORT CSV ───────────────────────────────────────────────────────────────
function exportCSV() {
  const headers = ['Date','Heure','Produit','Catégorie','Quantité','Prix Unitaire','Remise %','Total','Mode Paiement','Notes'];
  const rows = state.ventes.map(v => [v.date,v.heure||'',v.produit_nom||'',v.categorie||'',v.quantite,v.prix_unitaire||0,v.remise||0,v.total||0,v.paiement||'',v.notes||''].map(c=>`"${c}"`).join(','));
  const csv = [headers.join(','), ...rows].join('\n');
  const blob = new Blob(['\ufeff'+csv], {type:'text/csv;charset=utf-8;'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href=url; a.download='batismart_ventes.csv'; a.click();
}

// ─── CHART HELPERS ────────────────────────────────────────────────────────────
const PALETTE = ['#D85A30','#1D9E75','#185FA5','#BA7517','#993C1D','#085041','#534AB7','#3B6D11'];

function renderChart(canvasId, type, labels, data, label='', color=null) {
  if(charts[canvasId]) { charts[canvasId].destroy(); }
  const ctx = document.getElementById(canvasId);
  if(!ctx) return;
  const colors = color ? [color] : PALETTE;
  charts[canvasId] = new Chart(ctx, {
    type: type === 'horizontalBar' ? 'bar' : type,
    data: {
      labels,
      datasets: [{
        label: label,
        data,
        backgroundColor: type === 'bar' ? colors[0] : labels.map((_,i) => PALETTE[i%PALETTE.length]),
        borderColor: 'transparent',
        borderRadius: 4,
        indexAxis: type === 'horizontalBar' ? 'y' : 'x'
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: type !== 'bar', position: 'right', labels: { boxWidth: 12, font: { size: 11 } } } },
      scales: { x: { display: type!=='doughnut', grid:{display:false}, ticks:{font:{size:11}} }, y: { display: type!=='doughnut', grid:{color:'rgba(0,0,0,0.05)'}, ticks:{font:{size:11}} } }
    }
  });
}

function renderChartDouble(canvasId, labels, rev, dep) {
  if(charts[canvasId]) { charts[canvasId].destroy(); }
  const ctx = document.getElementById(canvasId);
  if(!ctx) return;
  charts[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label:'Revenus', data:rev, backgroundColor:'#1D9E75', borderRadius:4 },
        { label:'Dépenses', data:dep, backgroundColor:'#E24B4A', borderRadius:4 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'top', labels:{ boxWidth:12, font:{size:11} } } },
      scales: { x: { grid:{display:false}, ticks:{font:{size:11}} }, y: { grid:{color:'rgba(0,0,0,0.05)'}, ticks:{font:{size:11}} } }
    }
  });
}

// ─── ALERTS ───────────────────────────────────────────────────────────────────
function showAlert(page, msg, type='success') {
  const el = document.getElementById('alert-' + page);
  if(!el) return;
  el.className = `alert alert-${type} show`;
  el.textContent = msg;
  setTimeout(() => el.classList.remove('show'), 5000);
}

// ─── MODAL ────────────────────────────────────────────────────────────────────
function openModal(title, body, onOk) {
  document.getElementById('modal-title').textContent = title;
  document.getElementById('modal-body').textContent = body;
  document.getElementById('modal-ok').onclick = () => { onOk(); closeModal(); };
  document.getElementById('modal').classList.add('open');
}
function closeModal() { document.getElementById('modal').classList.remove('open'); }
</script>
</body>
</html>"""

# ─── BASE DE DONNÉES SQLITE ──────────────────────────────────────────────────
import sqlite3
from contextlib import contextmanager

DB_FILE = "batismart.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Crée les tables si elles n'existent pas et insère les produits par défaut."""
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS stocks (
                id          TEXT PRIMARY KEY,
                produit     TEXT NOT NULL,
                categorie   TEXT NOT NULL,
                prix_unitaire REAL NOT NULL,
                quantite    INTEGER NOT NULL DEFAULT 0,
                seuil_alerte INTEGER NOT NULL DEFAULT 10
            );

            CREATE TABLE IF NOT EXISTS clients (
                id          TEXT PRIMARY KEY,
                nom         TEXT NOT NULL,
                telephone   TEXT,
                email       TEXT,
                adresse     TEXT,
                type        TEXT DEFAULT 'particulier',
                created_at  TEXT
            );

            CREATE TABLE IF NOT EXISTS ventes (
                id          TEXT PRIMARY KEY,
                date        TEXT,
                heure       TEXT,
                client_id   TEXT,
                produit_id  TEXT,
                produit_nom TEXT,
                categorie   TEXT,
                quantite    REAL,
                prix_unitaire REAL,
                remise      REAL DEFAULT 0,
                total       REAL,
                paiement    TEXT,
                notes       TEXT,
                created_at  TEXT,
                FOREIGN KEY (produit_id) REFERENCES stocks(id),
                FOREIGN KEY (client_id)  REFERENCES clients(id)
            );

            CREATE TABLE IF NOT EXISTS depenses (
                id          TEXT PRIMARY KEY,
                date        TEXT,
                categorie   TEXT,
                montant     REAL,
                beneficiaire TEXT,
                description TEXT,
                created_at  TEXT
            );
        """)

        # Produits par défaut (insérés seulement si la table est vide)
        count = db.execute("SELECT COUNT(*) FROM stocks").fetchone()[0]
        if count == 0:
            produits = [
                ("S001","Ciment Portland 50kg","Liants",8500,120,20),
                ("S002","Barre Fer à Béton 12mm","Ferraillage",6200,85,15),
                ("S003","Parpaing Creux 20x20x40","Maçonnerie",450,340,50),
                ("S004","Carrelage 60x60 (m²)","Revêtements",12000,60,10),
                ("S005","Tôle Ondulée 3m","Couverture",9800,45,10),
                ("S006","Peinture Exterior 20L","Peintures",38000,22,5),
                ("S007","Sable Lavé (m³)","Granulats",25000,30,8),
                ("S008","Gravier Concassé (m³)","Granulats",28000,25,8),
                ("S009","Plaque Plâtre 12mm","Cloisons",7500,55,12),
                ("S010","Tube PVC 110mm (3m)","Plomberie",4200,70,15),
            ]
            db.executemany(
                "INSERT INTO stocks (id,produit,categorie,prix_unitaire,quantite,seuil_alerte) VALUES (?,?,?,?,?,?)",
                produits
            )

def row_to_dict(row):
    return dict(row) if row else None

def rows_to_list(rows):
    return [dict(r) for r in rows]

# ─── API ROUTES ───────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/data")
def api_data():
    with get_db() as db:
        stocks   = rows_to_list(db.execute("SELECT * FROM stocks ORDER BY id").fetchall())
        clients  = rows_to_list(db.execute("SELECT * FROM clients ORDER BY nom").fetchall())
        ventes   = rows_to_list(db.execute("SELECT * FROM ventes ORDER BY date DESC, heure DESC").fetchall())
        depenses = rows_to_list(db.execute("SELECT * FROM depenses ORDER BY date DESC").fetchall())
    return jsonify({"stocks": stocks, "clients": clients, "ventes": ventes, "depenses": depenses})

@app.route("/api/vente", methods=["POST"])
def api_vente():
    v = request.json
    if not v.get("produit_id"):
        return jsonify({"success": False, "error": "Produit manquant"})

    with get_db() as db:
        stock = row_to_dict(db.execute("SELECT * FROM stocks WHERE id=?", (v["produit_id"],)).fetchone())
        if not stock:
            return jsonify({"success": False, "error": "Produit introuvable"})

        qty = float(v.get("quantite", 0))
        if stock["quantite"] < qty:
            return jsonify({"success": False, "error": f"Stock insuffisant. Disponible : {stock['quantite']}"})

        total = qty * float(v.get("prix_unitaire", 0)) * (1 - float(v.get("remise", 0)) / 100)
        vid = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()

        db.execute("""
            INSERT INTO ventes (id,date,heure,client_id,produit_id,produit_nom,categorie,
                                quantite,prix_unitaire,remise,total,paiement,notes,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (vid, v.get("date"), v.get("heure"), v.get("client_id") or None,
              v["produit_id"], v.get("produit_nom"), v.get("categorie"),
              qty, float(v.get("prix_unitaire", 0)), float(v.get("remise", 0)),
              total, v.get("paiement"), v.get("notes"), now))

        db.execute("UPDATE stocks SET quantite = quantite - ? WHERE id = ?", (int(qty), v["produit_id"]))

    return jsonify({"success": True, "id": vid})

@app.route("/api/client", methods=["POST"])
def api_client():
    c = request.json
    nom = (c.get("nom") or "").strip()
    if not nom:
        return jsonify({"success": False, "error": "Le nom est obligatoire"})

    with get_db() as db:
        if c.get("telephone"):
            existing = db.execute("SELECT id FROM clients WHERE telephone=?", (c["telephone"],)).fetchone()
            if existing:
                return jsonify({"success": False, "error": "Ce numéro de téléphone existe déjà."})

        cid = "C" + str(uuid.uuid4())[:6].upper()
        now = datetime.now().isoformat()
        db.execute("""
            INSERT INTO clients (id,nom,telephone,email,adresse,type,created_at)
            VALUES (?,?,?,?,?,?,?)
        """, (cid, nom, c.get("telephone"), c.get("email"),
              c.get("adresse"), c.get("type","particulier"), now))

    return jsonify({"success": True, "id": cid})

@app.route("/api/stock", methods=["POST"])
def api_stock():
    r = request.json
    produit_id = r.get("produit_id")
    quantite   = int(r.get("quantite", 0))
    operation  = r.get("operation")

    if not produit_id:
        return jsonify({"success": False, "error": "Produit manquant"})

    with get_db() as db:
        stock = db.execute("SELECT id FROM stocks WHERE id=?", (produit_id,)).fetchone()
        if not stock:
            return jsonify({"success": False, "error": "Produit introuvable"})

        if operation == "entree":
            db.execute("UPDATE stocks SET quantite = quantite + ? WHERE id = ?", (quantite, produit_id))
        elif operation == "correction":
            db.execute("UPDATE stocks SET quantite = ? WHERE id = ?", (quantite, produit_id))

    return jsonify({"success": True})

@app.route("/api/depense", methods=["POST"])
def api_depense():
    d = request.json
    montant = float(d.get("montant", 0))
    if montant <= 0:
        return jsonify({"success": False, "error": "Montant invalide"})

    with get_db() as db:
        did = "D" + str(uuid.uuid4())[:6].upper()
        now = datetime.now().isoformat()
        db.execute("""
            INSERT INTO depenses (id,date,categorie,montant,beneficiaire,description,created_at)
            VALUES (?,?,?,?,?,?,?)
        """, (did, d.get("date"), d.get("categorie"), montant,
              d.get("beneficiaire"), d.get("description"), now))

    return jsonify({"success": True})

@app.route("/api/stats")
def api_stats():
    with get_db() as db:
        rows = db.execute("SELECT total FROM ventes WHERE total IS NOT NULL").fetchall()
    totaux = [r["total"] for r in rows]
    n = len(totaux)
    if n == 0:
        return jsonify({"n":0,"mean":0,"median":0,"std":0,"min":0,"max":0,"total":0})
    mean = sum(totaux) / n
    s = sorted(totaux)
    median = s[n//2] if n % 2 != 0 else (s[n//2-1]+s[n//2])/2
    variance = sum((x-mean)**2 for x in totaux) / n
    return jsonify({"n":n,"mean":round(mean,2),"median":round(median,2),
                    "std":round(variance**0.5,2),"min":min(totaux),"max":max(totaux),"total":sum(totaux)})

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
