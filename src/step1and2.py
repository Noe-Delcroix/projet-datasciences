import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# chemin vers les fichiers de la bdd
RESOURCE_PATH = "..\\resources"

# chemin de sortie du csv mergé
outPath = "..\\out"


def get_grouped_mod(mod_number):
    """
    Récupère les données des 8 parties du module et les regroupe dans un dataframe
    :param mod_number: le numéro du module
    :return: le dataframe regroupant les données des 8 parties du module
    """
    # création du dataframe global
    modGrouped = pd.DataFrame(
        columns=["Time", "RH", "Temperature", "TGS4161", "MICS2714", "TGS2442", "MICS5524", "TGS2602", "TGS2620"])

    # on itère sur les 8 parties du module
    for part in range(1, 9):
        # on charge les données de la partie a partir du fichier txt
        mod = pd.read_csv(RESOURCE_PATH + "\\Libelium New\\part" + str(part) + "\\mod" + str(mod_number) + ".txt",
                          sep="\t",
                          header=None, names=(
                "Time", "RH", "Temperature", "TGS4161", "MICS2714", "TGS2442", "MICS5524", "TGS2602", "TGS2620"))
        # on ajoute la partie au dataframe global
        modGrouped = pd.concat([modGrouped, mod])

    # conversion des dates en datetime
    modGrouped["Time"] = pd.to_datetime(modGrouped["Time"], dayfirst=True).dt.tz_localize('UTC+01:00',
                                                                                          ambiguous='infer')
    # tri par date
    modGrouped = modGrouped.sort_values(by="Time")
    return modGrouped


def get_grouped_pod(pod_number):
    """
    Récupère les données des 3 parties des données d'un pod et les regroupe dans un dataframe
    :param pod_number: le numéro du pod
    :return: le dataframe regroupant les données des 3 parties des données du pod souhaité
    """
    # charmement des 3 fichiers csv
    pod_1 = pd.read_csv(RESOURCE_PATH + "\\PODs\\14_nov-22_nov-Pods\\POD " + str(pod_number) + ".csv", sep=";",
                        skiprows=(1, 2, 3, 4))
    pod_2 = pd.read_csv(RESOURCE_PATH + "\\PODs\\23_nov-12_dec-Pods\\POD " + str(pod_number) + ".csv", sep=";",
                        skiprows=(1, 2, 3, 4))
    pod_3 = pd.read_csv(RESOURCE_PATH + "\\PODs\\fevrier_mars_2023_pods\\POD " + str(pod_number) + ".csv", sep=";",
                        skiprows=(1, 2, 3, 4))

    # regroupement des données
    groupedPod = pd.concat([pod_1, pod_2, pod_3])

    # renommage des colonnes
    groupedPod.rename(columns={"date": "Time"}, inplace=True)
    groupedPod.rename(columns={"temperature": "Temperature"}, inplace=True)

    # conversion des dates en datetime si besoin
    groupedPod["Time"] = pd.to_datetime(groupedPod["Time"], dayfirst=True)
    if groupedPod["Time"].dt.tz is not None:
        groupedPod["Time"] = groupedPod["Time"].dt.tz_convert('UTC+01:00')
    else:
        groupedPod["Time"] = groupedPod["Time"].dt.tz_localize('UTC', ambiguous='infer').dt.tz_convert('UTC+01:00')

    # suppression des doublons
    groupedPod = groupedPod.drop_duplicates(subset="Time")

    # suppression des colonnes inutiles
    groupedPod = groupedPod.drop(columns=['element', 'aqi', 'Unnamed: 14'])

    # tri par date
    groupedPod = groupedPod.sort_values(by="Time")
    return groupedPod


def get_groupe_piano(name):
    """
    Récupère les données des 3 parties des données d'un module piano et les regroupe dans un dataframe
    :param name: le nom du module piano
    :return: le dataframe regroupant les données des 3 parties des données du module piano souhaité
    """

    # chargement des fichiers
    piano1 = pd.read_csv(RESOURCE_PATH + "\\Piano\\14_nov-22_nov-Piano\\IMT_" + name + ".csv", sep=";",
                         skiprows=(1, 2, 3, 4))
    piano2 = pd.read_csv(RESOURCE_PATH + "\\Piano\\23_nov-12_dec-Piano\\IMT_" + name + ".csv", sep=";",
                         skiprows=(1, 2, 3, 4))
    piano3 = pd.read_csv(RESOURCE_PATH + "\\Piano\\fevrier_mars_2023_piano\\IMT_" + name + ".csv", sep=";",
                         skiprows=(1, 2, 3, 4))

    # regroupement des données
    groupedPiano = pd.concat([piano1, piano2, piano3])

    # renommage des colonnes
    groupedPiano.rename(columns={"date": "Time"}, inplace=True)
    groupedPiano.rename(columns={"temperature": "Temperature"}, inplace=True)

    # suppression des éventuels doublons
    groupedPiano = groupedPiano.drop_duplicates(subset="Time")

    # suppression des colonnes inutiles
    groupedPiano = groupedPiano.loc[:, ~groupedPiano.columns.str.contains('aqi|qai|iaq|element|Unnamed')]

    # conversion des dates en datetime si besoin
    groupedPiano["Time"] = pd.to_datetime(groupedPiano["Time"], dayfirst=True)
    if groupedPiano["Time"].dt.tz is not None:
        groupedPiano["Time"] = groupedPiano["Time"].dt.tz_convert('UTC+01:00')
    else:
        groupedPiano["Time"] = groupedPiano["Time"].dt.tz_localize('UTC', ambiguous='infer').dt.tz_convert('UTC+01:00')

    # tri par date
    groupedPiano = groupedPiano.sort_values(by="Time")
    return groupedPiano


def plot_test(mod1, mod2, pod200085, pico, thick, thin):
    """
    Affiche les graphes des données des modules et des pods
    :param mod1: dataframe des données du module 1
    :param mod2: dataframe des données du module 2
    :param pod200085: dataframe des données du pod 200085
    :param pico: dataframe des données du module PICO
    :param thick: dataframe des données du module Thick
    :param thin: dataframe des données du module Thin
    """
    plt.figure(figsize=(12, 10))
    date_format = mdates.DateFormatter('%d-%b')

    plt.subplot(3, 2, 1)  # MOD1
    plt.subplots_adjust(top=8)
    plt.title("MOD1 (Temperature x Time)")
    plt.plot(mod1['Time'], mod1['Temperature'])
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.xticks(rotation=45)

    plt.subplot(3, 2, 2)  # MOD2
    plt.subplots_adjust(top=8)
    plt.title("MOD2 (Temperature x Time)")
    plt.plot(mod2['Time'], mod2['Temperature'])
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.xticks(rotation=45)

    plt.subplot(3, 2, 3)  # POD 200085
    plt.subplots_adjust(top=8)
    plt.title("POD 200085 (Temperature x Time)")
    plt.plot(pod200085['Time'], pod200085['Temperature'])
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.xticks(rotation=45)

    plt.subplot(3, 2, 4)  # Piano PICO
    plt.subplots_adjust(top=8)
    plt.title("PICO (Temperature x Time)")
    plt.plot(pico['Time'], pico['bme68x_temp'])
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.xticks(rotation=45)

    plt.subplot(3, 2, 5)  # Piano Thick
    plt.subplots_adjust(top=8)
    plt.title("THICK (TGS2620 x Time)")
    plt.plot(thick['Time'], thick['piano_TGS2620I00'])
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.xticks(rotation=45)

    plt.subplot(3, 2, 6)  # Piano Thin
    plt.subplots_adjust(top=8)
    plt.title("THIN (GM102B x Time)")
    plt.plot(thin['Time'], thin['piano_GM102BI00'])
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()


# récupération des données groupées
mod1 = get_grouped_mod(1)
mod2 = get_grouped_mod(2)

pod200085 = get_grouped_pod(200085)
pod200086 = get_grouped_pod(200086)
pod200088 = get_grouped_pod(200088)

pico = get_groupe_piano("PICO")
thick = get_groupe_piano("Thick")
thin = get_groupe_piano("Thin")

# on gère le cas des modules mod qui n'ont pas les mêmes écarts de temps entre chaque mesures
# pour ce faire on arrondit les dates a des intervalles de 10 secondes, en prenant la moyenne des valeurs
mod1['Time'] = mod1['Time'].dt.round('10s')
mod2['Time'] = mod2['Time'].dt.round('10s')
mod1_mean = mod1.groupby('Time').mean().reset_index()
mod2_mean = mod2.groupby('Time').mean().reset_index()

# affichage des graphiques des données des fichiers chargés
# plotTest(mod1,mod2,pod200085,pico,thick,thin)

# ajout de suffixe des noms des modules aux noms des colonnes
mod1_mean.columns = ['Time'] + [f"{col}_mod1" for col in mod1_mean.columns if col != 'Time']
mod2_mean.columns = ['Time'] + [f"{col}_mod2" for col in mod2_mean.columns if col != 'Time']
pod200085.columns = ['Time'] + [f"{col}_pod200085" for col in pod200085.columns if col != 'Time']
pod200086.columns = ['Time'] + [f"{col}_pod200086" for col in pod200086.columns if col != 'Time']
pod200088.columns = ['Time'] + [f"{col}_pod200088" for col in pod200088.columns if col != 'Time']
pico.columns = ['Time'] + [f"{col}_pico" for col in pico.columns if col != 'Time']
thick.columns = ['Time'] + [f"{col}_thick" for col in thick.columns if col != 'Time']

# merge complet des données
merged = pd.merge(mod1_mean, mod2_mean, how='outer', on='Time')
merged = pd.merge(merged, pod200085, how='outer', on='Time')
merged = pd.merge(merged, pod200086, how='outer', on='Time')
merged = pd.merge(merged, pod200088, how='outer', on='Time')
merged = pd.merge(merged, pico, how='outer', on='Time')
merged = pd.merge(merged, thick, how='outer', on='Time')
merged = pd.merge(merged, thin, how='outer', on='Time')

# affichage de la taille du dataframe final
print(merged.shape)


if not os.path.exists(outPath):
    os.makedirs(outPath)

# export du fichier csv final
merged.to_csv(outPath + "\\merged.csv", index=False)
