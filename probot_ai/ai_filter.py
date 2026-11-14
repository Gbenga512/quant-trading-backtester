"""Optional ML market-movement filter with chronological, purged validation."""
import joblib
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
        df["label"] = (future_return.abs() > threshold).astype("float")
        df.loc[future_return.isna(), "label"] = float("nan")
        data = df.dropna(subset=FEATURES+["label"])
        if len(data) < 500:
            raise ValueError("At least 500 labelled observations are required.")
        split = int(len(data)*0.8)
        # Purge the label horizon at the boundary to prevent future leakage.
        train, test = data.iloc[:max(0, split-horizon)], data.iloc[split:]
        if train.empty or test.empty or train.label.nunique() < 2:
            raise ValueError("Training data must contain both classes and a valid chronological test set.")
        self.model = RandomForestClassifier(n_estimators=300, max_depth=7,
                    min_samples_leaf=10, class_weight="balanced", random_state=42)
        self.model.fit(train[FEATURES], train.label.astype(int))
        pred = self.model.predict(test[FEATURES])
        return classification_report(test.label.astype(int), pred, output_dict=True, zero_division=0)

    def probability(self, row):
        if self.model is None:
            raise RuntimeError("Model is not trained or loaded")
        classes = list(self.model.classes_)
        if 1 not in classes:
            return 0.0
        return float(self.model.predict_proba(row[FEATURES].to_frame().T)[0][classes.index(1)])

    def save(self):
        import os
        os.makedirs("models", exist_ok=True)
        joblib.dump(self.model, self.path)

    def load(self):
        self.model = joblib.load(self.path)
        return self
