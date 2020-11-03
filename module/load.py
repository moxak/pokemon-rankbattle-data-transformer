import json
import urllib.request
import datetime
from pathlib import Path
import os
import re
import csv
from tqdm import tqdm
import pandas as pd
from sklearn import preprocessing

class Data_loader:
    def __init__(self, download = True ,input_file_path = './/datachunk',output_file_path = './/output', output_rankbattle_file_path ='.//output//rankbattle_stats', resources_file_path = './/resources', lower_resources_file_path = './/resources//split'):
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.output_rankbattle_file_path = output_rankbattle_file_path
        self.resources_file_path = resources_file_path
        self.lower_resources_file_path = lower_resources_file_path
        for path in [self.output_file_path, self.output_rankbattle_file_path, self.resources_file_path, self.lower_resources_file_path]:
            self.check_dir(path)
        self.ids = self.load_json(file_path = f'{self.input_file_path}//IDs.json')
        self.pokedex = self.load_json(file_path = f'{input_file_path}//bundle.json')
        self.make_index_files()
        if download == True:
            print('Start downloading the file.')
            self.download_jsonchunk()
            self.merge_json()

    def check_dir(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)
            self.write_log(path, message='MakeDir  ')

    def write_log(self, file_name, message='Generated'):
        with open('log', 'a') as f:
            print(f'{datetime.datetime.now()} | {message}: {file_name}', file=f)

    @staticmethod
    def load_json(file_path):
        dict_ = "";
        with open(file_path, 'r', encoding='utf-8') as json_open:
            dict_ = json.load(json_open)
        return dict_

    @staticmethod
    def get_response(url, file_name, lower_resources_file_path):
        try:
            with urllib.request.urlopen(url) as response:
                body = json.loads(response.read())
                with open(f'{lower_resources_file_path}//{file_name}', 'w') as f:
                    json.dump(body, f, indent=4)
            return True
        except urllib.error.URLError as e:
            print(e.reason)
            return False

    def download_jsonchunk(self):
        print(f'{datetime.datetime.now()} | Download JSONs')
        for season_number in tqdm(self.ids['list'].keys()):
            for  season_id in self.ids['list'][season_number].keys():
                rst = self.ids['list'][season_number][season_id]['rst']
                ts2 = self.ids['list'][season_number][season_id]['ts2']
                for i in range(1,6,1):
                    url = f'https://resource.pokemon-home.com/battledata/ranking/{season_id}/{rst}/{ts2}/pdetail-{i}'
                    file_name = f'Season{season_number}_{"Single" if season_id[4]=="1" else "Double"}_{i}.json'
                    if self.get_response(url, file_name, self.lower_resources_file_path):
                        self.write_log(file_name=file_name)

    def merge_json(self):
        print(f'{datetime.datetime.now()} | Merge JSONs')
        for i in tqdm(self.ids['list'].keys()):
            for j in self.ids['list'][i].keys():
                rule = "Single" if j[4] == '1' else "Double"
                files = []
                for n in range(1,6,1):
                    with open(f'{self.lower_resources_file_path}//Season{i}_{rule}_{n}.json', 'r', encoding='utf-8') as json_open:
                        files.append(json.load(json_open))
                jsonMerged = {**files[0], **files[1], **files[2], **files[3], **files[4]}
                file_name = f'Season{i}_{rule}_merged.json'
                with open(f'{self.resources_file_path}//{file_name}', 'w') as f:
                    json.dump(jsonMerged, f, indent=4)
                    self.write_log(file_name=file_name)

    def make_index_files(self):
        new_dict = {}
        for n in self.pokedex['item'].keys():
            n = int(n)
            if n < 148:
                pass
            elif n < 260:
                id_ = n-143
                new_dict[id_] = self.pokedex['item'][str(n)]
            elif 264 < n:
                id_ = n-148
                new_dict[id_] = self.pokedex['item'][str(n)]

        pd.DataFrame(new_dict.values(), index=new_dict.keys(), columns=['item']).to_csv(f'{self.output_file_path}//helditem_index.csv')
        pd.DataFrame(self.pokedex['tokusei'].values(), index=self.pokedex['tokusei'].keys(), columns=['tokusei']).to_csv(f'{self.output_file_path}//ability_index.csv')
        pd.DataFrame(self.pokedex['waza'].values(), index=self.pokedex['waza'].keys(), columns = ['waza']).to_csv(f'{self.output_file_path}//move_index.csv')


class Data_transformer(Data_loader):
    def __init__(self, download=True):
        super().__init__(download=download)
        self.order_dicts = self.load_json(file_path=f"{self.input_file_path}//order.json")

        print(f'{datetime.datetime.now()} | Make CSVs')
        self.split(meta_value=True)
        for order_key in self.order_dicts:
            self.split(order_dict = self.order_dicts[order_key])

    @staticmethod
    def write_csv(text, file, mode):
        with open(file, mode, newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(text)

    @staticmethod
    def cal_crt(df, method='temoti'):
        if method == 'temoti':
            row_name = "流行指数"
        elif method == 'win':
            row_name = 'メタ指数'

        concated_df1 = df.groupby('B', as_index=False)['value'].mean()
        concated_df1.columns = ['Pokemon', 'RankAverage']

        concated_df2 = df.groupby('B', as_index=False)['value'].sum()
        concated_df2.columns = ['Pokemon', 'Top10Count']

        concat_df = pd.concat([concated_df1,concated_df2], axis = 1, join = 'inner')
        concat_df =pd.concat([concated_df1[concated_df1.columns[0]], \
                    concat_df.drop(concat_df.columns[2], axis =1)], axis = 1)

        concat_df['RankAverage_std'] = preprocessing.minmax_scale(concat_df['RankAverage'])
        concat_df['Top10Count_std'] = preprocessing.minmax_scale(concat_df['Top10Count'])

        concat_df['Crt'] = concat_df["RankAverage"] * concat_df["Top10Count"]
        concat_df[row_name] = concat_df['RankAverage_std'] * concat_df['Top10Count_std']
        df = concat_df.sort_values('Crt', ascending = False)
        return df.drop(['RankAverage', 'Top10Count', 'RankAverage_std', 'Top10Count_std', 'Crt'], axis=1)

    @staticmethod
    def get_name(num, p_detail_id, pokedex, method='pokemon'):
        if method == 'pokemon':
            name = ''
            if num == "876":
                if p_detail_id == "0":
                    name = "イエッサン♂"
                else:
                    name = "イエッサン♀"
            elif num == "479":
                if p_detail_id == "0":
                    name = "ロトム（デフォ）"
                elif p_detail_id == "1":
                    name = "ロトム（火）"
                elif p_detail_id == "2":
                    name = "ロトム（水）"
                elif p_detail_id == "3":
                    name = "ロトム（氷）"
                elif p_detail_id == "4":
                    name = "ロトム（飛行）"
                elif p_detail_id == "5":
                    name = "ロトム（草）"
            else:
                name = pokedex['poke'][int(num) -1]
        elif method == 'motimono':
            name = pokedex['item'][num]
        else:
            name = pokedex[method][num]
        return name

    @staticmethod
    def Change_Name(x):
        rename_dict = {
            'ニャオニクス': 'ニャオニクス♂',
            'ギルガルド': 'ギルガルド盾',
            'ヒヒダルマ': 'ヒヒダルマN',
            'バスラオ': 'バスラオ赤',
            'ルガルガン':'ルガルガン昼',
            'メテノ':'メテノ(流星)',
            'イエッサン': 'イエッサン♂'
            }
        for key in rename_dict.keys():
            if x[2] == key:
                x[2] = rename_dict[key]
        return x[2]

    def trans(self, pdetail, method1 = 'temoti', method2='pokemon', column =  ["A", "B", "value"]):
        t_names = []
        a_names = []
        ranks = []
        for pokenum in  list(pdetail.keys()):
            for p_detail_id in list(pdetail[pokenum].keys()):
                t_name = self.get_name(pokenum, p_detail_id, pokedex = self.pokedex,method='pokemon')
                for rank, component in enumerate(list(pdetail[pokenum][p_detail_id][method1][method2])):
                    a_name = self.get_name(component['id'], component[list(component.keys())[1]], pokedex = self.pokedex, method=method2)
                    t_names += [t_name]
                    a_names += [a_name]
                    ranks += [rank+1]
        self.trans_df = pd.DataFrame(
            data = {column[0]: t_names,column[1]: a_names,  column[2]: ranks},
            columns = column)

    def split(self, order_dict=False, meta_value=False):
        Seasons = []
        Rules = []
        if meta_value == True:
            df_master = pd.DataFrame(columns = ['Season', 'Rule', 'Pokemon','流行指数', 'メタ指数'])
            for rule in ['Single', 'Double']:
                for season_num in range(1,len(self.ids['list'].keys())+1,1):
                    for method in ['temoti', 'win']:
                        with open(f'{self.resources_file_path}//Season{season_num}_{rule}_merged.json', 'r', encoding='utf-8') as json_open:
                            data = json.load(json_open)
                        self.trans(data, method1=method)
                        if method == 'temoti':
                            df_fashion = self.cal_crt(self.trans_df, method=method)
                        elif method == 'win':
                            df_meta =  self.cal_crt(self.trans_df, method=method)

                    df = pd.merge(df_fashion, df_meta, on='Pokemon', how='outer').fillna(0)

                    df['Season'] = season_num
                    df['Rule'] = rule

                    df_master = pd.concat([df_master, df], axis = 0)

            df_master['Pokemon'] = df_master.apply(self.Change_Name, axis=1)
            file_name = f'ALL_SEASON_METAVALUES.csv'
            df_master.to_csv(f'{self.output_rankbattle_file_path}//{file_name}', index=False)
            self.write_log(file_name=file_name)
        else:
            for method in tqdm(order_dict['column'].keys()):
                df_master = pd.DataFrame(columns = ['Season', 'Rule', 'Pokemon', order_dict['column'][method], f'Rank_{order_dict["column"][method]}'])
                for rule in ['Single', 'Double']:
                    for season_num in range(1,len(self.ids['list'].keys()),1):
                        with open(f'{self.resources_file_path}//Season{season_num}_{rule}_merged.json', 'r', encoding='utf-8') as json_open:
                            data = json.load(json_open)
                        self.trans(data, method1 = order_dict['method1'],method2 = method, column = ['Pokemon', order_dict['column'][method], f'Rank_{order_dict["column"][method]}'])
                        self.trans_df['Season'] = season_num
                        self.trans_df['Rule'] = rule
                        df_master = pd.concat([df_master, self.trans_df], axis = 0)
                df_master['Pokemon'] = df_master.apply(self.Change_Name, axis=1)
                file_name = f'{order_dict["file_names"][method]}'
                df_master.to_csv(f'{self.output_rankbattle_file_path}//{file_name}', index=False)
                self.write_log(file_name=file_name)


