"""
Motor auditado para Power BI / Python.Execute.

Objetivos:
- Regresión logística: probabilidad de incumplir el SLA interno zonal: 4 DH Santiago y 5 DH Regiones.
- Regresión lineal regularizada: días hábiles totales esperados.
- Entrena únicamente con pedidos de flujo completo y calidad válida.
- Predice pedidos pendientes sin usar FES, Saldo ni duraciones futuras como predictores.

Entrada Power BI: DataFrame `dataset`.
Salida Power BI: DataFrame `dataset` con una fila por pedido.
"""
from __future__ import annotations

import math
import warnings
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

try:
    from sklearn.linear_model import LogisticRegression, Ridge
    from sklearn.metrics import average_precision_score, brier_score_loss, mean_absolute_error, mean_squared_error, r2_score, roc_auc_score
    SKLEARN_OK = True
except Exception:
    SKLEARN_OK = False

SLA_DEFAULT_DH = 5.0
MAX_TARGET_DH = 60.0
RISK_HIGH = 0.20
RISK_MEDIUM = 0.10
SMOOTHING_K = 10.0
MODEL_VERSION = "ML_LOGIT_LINEAR_FLUJO_COMPLETO_V50_2026"
MODEL_DATE = datetime.now().strftime("%Y-%m-%d %H:%M")

REQUIRED = [
    "PED_NUMERO_PEDIDO", "PED_CODIGO_CLIENTE", "PED_RESPONSABLE",
    "PED_CANAL_CODIGO", "PED_REGION", "PED_CONDICION_EXPEDICION_CODIGO",
    "PED_ESTADO_CREDITO", "SERV_TIPO_SERVICIO", "PED_VALOR_NETO",
    "PED_FECHA_HORA", "DH_ENTREGA_COMPLETA_100"
]

OPTIONAL_DEFAULTS = {
    "PED_CANAL": "SIN DATO", "PED_CONDICION_EXPEDICION": "SIN DATO",
    "SERV_TIPO_SERVICIO_PLANIFICADO": "SIN DATO", "PED_CIUDAD": "SIN DATO",
    "ES_FES": False, "ES_SALDO": False, "SEGMENTO_ANALISIS": "NORMAL",
    "ES_ULTIMOS_7_DIAS_HABILES_MES": False, "AUD_TOTAL_CRITICAS": 0,
    "AUD_ESTADO_GENERAL": "SIN AUDITORIA", "AUD_PRINCIPAL_INCONGRUENCIA": "",
    "DH_CREDITO_COBRANZAS": np.nan, "DH_OPERACION_INTERNA": np.nan,
    "DH_CREDITO_A_PRIMERA_ENTREGA": np.nan,
    "DH_PRIMERA_ENTREGA_A_PRIMER_PICKING": np.nan,
    "DH_PRIMER_PICKING_A_PRIMERA_FACTURA": np.nan,
    "DH_PRIMER_PACKING_A_PRIMERA_FACTURA": np.nan,
    "DH_DESPACHO": np.nan, "ES_CERRADO": np.nan,
    "ESTADO_ACTUAL": "SIN ESTADO", "HITO_ACTUAL": "SIN HITO",
    "DIAS_INTERNOS_DH": np.nan, "DIAS_EN_ESTADO_DH": np.nan,
    "DIAS_RESTANTES_DH": np.nan, "SLA_INTERNO_DH": np.nan, "FECHA_ACTUALIZACION": pd.NaT,
    "CLIENTE_NOMBRE": "", "VENDEDOR_NOMBRE": ""
}


def _safe_text(s: pd.Series, default: str = "SIN DATO") -> pd.Series:
    out = s.astype("string").fillna(default).str.strip()
    return out.mask(out.eq(""), default)


def _bool(s: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(s):
        return s.fillna(False)
    return s.astype(str).str.strip().str.lower().isin({"true", "1", "si", "sí", "yes"})


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def _dt(s: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(s):
        return pd.to_datetime(s, errors="coerce")
    n = pd.to_numeric(s, errors="coerce")
    if n.notna().mean() > 0.85:
        return pd.to_datetime(n, origin="1899-12-30", unit="D", errors="coerce")
    return pd.to_datetime(s, errors="coerce")


def _auc(y: np.ndarray, p: np.ndarray) -> float:
    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    pos = y == 1
    neg = y == 0
    if pos.sum() == 0 or neg.sum() == 0:
        return float("nan")
    order = np.argsort(p)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(p) + 1)
    return float((ranks[pos].sum() - pos.sum() * (pos.sum() + 1) / 2) / (pos.sum() * neg.sum()))


def _ap(y: np.ndarray, p: np.ndarray) -> float:
    order = np.argsort(-p)
    yy = np.asarray(y, dtype=int)[order]
    positives = yy.sum()
    if positives == 0:
        return float("nan")
    precision = np.cumsum(yy) / (np.arange(len(yy)) + 1)
    return float((precision * yy).sum() / positives)


def _metrics_class(y: np.ndarray, p: np.ndarray) -> Dict[str, float]:
    if SKLEARN_OK:
        return {
            "AUC": float(roc_auc_score(y, p)),
            "AP": float(average_precision_score(y, p)),
            "BRIER": float(brier_score_loss(y, p)),
        }
    return {
        "AUC": _auc(y, p),
        "AP": _ap(y, p),
        "BRIER": float(np.mean((np.asarray(y) - np.asarray(p)) ** 2)),
    }


def _metrics_reg(y: np.ndarray, pred: np.ndarray) -> Dict[str, float]:
    y = np.asarray(y, dtype=float)
    pred = np.asarray(pred, dtype=float)
    if SKLEARN_OK:
        return {
            "MAE": float(mean_absolute_error(y, pred)),
            "RMSE": float(math.sqrt(mean_squared_error(y, pred))),
            "R2": float(r2_score(y, pred)),
        }
    mae = float(np.mean(np.abs(y - pred)))
    rmse = float(np.sqrt(np.mean((y - pred) ** 2)))
    denom = float(np.sum((y - y.mean()) ** 2))
    r2 = float(1 - np.sum((y - pred) ** 2) / denom) if denom > 0 else float("nan")
    return {"MAE": mae, "RMSE": rmse, "R2": r2}


class FallbackLogit:
    def __init__(self, l2: float = 0.05, iterations: int = 1200, lr: float = 0.03):
        self.l2, self.iterations, self.lr = l2, iterations, lr
        self.coef_ = None
        self.intercept_ = None

    def fit(self, x: np.ndarray, y: np.ndarray):
        n, k = x.shape
        w = np.zeros(k + 1)
        xx = np.column_stack([np.ones(n), x])
        y = y.astype(float)
        pos = max(y.sum(), 1.0)
        neg = max(n - y.sum(), 1.0)
        weights = np.where(y == 1, n / (2 * pos), n / (2 * neg))
        for _ in range(self.iterations):
            z = np.clip(xx @ w, -25, 25)
            p = 1 / (1 + np.exp(-z))
            grad = xx.T @ ((p - y) * weights) / n
            grad[1:] += self.l2 * w[1:]
            w -= self.lr * grad
        self.intercept_ = np.array([w[0]])
        self.coef_ = np.array([w[1:]])
        return self

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        z = np.clip(x @ self.coef_[0] + self.intercept_[0], -25, 25)
        p = 1 / (1 + np.exp(-z))
        return np.column_stack([1 - p, p])


class FallbackRidge:
    def __init__(self, alpha: float = 2.0):
        self.alpha = alpha
        self.coef_ = None
        self.intercept_ = None

    def fit(self, x: np.ndarray, y: np.ndarray):
        xm = x.mean(axis=0)
        ym = float(np.mean(y))
        xc = x - xm
        yc = y - ym
        eye = np.eye(x.shape[1])
        self.coef_ = np.linalg.pinv(xc.T @ xc + self.alpha * eye) @ xc.T @ yc
        self.intercept_ = ym - xm @ self.coef_
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        return x @ self.coef_ + self.intercept_


def prepare(source: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    missing = [c for c in REQUIRED if c not in source.columns]
    if missing:
        raise ValueError("Faltan columnas obligatorias ML: " + ", ".join(missing))

    df = source.copy()
    for c, default in OPTIONAL_DEFAULTS.items():
        if c not in df.columns:
            df[c] = default

    df["PED_NUMERO_PEDIDO"] = _safe_text(df["PED_NUMERO_PEDIDO"])
    df["FECHA_ACTUALIZACION"] = _dt(df["FECHA_ACTUALIZACION"])
    dup_count = int(df["PED_NUMERO_PEDIDO"].duplicated(keep=False).sum())
    if dup_count:
        df = df.sort_values(["PED_NUMERO_PEDIDO", "FECHA_ACTUALIZACION"], na_position="first").drop_duplicates("PED_NUMERO_PEDIDO", keep="last")

    text_cols = [
        "PED_CODIGO_CLIENTE", "PED_RESPONSABLE", "PED_CANAL_CODIGO", "PED_CANAL",
        "PED_REGION", "PED_CONDICION_EXPEDICION_CODIGO", "PED_CONDICION_EXPEDICION",
        "PED_ESTADO_CREDITO", "SERV_TIPO_SERVICIO", "SERV_TIPO_SERVICIO_PLANIFICADO",
        "SEGMENTO_ANALISIS", "AUD_ESTADO_GENERAL", "AUD_PRINCIPAL_INCONGRUENCIA",
        "ESTADO_ACTUAL", "HITO_ACTUAL", "CLIENTE_NOMBRE", "VENDEDOR_NOMBRE"
    ]
    for c in text_cols:
        df[c] = _safe_text(df[c])

    df["PED_FECHA_HORA"] = _dt(df["PED_FECHA_HORA"])
    for c in [
        "PED_VALOR_NETO", "DH_ENTREGA_COMPLETA_100", "AUD_TOTAL_CRITICAS",
        "DH_CREDITO_COBRANZAS", "DH_OPERACION_INTERNA", "DH_CREDITO_A_PRIMERA_ENTREGA",
        "DH_PRIMERA_ENTREGA_A_PRIMER_PICKING", "DH_PRIMER_PICKING_A_PRIMERA_FACTURA",
        "DH_PRIMER_PACKING_A_PRIMERA_FACTURA", "DH_DESPACHO", "DIAS_INTERNOS_DH",
        "DIAS_EN_ESTADO_DH", "DIAS_RESTANTES_DH", "SLA_INTERNO_DH"
    ]:
        df[c] = _num(df[c])

    df["SLA_INTERNO_DH"] = df["SLA_INTERNO_DH"].fillna(np.where(df["PED_REGION"].str.lstrip("0").eq("13"), 4.0, 5.0))
    df["SLA_INTERNO_DH"] = df["SLA_INTERNO_DH"].clip(lower=1)

    df["ES_FES"] = _bool(df["ES_FES"])
    df["ES_SALDO"] = _bool(df["ES_SALDO"])
    df["ES_FIN_MES"] = _bool(df["ES_ULTIMOS_7_DIAS_HABILES_MES"])

    # Tracking vivo cuando está disponible; fallback: sin resultado = pendiente.
    cerrado_raw = df["ES_CERRADO"]
    has_tracking = cerrado_raw.notna().any()
    if has_tracking:
        df["ES_CERRADO_TRACKING"] = _bool(cerrado_raw)
        df["ES_PENDIENTE"] = ~df["ES_CERRADO_TRACKING"]
    else:
        df["ES_CERRADO_TRACKING"] = df["DH_ENTREGA_COMPLETA_100"].notna()
        df["ES_PENDIENTE"] = df["DH_ENTREGA_COMPLETA_100"].isna()

    df["PED_FECHA"] = df["PED_FECHA_HORA"].dt.normalize()
    df["MES_CREACION"] = df["PED_FECHA_HORA"].dt.strftime("%Y-%m")
    df["DIA_MES"] = df["PED_FECHA_HORA"].dt.day.fillna(0).astype(int)
    df["HORA_CREACION"] = df["PED_FECHA_HORA"].dt.hour.fillna(0).astype(int)
    df["DIA_SEMANA"] = df["PED_FECHA_HORA"].dt.dayofweek.fillna(0).astype(int).astype(str)
    df["SEMANA_MES"] = pd.cut(df["DIA_MES"], [0, 7, 14, 21, 31], labels=["1-7", "8-14", "15-21", "22-FIN"], include_lowest=True).astype("string").fillna("SIN DATO")
    df["VALOR_NETO"] = df["PED_VALOR_NETO"].fillna(0.0)
    df["VALOR_MM"] = df["VALOR_NETO"] / 1_000_000.0
    df["ZONA"] = np.where(df["PED_REGION"].str.lstrip("0").eq("13"), "Santiago", "Regiones")
    df["CLASIFICACION"] = np.select(
        [df["ES_FES"] & df["ES_SALDO"], df["ES_FES"], df["ES_SALDO"]],
        ["FES + SALDO", "FES", "SALDO"], default="NORMAL"
    )
    df["DH_TOTAL"] = df["DH_ENTREGA_COMPLETA_100"]
    df["Y_ATRASO_SLA"] = np.where(df["DH_TOTAL"].notna(), (df["DH_TOTAL"] > df["SLA_INTERNO_DH"]).astype(float), np.nan)

    df["ES_CALIDAD_VALIDA_ML"] = (
        df["DH_TOTAL"].notna()
        & df["DH_TOTAL"].between(0, MAX_TARGET_DH, inclusive="both")
        & df["AUD_TOTAL_CRITICAS"].fillna(0).eq(0)
        & ~df["AUD_ESTADO_GENERAL"].str.upper().eq("CRITICO")
    )
    df["ES_FLUJO_COMPLETO_ML"] = df["ES_CALIDAD_VALIDA_ML"] & ~df["ES_PENDIENTE"]

    reasons = np.select(
        [
            df["AUD_TOTAL_CRITICAS"].fillna(0).gt(0) | df["AUD_ESTADO_GENERAL"].str.upper().eq("CRITICO"),
            df["DH_TOTAL"].isna(),
            ~df["DH_TOTAL"].between(0, MAX_TARGET_DH, inclusive="both")
        ],
        ["AUDITORIA CRITICA", "FLUJO INCOMPLETO / PENDIENTE", "DIAS FUERA DE RANGO 0-60"],
        default="INCLUIDO EN ENTRENAMIENTO"
    )
    df["MOTIVO_EXCLUSION_ML"] = reasons
    df["AUD_DUPLICADOS_ENTRADA"] = dup_count
    return df.sort_values(["PED_FECHA_HORA", "PED_NUMERO_PEDIDO"]).reset_index(drop=True), dup_count


def add_prior_history(df: pd.DataFrame) -> pd.DataFrame:
    out = df.sort_values(["MES_CREACION", "PED_FECHA_HORA", "PED_NUMERO_PEDIDO"]).copy()
    complete = out[out["ES_FLUJO_COMPLETO_ML"]]
    base_rate = float(complete["Y_ATRASO_SLA"].mean()) if len(complete) else 0.15
    levels = [("CLIENTE", "PED_CODIGO_CLIENTE"), ("VENDEDOR", "PED_RESPONSABLE"), ("CANAL", "PED_CANAL_CODIGO")]
    for label, _ in levels:
        out[f"HIST_{label}_N"] = 0.0
        out[f"HIST_{label}_RIESGO"] = base_rate
    history: Dict[str, Dict[str, Tuple[int, int]]] = {label: {} for label, _ in levels}
    for month in sorted(out["MES_CREACION"].dropna().unique()):
        idx = out.index[out["MES_CREACION"].eq(month)]
        for i in idx:
            for label, col in levels:
                key = str(out.at[i, col])
                n, delayed = history[label].get(key, (0, 0))
                out.at[i, f"HIST_{label}_N"] = n
                out.at[i, f"HIST_{label}_RIESGO"] = (delayed + SMOOTHING_K * base_rate) / (n + SMOOTHING_K)
        for i in idx:
            if not bool(out.at[i, "ES_FLUJO_COMPLETO_ML"]):
                continue
            y = int(out.at[i, "Y_ATRASO_SLA"])
            for label, col in levels:
                key = str(out.at[i, col])
                n, delayed = history[label].get(key, (0, 0))
                history[label][key] = (n + 1, delayed + y)
    return out


NUM_FEATURES = [
    "LOG_VALOR", "VALOR_GE_2_6", "VALOR_GE_5", "DIA_MES_N", "HORA_N", "ES_FIN_MES_N",
    "HIST_CLIENTE_RIESGO", "HIST_CLIENTE_N_LOG", "HIST_VENDEDOR_RIESGO",
    "HIST_VENDEDOR_N_LOG", "HIST_CANAL_RIESGO", "HIST_CANAL_N_LOG"
]
CAT_FEATURES = [
    "CAT_CANAL", "CAT_VENDEDOR", "CAT_REGION", "CAT_CONDICION", "CAT_CREDITO",
    "CAT_SERVICIO", "CAT_SERVICIO_PLAN", "CAT_SEMANA", "CAT_DIA_SEMANA"
]


def build_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    x = pd.DataFrame(index=df.index)
    x["LOG_VALOR"] = np.log1p(df["VALOR_MM"].clip(lower=0))
    x["VALOR_GE_2_6"] = (df["VALOR_MM"] >= 2.6).astype(float)
    x["VALOR_GE_5"] = (df["VALOR_MM"] >= 5).astype(float)
    x["DIA_MES_N"] = df["DIA_MES"].astype(float)
    x["HORA_N"] = df["HORA_CREACION"].astype(float)
    x["ES_FIN_MES_N"] = df["ES_FIN_MES"].astype(float)
    x["HIST_CLIENTE_RIESGO"] = df["HIST_CLIENTE_RIESGO"].astype(float)
    x["HIST_CLIENTE_N_LOG"] = np.log1p(df["HIST_CLIENTE_N"].astype(float))
    x["HIST_VENDEDOR_RIESGO"] = df["HIST_VENDEDOR_RIESGO"].astype(float)
    x["HIST_VENDEDOR_N_LOG"] = np.log1p(df["HIST_VENDEDOR_N"].astype(float))
    x["HIST_CANAL_RIESGO"] = df["HIST_CANAL_RIESGO"].astype(float)
    x["HIST_CANAL_N_LOG"] = np.log1p(df["HIST_CANAL_N"].astype(float))
    x["CAT_CANAL"] = "CANAL=" + df["PED_CANAL_CODIGO"].astype(str)
    x["CAT_VENDEDOR"] = "VENDEDOR=" + df["PED_RESPONSABLE"].astype(str)
    x["CAT_REGION"] = "REGION=" + df["PED_REGION"].astype(str)
    x["CAT_CONDICION"] = "CONDICION=" + df["PED_CONDICION_EXPEDICION_CODIGO"].astype(str)
    x["CAT_CREDITO"] = "CREDITO=" + df["PED_ESTADO_CREDITO"].astype(str)
    x["CAT_SERVICIO"] = "SERVICIO=" + df["SERV_TIPO_SERVICIO"].astype(str)
    x["CAT_SERVICIO_PLAN"] = "SERVICIO_PLAN=" + df["SERV_TIPO_SERVICIO_PLANIFICADO"].astype(str)
    x["CAT_SEMANA"] = "SEMANA=" + df["SEMANA_MES"].astype(str)
    x["CAT_DIA_SEMANA"] = "DIA_SEMANA=" + df["DIA_SEMANA"].astype(str)
    return x


def encode_fit_transform(xraw: pd.DataFrame, train_idx: pd.Index):
    numeric = xraw[NUM_FEATURES].copy().fillna(0.0)
    cats = pd.get_dummies(xraw[CAT_FEATURES].astype("string").fillna("SIN DATO"), prefix="", prefix_sep="", dtype=float)
    x = pd.concat([numeric, cats], axis=1).astype(float)
    means = x.loc[train_idx, NUM_FEATURES].mean()
    stds = x.loc[train_idx, NUM_FEATURES].std(ddof=0).replace(0, 1).fillna(1)
    x.loc[:, NUM_FEATURES] = (x[NUM_FEATURES] - means) / stds
    return x, means, stds


def fit_model_pair(x: np.ndarray, y_cls: np.ndarray, y_reg: np.ndarray):
    if SKLEARN_OK:
        clf = LogisticRegression(max_iter=3000, C=0.8, solver="liblinear", class_weight=None, random_state=42)
        reg = Ridge(alpha=2.0)
    else:
        clf = FallbackLogit()
        reg = FallbackRidge(alpha=2.0)
    clf.fit(x, y_cls)
    reg.fit(x, y_reg)
    return clf, reg


def business_name(feature: str) -> str:
    prefixes = {
        "CANAL=": "Canal", "VENDEDOR=": "Vendedor", "REGION=": "Región",
        "CONDICION=": "Condición de expedición", "CREDITO=": "Estado de crédito",
        "SERVICIO=": "Tipo de servicio", "SERVICIO_PLAN=": "Servicio planificado",
        "SEMANA=": "Semana del mes", "DIA_SEMANA=": "Día de semana"
    }
    for p, label in prefixes.items():
        if feature.startswith(p):
            return f"{label}: {feature[len(p):]}"
    mapping = {
        "LOG_VALOR": "Monto del pedido", "VALOR_GE_2_6": "Monto >= 2,6 MM",
        "VALOR_GE_5": "Monto >= 5 MM", "DIA_MES_N": "Día del mes",
        "HORA_N": "Hora de creación", "ES_FIN_MES_N": "Fin de mes",
        "HIST_CLIENTE_RIESGO": "Historial previo del cliente",
        "HIST_CLIENTE_N_LOG": "Soporte histórico del cliente",
        "HIST_VENDEDOR_RIESGO": "Historial previo del vendedor",
        "HIST_VENDEDOR_N_LOG": "Soporte histórico del vendedor",
        "HIST_CANAL_RIESGO": "Historial previo del canal",
        "HIST_CANAL_N_LOG": "Soporte histórico del canal",
    }
    return mapping.get(feature, feature)


def top_contributions(x: np.ndarray, feature_names: List[str], coef: np.ndarray, top_n: int = 3):
    results = []
    feature_names = np.asarray(feature_names)
    for row in x:
        vals = row * coef
        idx = np.argsort(-vals)
        positive = [j for j in idx if vals[j] > 0][:top_n]
        names = [business_name(feature_names[j]) for j in positive]
        while len(names) < top_n:
            names.append("Riesgo base / combinación")
        results.append(names)
    return results


def area_action(row) -> Tuple[str, str]:
    hito = str(row.get("HITO_ACTUAL", "")).upper()
    estado = str(row.get("ESTADO_ACTUAL", "")).upper()
    credit = str(row.get("PED_ESTADO_CREDITO", "")).upper()
    factor = str(row.get("FACTOR_PRINCIPAL", ""))
    high_value = float(row.get("VALOR_MM", 0) or 0) >= 5
    if "CRED" in hito or "CRED" in estado or credit == "D":
        return "Crédito y Cobranzas", "Escalar liberación y bloqueo de crédito"
    if "PICK" in hito or "LOG" in hito or "ENTREGA" in hito:
        return "Logística", "Priorizar ingreso, picking o continuidad operativa"
    if "FACT" in hito:
        return "Facturación", "Priorizar emisión o cierre de factura"
    if "DESP" in hito or "MANIF" in hito or "TRANSP" in hito:
        return "Despacho", "Priorizar despacho, transporte o manifiesto"
    if high_value:
        return "Control de Gestión", "Priorizar pedido sobre CLP 5 MM y coordinar área responsable"
    if factor.startswith("Historial previo del cliente"):
        return "Comercial", "Seguimiento preventivo con cliente y vendedor"
    return "Operaciones", "Revisar hito actual y remover restricción principal"


def run_pipeline(source: pd.DataFrame) -> pd.DataFrame:
    df, dup_count = prepare(source)
    df = add_prior_history(df)
    full = df[df["ES_FLUJO_COMPLETO_ML"]].copy()
    if len(full) < 100 or full["Y_ATRASO_SLA"].nunique() < 2:
        raise ValueError("No hay suficientes pedidos completos y válidos para entrenar ambos resultados SLA.")

    months = sorted(full["MES_CREACION"].dropna().unique())
    max_month = df["MES_CREACION"].dropna().max()
    mature_months = [m for m in months if m < max_month]
    if len(mature_months) >= 2:
        test_month = mature_months[-1]
        train_months = mature_months[:-1]
        train_mask = full["MES_CREACION"].isin(train_months)
        test_mask = full["MES_CREACION"].eq(test_month)
    else:
        full_sorted = full.sort_values("PED_FECHA_HORA")
        cut = max(1, int(len(full_sorted) * 0.80))
        train_ids = set(full_sorted.iloc[:cut]["PED_NUMERO_PEDIDO"])
        train_mask = full["PED_NUMERO_PEDIDO"].isin(train_ids)
        test_mask = ~train_mask
        test_month = "HOLDOUT CRONOLOGICO"
        train_months = ["PRIMER 80% TEMPORAL"]

    xraw = build_feature_frame(df)
    full_idx = full.index
    xall, _, _ = encode_fit_transform(xraw, full_idx)
    feature_names = list(xall.columns)

    train_idx = full.index[train_mask]
    test_idx = full.index[test_mask]
    x_train = xall.loc[train_idx].to_numpy(dtype=float)
    x_test = xall.loc[test_idx].to_numpy(dtype=float)
    y_train_cls = df.loc[train_idx, "Y_ATRASO_SLA"].astype(int).to_numpy()
    y_test_cls = df.loc[test_idx, "Y_ATRASO_SLA"].astype(int).to_numpy()
    y_train_reg = df.loc[train_idx, "DH_TOTAL"].astype(float).to_numpy()
    y_test_reg = df.loc[test_idx, "DH_TOTAL"].astype(float).to_numpy()

    clf_val, reg_val = fit_model_pair(x_train, y_train_cls, y_train_reg)
    p_test = clf_val.predict_proba(x_test)[:, 1]
    d_test = np.clip(reg_val.predict(x_test), 0, MAX_TARGET_DH)
    mc = _metrics_class(y_test_cls, p_test)
    mr = _metrics_reg(y_test_reg, d_test)

    # Entrenamiento final: todos los pedidos de flujo completo y calidad válida.
    x_final = xall.loc[full_idx].to_numpy(dtype=float)
    y_final_cls = df.loc[full_idx, "Y_ATRASO_SLA"].astype(int).to_numpy()
    y_final_reg = df.loc[full_idx, "DH_TOTAL"].astype(float).to_numpy()
    clf, reg = fit_model_pair(x_final, y_final_cls, y_final_reg)

    x_score = xall.to_numpy(dtype=float)
    prob = np.clip(clf.predict_proba(x_score)[:, 1], 0.001, 0.999)
    pred_days_raw = np.clip(reg.predict(x_score), 0, MAX_TARGET_DH)
    current_days = df["DIAS_INTERNOS_DH"].fillna(0).clip(lower=0).to_numpy(float)
    pred_days = np.maximum(pred_days_raw, current_days)

    clf_coef = np.asarray(clf.coef_)[0]
    reg_coef = np.asarray(reg.coef_)
    top_risk = top_contributions(x_score, feature_names, clf_coef, 3)
    top_days = top_contributions(x_score, feature_names, reg_coef, 1)

    df["PROB_ML_ATRASO"] = prob
    df["DH_PREDICHO_ML"] = np.round(pred_days, 1)
    df["DH_PREDICHO_BASE_ML"] = np.round(pred_days_raw, 1)
    df["DIAS_ACTUALES_DH"] = current_days
    df["DIAS_RESTANTES_PREDICHOS"] = np.maximum(pred_days - current_days, 0).round(1)
    df["SLA_CONSUMIDO_PCT"] = np.clip(current_days / df["SLA_INTERNO_DH"].to_numpy(float), 0, 3)
    df["FEATURE_TOP1"] = [r[0] for r in top_risk]
    df["FEATURE_TOP2"] = [r[1] for r in top_risk]
    df["FEATURE_TOP3"] = [r[2] for r in top_risk]
    df["FACTOR_DIAS_PRINCIPAL"] = [r[0] for r in top_days]
    df["FACTOR_PRINCIPAL"] = df["FEATURE_TOP1"]

    df["RIESGO_ATRASO"] = np.select(
        [df["ES_PENDIENTE"] & (df["DIAS_ACTUALES_DH"] > df["SLA_INTERNO_DH"]), prob >= RISK_HIGH, prob >= RISK_MEDIUM],
        ["ATRASADO", "ALTO", "MEDIO"], default="BAJO"
    )
    df["PREDICCION_SLA"] = np.where((prob >= 0.50) | (pred_days > df["SLA_INTERNO_DH"].to_numpy(float)), "PROBABLE INCUMPLIMIENTO", "PROBABLE CUMPLIMIENTO")
    df["BANDA_DIAS_PREDICHOS"] = pd.cut(
        df["DH_PREDICHO_ML"], [-0.001, 5, 7, 10, np.inf],
        labels=["0-4/5 DH", "+1-2 DH", "+3-5 DH", ">5 DH exceso"], include_lowest=True
    ).astype(str)
    value_pressure = np.clip(df["VALOR_MM"].to_numpy(float) / 5.0, 0, 1)
    sla_pressure = np.clip(df["SLA_CONSUMIDO_PCT"].to_numpy(float) / 1.5, 0, 1)
    df["PRIORIDAD_SCORE"] = np.round(100 * (0.65 * prob + 0.25 * sla_pressure + 0.10 * value_pressure), 1)

    df["ESTADO_SLA"] = np.select(
        [df["ES_PENDIENTE"] & (df["DIAS_ACTUALES_DH"] > df["SLA_INTERNO_DH"]), df["ES_PENDIENTE"], df["DH_TOTAL"] > df["SLA_INTERNO_DH"]],
        ["FUERA_SLA_ACTUAL", "PENDIENTE", "FUERA_SLA"], default="CUMPLE"
    )
    df["DH_CREDITO"] = df["DH_CREDITO_COBRANZAS"].fillna(0)
    df["DH_OPERACIONES"] = df["DH_OPERACION_INTERNA"].fillna(0)
    df["DH_DESPACHO"] = df["DH_DESPACHO"].fillna(0)
    df["DH_PICKING"] = (df["DH_PRIMERA_ENTREGA_A_PRIMER_PICKING"].fillna(0) + df["DH_PRIMER_PICKING_A_PRIMERA_FACTURA"].fillna(0))
    df["DH_FACTURACION"] = df["DH_PRIMER_PACKING_A_PRIMERA_FACTURA"].fillna(0)
    comp = pd.DataFrame({"CREDITO": df["DH_CREDITO"], "OPERACIONES": df["DH_OPERACIONES"], "DESPACHO": df["DH_DESPACHO"], "PICKING": df["DH_PICKING"]})
    df["FASE_MAS_LENTA"] = comp.idxmax(axis=1)
    df["DH_FASE_LENTA"] = comp.max(axis=1)
    df["FACTOR_HISTORICO"] = np.select(
        [df["ES_FES"] & df["ES_SALDO"], df["ES_FES"], df["ES_SALDO"]],
        ["FES + SALDO", "FES", "SALDO"],
        default=df["FASE_MAS_LENTA"]
    )
    # En pendientes predomina la explicación predictiva; en cerrados, la etapa histórica observada.
    df["FACTOR_PRINCIPAL"] = np.where(df["ES_PENDIENTE"], df["FEATURE_TOP1"], df["FACTOR_HISTORICO"])

    areas, actions = [], []
    for _, row in df.iterrows():
        area, action = area_action(row)
        areas.append(area)
        actions.append(action)
    df["RESPONSABLE_AREA"] = areas
    df["ACCION_RECOMENDADA"] = actions

    df["CLIENTE"] = np.where(df["CLIENTE_NOMBRE"].str.upper().eq("SIN DATO"), df["PED_CODIGO_CLIENTE"], df["CLIENTE_NOMBRE"])
    df["VENDEDOR"] = np.where(df["VENDEDOR_NOMBRE"].str.upper().eq("SIN DATO"), df["PED_RESPONSABLE"], df["VENDEDOR_NOMBRE"])
    df["ES_FIN_MES"] = np.where(df["ES_FIN_MES"], "Si", "No")
    df["MODELO_ML"] = "Regresión logística + regresión lineal regularizada"
    df["MODELO_VERSION"] = MODEL_VERSION
    df["MODELO_FECHA"] = MODEL_DATE
    df["MODELO_VALIDADO"] = True
    df["MODELO_DEPENDENCIA"] = "scikit-learn" if SKLEARN_OK else "numpy fallback"
    df["MODELO_FUENTE_SCORE"] = "ML entrenado con flujo completo; sin FES/Saldo como predictores iniciales"
    df["N_ENTRENAMIENTO_FINAL"] = len(full_idx)
    df["N_TRAIN_VALIDACION"] = len(train_idx)
    df["N_TEST_VALIDACION"] = len(test_idx)
    df["MES_TEST_VALIDACION"] = str(test_month)
    df["MESES_TRAIN_VALIDACION"] = ", ".join(map(str, train_months))
    df["AUC_TEST"] = mc["AUC"]
    df["AP_TEST"] = mc["AP"]
    df["BRIER_TEST"] = mc["BRIER"]
    df["MAE_DIAS_TEST"] = mr["MAE"]
    df["RMSE_DIAS_TEST"] = mr["RMSE"]
    df["R2_DIAS_TEST"] = mr["R2"]
    df["TASA_INCUMPLIMIENTO_SLA_ENTRENAMIENTO"] = float(full["Y_ATRASO_SLA"].mean())
    df["PEDIDOS_PENDIENTES_MODELO"] = int(df["ES_PENDIENTE"].sum())
    df["PEDIDOS_PENDIENTES_ALTO"] = int((df["ES_PENDIENTE"] & df["RIESGO_ATRASO"].isin(["ALTO", "ATRASADO"])).sum())
    df["ATRASOS_ESPERADOS_PENDIENTES"] = float(df.loc[df["ES_PENDIENTE"], "PROB_ML_ATRASO"].sum())

    df["ES_ENTRENAMIENTO_FINAL"] = df["ES_FLUJO_COMPLETO_ML"]
    df["ES_VALIDACION_TEST"] = df.index.isin(test_idx)

    output_cols = [
        "PED_NUMERO_PEDIDO", "PED_FECHA", "MES_CREACION", "PED_CODIGO_CLIENTE", "CLIENTE",
        "PED_RESPONSABLE", "VENDEDOR", "PED_CANAL_CODIGO", "PED_CANAL", "PED_REGION", "ZONA",
        "PED_CONDICION_EXPEDICION_CODIGO", "PED_CONDICION_EXPEDICION", "PED_ESTADO_CREDITO",
        "SERV_TIPO_SERVICIO", "VALOR_NETO", "VALOR_MM", "DIA_MES", "SEMANA_MES", "ES_FIN_MES",
        "CLASIFICACION", "ES_FES", "ES_SALDO", "ES_PENDIENTE", "ES_CERRADO_TRACKING",
        "ESTADO_ACTUAL", "HITO_ACTUAL", "FECHA_ACTUALIZACION", "DIAS_ACTUALES_DH", "DIAS_EN_ESTADO_DH",
        "DH_TOTAL", "ESTADO_SLA", "PROB_ML_ATRASO", "RIESGO_ATRASO", "PREDICCION_SLA",
        "DH_PREDICHO_ML", "DH_PREDICHO_BASE_ML", "DIAS_RESTANTES_PREDICHOS", "BANDA_DIAS_PREDICHOS",
        "SLA_CONSUMIDO_PCT", "PRIORIDAD_SCORE", "FACTOR_PRINCIPAL", "FACTOR_HISTORICO", "FEATURE_TOP1", "FEATURE_TOP2",
        "FEATURE_TOP3", "FACTOR_DIAS_PRINCIPAL", "RESPONSABLE_AREA", "ACCION_RECOMENDADA",
        "DH_CREDITO", "DH_OPERACIONES", "DH_PICKING", "DH_FACTURACION", "DH_DESPACHO",
        "FASE_MAS_LENTA", "DH_FASE_LENTA", "ES_FLUJO_COMPLETO_ML", "ES_CALIDAD_VALIDA_ML",
        "ES_ENTRENAMIENTO_FINAL", "ES_VALIDACION_TEST", "MOTIVO_EXCLUSION_ML", "AUD_ESTADO_GENERAL",
        "AUD_TOTAL_CRITICAS", "AUD_PRINCIPAL_INCONGRUENCIA", "AUD_DUPLICADOS_ENTRADA",
        "MODELO_ML", "MODELO_VERSION", "MODELO_FECHA", "MODELO_VALIDADO", "MODELO_DEPENDENCIA",
        "MODELO_FUENTE_SCORE", "N_ENTRENAMIENTO_FINAL", "N_TRAIN_VALIDACION", "N_TEST_VALIDACION",
        "MESES_TRAIN_VALIDACION", "MES_TEST_VALIDACION", "AUC_TEST", "AP_TEST", "BRIER_TEST",
        "MAE_DIAS_TEST", "RMSE_DIAS_TEST", "R2_DIAS_TEST", "TASA_INCUMPLIMIENTO_SLA_ENTRENAMIENTO",
        "PEDIDOS_PENDIENTES_MODELO", "PEDIDOS_PENDIENTES_ALTO", "ATRASOS_ESPERADOS_PENDIENTES"
    ]
    return df[output_cols].sort_values(["ES_PENDIENTE", "PRIORIDAD_SCORE", "PED_NUMERO_PEDIDO"], ascending=[False, False, True]).reset_index(drop=True)


# Power BI reconoce la salida por el nombre `dataset`.
dataset = run_pipeline(dataset)
