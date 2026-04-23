from __future__ import annotations
import io
import sqlite3
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator, PercentFormatter
import matplotlib.ticker as mticker  # til at styre afstand mellem Y-akse etiketter

# Farver
RED = "#d32f2f"
LIGHT_RED = "#ffcdd2"

@dataclass
class _Row:
    id: int
    full_name: str
    gender: str
    full_cpr_encrypted: str
    join_date: str
    status: str
    leave_date: Optional[str]

def _parse_birthdate_from_full_cpr(full_cpr_encrypted: str) -> Optional[date]:
    """
    Forventer format 'dd-mm-YYYY-<token>' – vi bruger kun fødselsdato (ikke token).
    """
    if not full_cpr_encrypted:
        return None
    s = full_cpr_encrypted.strip()
    if len(s) >= 15 and s[2] == '-' and s[5] == '-' and s[10] == '-':
        birth = s[:10]  # dd-mm-YYYY
        try:
            return datetime.strptime(birth, "%d-%m-%Y").date()
        except Exception:
            return None
    return None

def _age_from_cpr(full_cpr_encrypted: str, today: Optional[date] = None) -> Optional[int]:
    bd = _parse_birthdate_from_full_cpr(full_cpr_encrypted)
    if not bd:
        return None
    t = today or date.today()
    years = t.year - bd.year - ((t.month, t.day) < (bd.month, bd.day))
    return years

def _to_date_safe(dmy: Optional[str]) -> Optional[date]:
    if not dmy:
        return None
    s = dmy.strip()
    try:
        return datetime.strptime(s, "%d-%m-%Y").date()
    except Exception:
        return None

class AnalyticsService:
    """
    Laver PNG-grafer ud fra medlemmer-tabellen.
    """

    def __init__(self, db_path: str):
        self._db_path = db_path

    # DB funktioner
    def _fetch_members(self) -> pd.DataFrame:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cols = pd.read_sql_query("PRAGMA table_info(members);", conn)
            has_leave = any(cols["name"].str.lower() == "leave_date")

            cols_select = "id, full_name, gender, full_cpr_encrypted, join_date, status"
            if has_leave:
                cols_select += ", leave_date"
            df = pd.read_sql_query(f"SELECT {cols_select} FROM members", conn)

        # Normalisering
        df["join_date_dt"] = df["join_date"].apply(_to_date_safe)
        if "leave_date" in df.columns:
            df["leave_date_dt"] = df["leave_date"].apply(_to_date_safe)
        else:
            df["leave_date_dt"] = None
        return df

    # skemaer
    def render(self, chart: str) -> io.BytesIO:
        """
        Genererer PNG for det ønskede chart-navn:
          - "membership"
          - "age_buckets"
          - "age_gender"
          - "child_vs_adult"
        """
        chart = (chart or "").strip().lower()
        df = self._fetch_members()

        if chart == "membership":
            fig = self._plot_membership(df)
        elif chart == "age_buckets":
            fig = self._plot_age_buckets_percent(df)
        elif chart == "age_gender":
            fig = self._plot_age_gender_counts(df)
        elif chart == "child_vs_adult":
            fig = self._plot_child_vs_adult(df)
        else:
            fig = plt.figure(figsize=(8, 4))
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "Ukendt graf", ha="center", va="center")
            ax.set_axis_off()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf

    # Statistikker
    def _plot_membership(self, df: pd.DataFrame):
        """
        Medlemsudvikling over tid (månedlige snapshots).
        """
        today = date.today()
        valid = df[~df["join_date_dt"].isna()].copy()
        if valid.empty:
            fig, ax = plt.subplots(figsize=(9, 4.5))
            ax.set_title("Medlemsudvikling (ingen data)")
            ax.set_axis_off()
            return fig

        start = min(valid["join_date_dt"]).replace(day=1)
        end = date(today.year, today.month, 1)

        months = []
        cur = start
        while cur <= end:
            months.append(cur)
            if cur.month == 12:
                cur = date(cur.year + 1, 1, 1)
            else:
                cur = date(cur.year, cur.month + 1, 1)

        def month_end(dt: date) -> date:
            if dt.month == 12:
                return date(dt.year, 12, 31)
            nxt = date(dt.year, dt.month + 1, 1)
            return nxt - pd.Timedelta(days=1)

        counts = []
        for m in months:
            me = month_end(m)
            start_m = m
            if "leave_date_dt" in valid.columns:
                active = valid[
                    (valid["join_date_dt"] <= me) &
                    (
                        valid["leave_date_dt"].isna() |
                        (valid["leave_date_dt"] >= start_m)
                    )
                ]
            else:
                active = valid[valid["join_date_dt"] <= me]
            counts.append(len(active))

        ser = pd.Series(counts, index=pd.to_datetime(months))

        fig, ax = plt.subplots(figsize=(20, 12))
        ax.plot(ser.index, ser.values, color=RED, linewidth=2.2)
        ax.set_title("Medlemsudvikling")
        ax.set_xlabel("Måned")
        ax.set_ylabel("Medlemmer")
        ax.grid(False)

        # Vis hver måned på X-aksen
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

        # Y-aksen
        ax.yaxis.set_major_locator(mticker.MultipleLocator(10))  # ← ændr 10 til 20 eller lign

        # Lodrette etiketter
        for label in ax.get_xticklabels():
            label.set_rotation(90)
            label.set_ha("center")

        plt.subplots_adjust(bottom=0.3)
        return fig

    def _plot_age_buckets_percent(self, df: pd.DataFrame):
        """
        Aldersfordeling i procent, Kun aktive medlemmer.
        Opdelinger: 0-14, 15-24, 25-34, 35-44, 45-54, 55-64, 65-99
        """
        today = date.today()
        active = df[df["status"] == "active"].copy()
        active["age"] = active["full_cpr_encrypted"].apply(lambda s: _age_from_cpr(s, today))
        active = active[~active["age"].isna()]
        if active.empty:
            fig, ax = plt.subplots(figsize=(9, 4.5))
            ax.set_title("Aldersfordeling (ingen data)")
            ax.set_axis_off()
            return fig

        edges = [0, 15, 25, 35, 45, 55, 65, 100]
        labels = ["0-14", "15-24", "25-34", "35-44", "45-54", "55-64", "65-99"]
        bins = pd.cut(active["age"].astype(int), bins=edges, right=False, labels=labels, include_lowest=True)
        counts = bins.value_counts().reindex(labels, fill_value=0)

        total = counts.sum()
        perc = (counts / total * 100.0).round(1)  # procent afrundet
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.bar(labels, perc.values, color=RED)
        ax.set_title("Aldersfordeling (procent)")
        ax.set_ylabel("Andel (%)")
        ax.set_ylim(0, max(100, perc.max() * 1.15))
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))
        ax.grid(False)

        # % labels
        for i, v in enumerate(perc.values):
            label = f"{int(v)}%" if abs(v - int(v)) < 0.05 else f"{v:.1f}%"
            ax.text(i, v + max(1, perc.max() * 0.02), label, ha="center", va="bottom", fontsize=9)
        return fig

    def _plot_age_gender_counts(self, df: pd.DataFrame):
        """
        Alder/køn fordeling
        """
        today = date.today()
        active = df[df["status"] == "active"].copy()
        active["age"] = active["full_cpr_encrypted"].apply(lambda s: _age_from_cpr(s, today))
        active = active[~active["age"].isna()]
        if active.empty:
            fig, ax = plt.subplots(figsize=(9, 4.5))
            ax.set_title("Alder/Køn (ingen data)")
            ax.set_axis_off()
            return fig

        edges = [0, 15, 25, 35, 45, 55, 65, 100]
        labels = ["0-14", "15-24", "25-34", "35-44", "45-54", "55-64", "65-99"]
        active["bucket"] = pd.cut(active["age"].astype(int), bins=edges, right=False, labels=labels, include_lowest=True)

        piv = active.pivot_table(index="bucket", columns="gender", values="id", aggfunc="count", fill_value=0).reindex(labels).fillna(0)
        genders = list(piv.columns)
        x = np.arange(len(labels))
        width = 0.8 / max(1, len(genders))

        fig, ax = plt.subplots(figsize=(9, 4.5))

        # standard farvecyklus
        for i, g in enumerate(genders):
            vals = piv[g].astype(int).values
            ax.bar(x + (i - (len(genders)-1)/2)*width, vals, width=width, label=g)

        ax.set_xticks(x, labels)
        ax.set_title("Alder / Køn (antal)")
        ax.set_ylabel("Antal")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))  # hele tal
        ax.grid(False)  # ingen gitter
        ax.legend(title="Køn")
        return fig

    def _plot_child_vs_adult(self, df: pd.DataFrame):
        """
        Cirkel: Børn (0-14) vs Voksne (15+)
        """
        today = date.today()
        active = df[df["status"] == "active"].copy()
        active["age"] = active["full_cpr_encrypted"].apply(lambda s: _age_from_cpr(s, today))
        active = active[~active["age"].isna()]
        if active.empty:
            fig, ax = plt.subplots(figsize=(8, 4.5))
            ax.set_title("Børn vs. Voksne (ingen data)")
            ax.set_axis_off()
            return fig

        child = (active["age"] <= 14).sum()
        adult = (active["age"] >= 15).sum()
        vals = [child, adult]
        labels = ["Børn (0-14)", "Voksne (15+)"]
        colors = [LIGHT_RED, RED]

        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.pie(
            vals,
            labels=labels,
            colors=colors,
            autopct=lambda p: f"{p:.0f}%",
            startangle=90,
            textprops={"color": "#111"}
        )
        ax.axis("equal")
        ax.set_title("Børn vs. Voksne")
        return fig