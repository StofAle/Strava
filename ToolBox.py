"""

version: 0.5
date: 05/19/2020
author: Alexander Stoffers

info:

class methods:
- update
-
-


"""

# load modules
import numpy as np
import pandas as pd
import json
import os
from sklearn.neighbors import LocalOutlierFactor

class Strava_ToolBox():
    """
    ???update description

    ToDo:
    make unit time and cutoffs accessible from the outside
    """

    def __init__(self):
        self.raw_data = {}  # container for data extracted from Strava API
        self.clean_data = {}  # container for cleaned data
        self.data = pd.DataFrame(data=[])  # container for aggregated, processed data

        # default variables for LocalOutlierFactor analysis, see function
        # LOF_velocity_results
        self.neighbors = 20
        self.write_to_clean_data = True  # flag whether clean data is stored in object

        # default variables for velocity calculation, see function 'get_velocities'
        self.unit_time = 10
        self.cutoff_beginning = 120
        self.cutoff_end = 60

        # default variables for data analysis, see function get_acticity_stats
        self.use_outlier_filtering = True

    @staticmethod
    def get_activities(client, path: str, limit: int = 1000) -> None:
        """ get and save running data from strava API to json files

        :param client:
        :type client:
        :return: None
        :rtype: None

        """
        # get list of already saved files
        files = list(os.listdir(path))

        activities = client.get_activities(limit=limit)
        for activity in activities:
            # check if activity data is already stored
            filename = str(activity.id) + '.json'

            if filename not in files:
                print('save file', filename)
                # get activity meta data
                infos = activity.to_dict()
                infos.pop('map')  # remove map details from dictionary

                # get activity data for times and distances
                stream_time = client.get_activity_streams(activity_id=activity.id,
                                                          types='Run', series_type='time')
                stream_distance = client.get_activity_streams(activity_id=activity.id,
                                                              types='Run',
                                                              series_type='distance')

                # save data if data for times and distances is available for activity ID
                if stream_time and stream_distance:
                    times = stream_time['time'].data
                    distances = stream_distance['distance'].data
                    dict_ = {'times': times, 'distances': distances, 'infos': infos}

                    # save data
                    with open(filename + '.json', 'w') as fp:
                        json.dump(dict_, fp)

    def save_clean_data(self, path: str) -> None:
        """
        """
        for key in self.clean_data.keys():
            filename = str(key) + '.json'
            data = self.clean_data[key]
            with open(path + filename, "w") as wf:
                json.dump(data, wf)

        return None

    def load_files(self, path: str, workout_type: str = 'Run') -> None:
        """
        ???update description
        """

        if self.raw_data and self.clean_data:
            print('raw data and clean data already loaded')
            return None

        if os.path.isdir('.'):
            print('loading files from directory')
            os.chdir(path)
            files = os.listdir('.')
            if not files:
                print('no files found')
                return None
        else:
            print('please enter valid directory path')

        for file in files:
            with open(path + file) as f:
                activity_id = int(file.split('.')[0])
                data = json.load(fp=f)

                if data['infos']['type'] == workout_type:
                    data_type = Strava_ToolBox.get_data_type_from_file(data)
                    if data_type == 'raw_data':
                        self.raw_data[activity_id] = data
                    elif data_type == 'clean_data':
                        self.clean_data[activity_id] = data

        return None

    def get_data_type_from_file(data: dict) -> str:
        """
        """
        try:
            if data['infos']['data_type']:
                return data['infos']['data_type']
        except:
            pass

        try:
            if data['infos']:
                return 'raw_data'
        except:
            return ''

    def get_velocities(self, times: list, distances: list) -> [float, float, float]:
        """
        update description
        """
        velocities = []
        velocity_times = []
        velocity_distances = []

        times_iter = iter(times)
        while True:

            try:
                start_time = next(times_iter)

                if self.cutoff_beginning < start_time < times[-1] - self.cutoff_end:
                    time = start_time
                    sum_velocity = 0
                    sum_time = 0
                    sum_distance = 0

                    j = 0
                    while time < start_time + self.unit_time and time + self.unit_time <= times[-1]:
                        delta_distance = distances[j + 1] - distances[j]
                        delta_time = times[j + 1] - times[j]
                        velocity = delta_distance / delta_time
                        sum_velocity = sum_velocity + velocity
                        sum_time = sum_time + time
                        sum_distance = sum_distance + distances[j]
                        j = j + 1
                        time = times[j]

                    if sum_time > 0:
                        avg_velocity = sum_velocity / float(j)
                        avg_time = sum_time / float(j)
                        avg_distance = sum_distance / float(j)
                        velocities.append(avg_velocity)
                        velocity_times.append(avg_time)
                        velocity_distances.append(avg_distance)

            except StopIteration:
                break

        return velocities, velocity_times, velocity_distances

    def get_activity_stats(self, activity_id: int) -> dict:
        """
        ???update description
        """

        dict_ = {}

        if self.use_outlier_filtering:
            df = self.get_clean_data(activity_id)
            df = df[df['outlier_flg'] == 1]
            times = df['time'].values
            distances = df['distances'].values

        else:
            times = self.raw_data[activity_id]['times']
            distances = self.raw_data[activity_id]['distances']

        velocities, velocity_times, velocity_distances = self.get_velocities(
            times=times, distances=distances)

        dict_['avg_velocity'] = np.average(velocities)
        dict_['std_velocity'] = np.std(velocities, axis=0)
        dict_['total_duration'] = velocity_times[-1]
        dict_['total_distance'] = velocity_distances[-1]
        dict_['start_date_local'] = self.raw_data[activity_id]['infos']['start_date_local']

        return dict_

    def process_raw_data(self) -> None:
        """
        ???update description
        """

        if not self.data.empty:
            print('raw data already processed')
            return None

        activity_ids = list(self.raw_data.keys())
        columns = list(self.get_activity_stats(activity_ids[0]).keys())
        df = pd.DataFrame(columns=columns)

        for cnt, activity_id in enumerate(activity_ids):
            print('processing data for activity ' + str(cnt) + ' out of ' +
                  str(len(activity_ids)))
            dict_ = self.get_activity_stats(activity_id)
            df_tmp = pd.DataFrame(data=[list(dict_.values())], index=[activity_id],
                                  columns=columns)

            df = df.append(df_tmp)

        self.data = df

        return None

    @staticmethod
    def instantaneous_velocity(distances: list, times: list):
        """
        """

        distances_iter = iter(distances)
        times_iter = iter(times)

        time_ante = 0
        distance_ante = 0

        while True:
            try:
                time_post = next(times_iter)
                delta_time = time_post - time_ante

                distance_post = next(distances_iter)
                delta_distance = distance_post - distance_ante

                time_ante = time_post
                distance_ante = distance_post
                if delta_time > 0:
                    inst_velocity = delta_distance / float(delta_time)
                    yield inst_velocity, time_ante

            except StopIteration:
                break

    def get_instantaneous_velocities(self, activity_id: int) -> np.ndarray:
        """
        """

        distances = self.raw_data[activity_id]['distances']
        times = self.raw_data[activity_id]['times']

        inst_velocities = np.ndarray(shape=(0, 2))
        for v, t in Strava_ToolBox.instantaneous_velocity(distances, times):
            vals = [[t, v]]
            inst_velocities = np.append(arr=inst_velocities, values=vals, axis=0)

        return inst_velocities

    def get_clean_data(self, activity_id: int) -> pd.DataFrame:
        """
        """

        LOF = LocalOutlierFactor(n_neighbors=self.neighbors)
        X = self.get_instantaneous_velocities(activity_id)
        y_pred = LOF.fit_predict(X)
        X_scores = LOF.negative_outlier_factor_

        df = pd.DataFrame({'time': X[:, 0], 'outlier_flg': y_pred
                              , 'LOF_score': X_scores})

        df_raw = pd.DataFrame({'time': self.raw_data[activity_id]['times'],
                               'distances': self.raw_data[activity_id]['distances']})

        df = df.merge(df_raw, on='time')

        if self.write_to_clean_data == True:
            self.clean_data[activity_id] = df.to_dict()
            self.clean_data[activity_id]['infos'] = self.raw_data[activity_id]['infos']
            self.clean_data[activity_id]['infos']['data_type'] = 'clean_data'

        return df
