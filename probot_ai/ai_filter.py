"""Optional ML trade filter. Requires a chronological, leakage-aware training dataset."""
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

FEATURES = ["ema_fast", "ema_slow", "ema_trend", "rsi", "adx", "atr"]

class TradeQualityModel:
    def __init__(self, path="models/trade_quality.joblib"):
        self.path = path
        self.model = None

    def fit(self, frame, horizon=3, min_move_atr=0.25):
        df = frame.copy()
        future_return = df.close.shift(-horizon) / df.close - 1
        threshold = (df.atr / df.close) * min_move_atr
        df["label"] = (future_return.abs() > threshold).astype(int)
        data = df.dropna(subset=FEATURES+["label"])
        if len(data) < 500:
            raise ValueError("At least 500 labelled observations are required.")
        split = int(len(data)*0.8)
        train, test = data.iloc[:split], data.iloc[split:]
        self.model = RandomForestClassifier(n_estimators=300, max_depth=7,
                    min_samples_leaf=10, class_weight="balanced", random_state=42)
        self.model.fit(train[FEATURES], train.label)
        pred = self.model.predict(test[FEATURES])
        return classification_report(test.label, pred, output_dict=True, zero_division=0)

    def probability(self, row):
        if self.model is None:
            raise RuntimeError("Model is not trained or loaded")
        return float(self.model.predict_proba(row[FEATURES].to_frame().T)[0][1])

    def save(self):
        import os
        os.makedirs("models", exist_ok=True)
        joblib.dump(self.model, self.path)

    def load(self):
        self.model = joblib.load(self.path)
        return self
