# -*- coding: utf-8 -*-
"""Project Datasciences seance 3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/103KCqTNoO7-fLRgK8ovZuF1VX4-wAPKF
"""

import torch
import numpy as np
from torch.utils.data import random_split, DataLoader
import pandas as pd
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from google.colab import drive
import torch.nn as nn
import torch.nn.functional as F
drive.mount('/content/drive')


def transform(sample):
    """
    Fonction pour transformer un échantillon en un tenseur et son label
    :param sample: le dataframe de l'échantillon a transformer
    :return: les features et le label
    """
    features = torch.tensor(sample.iloc[:-1].values.astype(np.float32))
    target = torch.tensor(sample.iloc[-1], dtype=torch.long)
    return features, target

def normalize_data(features):
    """
    Fonction pour normaliser les features en utilisant la moyenne
    :param features: les features à normaliser
    :return: les features avec leurs valeurs normalisées
    """
    mean = features.mean()
    std = features.std()
    normalized_features = (features - mean) / std
    return normalized_features

class CustomDataset(Dataset):
    """
    Un Dataset personnalisé pour charger et traiter les données à partir d'un fichier CSV.
    Les données peuvent être transformées et normalisées selon des fonctions fournies.
    """
    def __init__(self, csv_file, transform=None, normalize=None):
        """
        Initialise le dataset en chargeant des données à partir d'un fichier CSV, encode les labels,
        et applique les fonctions de transformation et de normalisation si fournies.
        :param csv_file: Chemin du fichier CSV contenant les données.
        :param transform: Fonction optionnelle pour transformer les échantillons.
        :param normalize: Fonction optionnelle pour normaliser les features numériques.
        """
        # Chargement des données à partir du fichier CSV
        self.data = pd.read_csv(csv_file)
        self.label_encoder = LabelEncoder()

        # Encodage des labels pour convertir de catégorique à numérique
        self.data['label'] = self.label_encoder.fit_transform(self.data['label'])

        # Identification et traitement des colonnes numériques
        numerical_cols = self.data.columns[self.data.dtypes != 'object'].tolist()
        numerical_cols = [col for col in numerical_cols if col != 'label']
        # Remplissage des valeurs manquantes par la moyenne de chaque colonne
        self.data[numerical_cols] = self.data[numerical_cols].apply(lambda x: x.fillna(x.mean()), axis=0)

        self.transform = transform  # Fonction de transformation à appliquer aux données
        self.normalize = normalize  # Fonction de normalisation à appliquer aux features

    def __len__(self):
        """
        Retourne la taille du dataset.
        """
        return len(self.data)

    def __getitem__(self, idx):
        """
        Récupère un échantillon et son label par index, applique transformation et normalisation, et retourne le résultat.
        :param idx: Index de l'échantillon à récupérer.
        :return: Un tuple contenant les features normalisées et le label de l'échantillon.
        """
        sample = self.data.iloc[idx]
        if self.transform:
            sample = self.transform(sample)
        if self.normalize:
            sample = (self.normalize(sample[0]), sample[1])
        return sample


class SimpleNet(nn.Module):
    """
    Réseau de neurones simple avec une couche cachée.
    """
    def __init__(self, input_size, hidden_size, num_classes):
        """
        Initialise le réseau.
        :param input_size: taille des features d'entrée.
        :param hidden_size: taille de la couche cachée.
        :param num_classes: nombre de classes pour la sortie. (ici nombre d'activités)
        """
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size) # couche linéaire cachée
        self.relu = nn.ReLU() # fonction d'activation ReLU
        self.fc2 = nn.Linear(hidden_size, num_classes) # couche linéaire de sortie

    def forward(self, x):
        """
        Propagation avant du réseau.
        :param x: entrée du réseau.
        :return: sortie du réseau.
        """
        out = self.fc1(x) # couche linéaire cachée
        out = self.relu(out) # fonction d'activation ReLU
        out = self.fc2(out) # couche linéaire de sortie
        return out


def train(model, device, train_loader, criterion, optimizer, num_epochs):
    """
    Fonction pour entraîner le modèle.
    :param model: le modèle à entraîner.
    :param device: périphérique de calcul (GPU ou CPU).
    :param train_loader: DataLoader pour les données d'entraînement.
    :param criterion: fonction de perte.
    :param optimizer: optimiseur pour la mise à jour des poids du modèle.
    :param num_epochs: nombre total d'époques pour l'entraînement.
    """
    model.train() # on met le modèle en mode entraînement
    # on boucle sur les époques
    for epoch in range(num_epochs):
        # on boucle sur les batchs
        for i, (features, labels) in enumerate(train_loader):
            # on envoie les données sur le périphérique de calcul
            features = features.to(device)
            labels = labels.to(device)

            # propagation avant
            outputs = model(features)
            # calcul de la perte
            loss = criterion(outputs, labels)

            # rétropropagation et optimisation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # affichage de la perte à chaque époque
        print ('Epoch [{}/{}], Loss: {:.4f}'.format(epoch+1, num_epochs, loss.item()))


def test(model, device, test_loader):
    """
    Fonction pour tester le modèle sur des données de test.
    :param model: modèle à tester.
    :param device: périphérique de calcul (GPU ou CPU).
    :param test_loader: DataLoader pour les données de test.
    """
    model.eval() # on met le modèle en mode évaluation
    correct = 0 # nombre de prédictions correctes
    total = 0 # nombre total de prédictions
    with torch.no_grad():
        # on boucle sur les batchs
        for features, labels in test_loader:
            # on envoie les données sur le périphérique de calcul
            features = features.to(device)
            labels = labels.to(device)

            # propagation avant
            outputs = model(features)

            # on récupère la prédiction
            _, predicted = torch.max(outputs.data, 1)

            total += labels.size(0)
            correct += (predicted == labels).sum().item() # on incrémente le nombre de prédictions correctes

    # on calcul et on affiche la précision du modèle (pourcentage de prédictions correctes dans l'ensemble de test)
    accuracy = 100 * correct / total
    print('Test Accuracy of the model on the test samples: {:.2f} %'.format(accuracy))
    return accuracy

# initialisation du dataset pour les données des activités labelisées provenant du fichier CSV
custom_dataset = CustomDataset("/content/drive/My Drive/data.csv",transform=transform, normalize=normalize_data)

# on divise le dataset en données d'entraînement et de test
train_size = int(0.5 * len(custom_dataset)) # 50% des données pour l'entraînement
test_size = len(custom_dataset) - train_size # le reste des données pour le test
train_dataset, test_dataset = random_split(custom_dataset, [train_size, test_size]) # division aléatoire

# initialisation des DataLoader pour les données d'entraînement et de test
train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=4, shuffle=False)

# initialisation du périphérique de calcul, on utilise le GPU s'il est disponible
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# initialisation des paramètres du modèle
input_size = custom_dataset[0][0].shape[0] # taille des features d'entrée
hidden_size = 100 # taille de la couche cachée
num_classes = len(custom_dataset.label_encoder.classes_) # nombre de classes pour la sortie
num_epochs = 20 # nombre d'époques pour l'entraînement
learning_rate = 0.001 # taux d'apprentissage

# initialisation du modèle, de la fonction de perte et de l'optimiseur
model = SimpleNet(input_size, hidden_size, num_classes).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# entraînement du modèle
train(model, device, train_loader, criterion, optimizer, num_epochs)

# test du modèle
accuracy = test(model, device, test_loader)

# sauvegarde du modèle avec le nom du fichier contenant les paramètres utilisés et la précision du modèle
filename = f"/content/drive/My Drive/model_projet_{hidden_size}_{num_epochs}_{learning_rate}_{round(accuracy, 2)}.pth"
torch.save(model.state_dict(), filename)