"""Reusable clustering helpers for EduPro."""
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

def fit_segments(learners, feature_columns, max_k=8):
    frame = learners.copy()
    X = frame[feature_columns].replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median(numeric_only=True)).fillna(0)
    if len(frame) < 3 or X.nunique().sum() <= 1:
        frame["segment_id"] = 0
        frame["pca_x"], frame["pca_y"] = 0.0, 0.0
        return frame, {"best_k": 1, "cluster_eval": [], "hierarchical_silhouette": 0.0, "pca_variance": [0, 0]}
    scaled = StandardScaler().fit_transform(X)
    scores = []
    for k in range(2, min(max_k, len(frame)-1)+1):
        labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(scaled)
        if len(set(labels)) > 1:
            scores.append({"k": k, "silhouette": float(silhouette_score(scaled, labels))})
    best_k = max(scores, key=lambda r:r["silhouette"])["k"] if scores else 2
    labels = KMeans(n_clusters=best_k, random_state=42, n_init=10).fit_predict(scaled)
    frame["segment_id"] = labels
    h_labels = AgglomerativeClustering(n_clusters=best_k, linkage="ward").fit_predict(scaled)
    h_score = float(silhouette_score(scaled, h_labels)) if len(set(h_labels)) > 1 else 0.0
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(scaled)
    frame["pca_x"], frame["pca_y"] = coords[:,0], coords[:,1]
    return frame, {"best_k":best_k, "cluster_eval":scores, "hierarchical_silhouette":h_score,
                   "pca_variance":pca.explained_variance_ratio_.tolist()}
