import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# chemin vers le fichier CSV mergé generé à l'étape précédente
MERGED_FILE = '../out/merged.csv'

# chemin vers le fichier Excel contenant les activités
ACTIVITIES_FILE = '../resources/activites.xlsx'

# chemin de sortie pour le fichier CSV labelisé
OUT_FILE = '../out/data.csv'

def skip_rows(index,nth):
    """
    Fonction utilisée pour sauter des lignes lors de la lecture du fichier CSV
    utilisée pour du debugging, pour que le fichier soit plus petit et charge plus vite pour nos tests
    :param index: position de la ligne en cours de lecture
    :param nth: nombre de lignes à sauter
    :return: True si la ligne doit être sautée, False sinon
    """
    return index > 0 and (index % nth != 0)

def get_data(nth=1):
    """
    Fonction permettant de lire les données du fichier CSV créé à l'étape et de les retourner sous forme de DataFrame
    :param nth: nombre de lignes à sauter lors de la lecture du fichier
    :return: DataFrame contenant les données du fichier CSV
    """

    # on lit le fichier CSV en sautant certaines lignes si nécessaire
    data = pd.read_csv(MERGED_FILE, sep=',', skiprows=lambda x: skip_rows(x,nth))

    # on s'assure que la colonne Time est bien dans le bon format de date
    data['Time'] = pd.to_datetime(data['Time']).dt.tz_convert('UTC+01:00')

    return data


def get_activities():
    """
    Fonction permettant de lire le fichier Excel des activités et de les retourner sous forme de DataFrame
    :return: DataFrame contenant les activités du fichier Excel
    """

    # on lit le fichier Excel
    activities = pd.read_excel(ACTIVITIES_FILE, sheet_name="Done so far", usecols=['activity', 'Started', 'Ended'])

    # on supprime les lignes où les colonnes Started et Ended sont vides
    activities.dropna(subset=['Started', 'Ended'], inplace=True)

    # on s'assure que les colonnes Started et Ended sont bien dans le bon format de date
    activities['Started'] = pd.to_datetime(activities['Started']).dt.tz_localize('UTC').dt.tz_convert('UTC+01:00')
    activities['Ended'] = pd.to_datetime(activities['Ended']).dt.tz_localize('UTC').dt.tz_convert('UTC+01:00')

    return activities


def get_segmented_activities(activities, data):
    """
    Fonction permettant de segmenter les données en fonction des activités, par rapport aux dates de début et de fin
    :param activities: DataFrame contenant les activités
    :param data: DataFrame contenant les données
    :return: dictionnaire contenant les segments de données pour chaque activité
    """

    # on crée un dictionnaire vide pour stocker les segments de données
    activity_segments = {}

    # on parcourt les activités
    for act in activities['activity'].unique():
        # on initialise une liste vide pour stocker les segments de données pour cette activité
        # ainsi qu'une variable pour stocker la longueur totale des données
        activity_segments[act] = {'data': [], 'length': 0}

    # on parcourt les activités
    for idact, row in activities.iterrows():
        # on récupère les dates de début et de fin de l'activité, ainsi que le nom de l'activité
        start = row['Started']
        end = row['Ended']
        activity_name = row['activity']

        # on récupère le segment de données correspondant à l'activité
        segment = data[(data['Time'] >= start) & (data['Time'] <= end)].reset_index(drop=True).sort_values(by='Time').drop(columns='Time')

        # on ajoute le segment de données à la liste des segments de données pour cette activité
        activity_segments[activity_name]['data'].append(segment)

        # on met à jour la longueur totale des données pour cette activité
        activity_segments[activity_name]['length'] += len(segment)

    return activity_segments



def get_average_signature(activity_segments, target_length):
    """
    Fonction permettant de calculer la signature moyenne pour chaque activité
    :param activity_segments: dictionnaire contenant les segments de données pour chaque activité
    :param target_length: longueur cible pour la signature moyenne
    :return: dictionnaire contenant les signatures moyennes pour chaque activité
    """
    # Dictionnaire pour stocker les données normalisées
    activity_average_signatures = {}

    # on précise les indices pour la nouvelle longueur cible de la signature moyenne
    new_index = np.linspace(0, 1, target_length)

    # on parcourt les activités
    for activity, data in activity_segments.items():
        # Liste pour stocker les données interpolées
        resampled_data = []

        # on parcourt les segments de données pour cette activité
        for df in data['data']:
            interp_func = np.linspace(0, 1, df.shape[0])
            interpolated_arrays = []

            # Interpoler chaque colonne du DataFrame
            for col in df.columns:
                interp_series = np.interp(new_index, interp_func, df[col])
                interpolated_arrays.append(interp_series)

            # Créer un nouveau DataFrame avec les données interpolées
            interpolated_df = pd.DataFrame(np.column_stack(interpolated_arrays), index=new_index, columns=df.columns)
            resampled_data.append(interpolated_df)

        # On concatène les données interpolées et on calcule la moyenne
        mean_df = pd.concat(resampled_data).groupby(level=0).mean()
        activity_average_signatures[activity] = mean_df

    return activity_average_signatures




def plot_activity_data_in_one_figure(activity_average_signatures, target_length):
    """
    Fonction permettant d'afficher les signatures moyennes pour chaque activité sous forme de graphiques
    :param activity_average_signatures: dictionnaire contenant les signatures moyennes pour chaque activité
    :param target_length: longueur cible pour la signature moyenne
    """

    n_activities = len(activity_average_signatures)
    # on calcule le nombre de lignes et de colonnes pour les sous-graphiques en fonction du nombre d'activités
    n_rows = int(np.ceil(np.sqrt(n_activities)))  # Nombre de lignes pour les sous-graphiques
    n_cols = int(np.ceil(n_activities / n_rows))  # Nombre de colonnes pour les sous-graphiques

    # on crée une figure pour afficher les graphiques
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 10), squeeze=False)
    axes = axes.flatten()  # Aplatir les axes pour faciliter l'indexation

    # on ajoute un titre à la figure
    fig.suptitle('Average Signature for each activity, over '+str(target_length)+' samples', fontsize=16)

    # on parcourt les activités
    for ax, (activity, mean_df) in zip(axes, activity_average_signatures.items()):
        # on parcours chaque colonne (donnée d'un capteur) de la signature moyenne
        for column in mean_df.columns:
            # on affiche la courbe correspondante
            ax.plot(mean_df.index, mean_df[column], label=column)
        ax.set_title(f'{activity}')
        ax.set_xlabel('Samples')
        ax.set_ylabel('Sensor Values')
        ax.grid(True)

    # on supprime les axes inutilisés
    for i in range(len(activity_average_signatures), len(axes)):
        axes[i].axis('off')

    # on ajuste la disposition des graphiques
    plt.tight_layout()
    # on affiche la figure
    plt.show()


# on récupère les données des capteurs
data = get_data()

# on récupère les données des activités
activities = get_activities()

# on segmente les données en fonction des dates des activités
segmented = get_segmented_activities(activities, data)


# on calcule la signature moyenne pour chaque activité
target_length = 100
activity_average_signatures = get_average_signature(segmented, target_length)
# on affiche les signatures moyennes pour chaque activité sous forme de graphiques
plot_activity_data_in_one_figure(activity_average_signatures, target_length)

# on ajoute une colonne label au données en fonction de l'activité
all_data_frames = []
for activity_name, info in segmented.items():
    for df in info['data']:
        df['label'] = activity_name
        all_data_frames.append(df)

# on regroupe tous les segments dans un dataframe
final_df = pd.concat(all_data_frames)
final_df.reset_index(drop=True, inplace=True)

# on exporte ce nouveau dataframe
final_df.to_csv(OUT_FILE, index=False)

