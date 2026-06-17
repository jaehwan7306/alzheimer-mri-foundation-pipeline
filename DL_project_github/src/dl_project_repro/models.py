from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset


class CachedFeatureDataset(Dataset):
    def __init__(self, cached, indices):
        self.features = cached["features"]
        self.labels = cached["labels"].long()
        self.patient_ids = cached["patient_ids"]
        self.indices = np.asarray(indices, dtype=np.int64)

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, item):
        index = int(self.indices[item])
        return self.features[index].float(), self.labels[index], self.patient_ids[index]


class AdapterProbe(nn.Module):
    def __init__(self, input_dim=512, hidden_dim=128, dropout=0.2):
        super().__init__()
        self.norm = nn.LayerNorm(input_dim)
        self.adapter = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, input_dim),
        )
        self.classifier = nn.Linear(input_dim, 2)

    def forward(self, features):
        normalized = self.norm(features)
        adapted = normalized + self.adapter(normalized)
        return self.classifier(adapted)


def count_trainable_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def indices_for_patient_ids(cached, patient_ids):
    patient_set = set(patient_ids)
    return [i for i, pid in enumerate(cached["patient_ids"]) if pid in patient_set]
