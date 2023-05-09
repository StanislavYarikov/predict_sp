import pandas as pd
import datetime as dt
from manage_db import get_crit_dict, get_crit_range, get_pers_dict, get_prop_dict, get_prop_option_dict, get_feats_list

class task_sp_facts:
    def __init__(self):
        self.filename = 'task_facts.xlsx'
        self.tasks = pd.DataFrame(columns=['task_uid', 'description', 'added_dt'])
        self.crit_facts = pd.DataFrame(columns=['task_uid', 'pers_uid', 'crit_uid', 'crit_val', 'added_dt'])
        self.prop_facts = pd.DataFrame(columns=['task_uid', 'prop_uid', 'opt_uid', 'added_dt'])
        self.performers = pd.DataFrame(columns=['task_uid', 'pers_uid', 'status', 'added_dt'])
        self.target_facts = pd.DataFrame(columns=['task_uid', 'target_val', 'added_dt'])
        self.read()
        
    def read(self):
        try:
            self.tasks = pd.read_excel(self.filename, 'tasks')
            self.crit_facts = pd.read_excel(self.filename, 'task_critaria')
            self.prop_facts = pd.read_excel(self.filename, 'task_properties')
            self.performers = pd.read_excel(self.filename, 'performers')
            self.target_facts = pd.read_excel(self.filename, 'task_target')
        except:
            self.save()
            
    def save(self):
        with pd.ExcelWriter(self.filename) as writer:
            self.tasks.to_excel(writer, sheet_name='tasks', index=False)
            self.crit_facts.to_excel(writer, sheet_name='task_critaria', index=False)
            self.prop_facts.to_excel(writer, sheet_name='task_properties', index=False)
            self.performers.to_excel(writer, sheet_name='performers', index=False)
            self.target_facts.to_excel(writer, sheet_name='task_target', index=False)
            
    def add_task(self, task_uid, desc):
        if task_uid in self.tasks["task_uid"].tolist():
            print(f'Задача {task_uid} уже в базе')
            return None
        self.tasks = self.tasks.append({'task_uid': task_uid, 'description': desc, 'added_dt': dt.datetime.now()}, ignore_index=True)
        self.save()
        return task_uid
        
    def add_task_crit(self, task_uid, pers_name, crit_name, crit_val):
        crit_dict = get_crit_dict()
        pers_dict = get_pers_dict()
        if task_uid not in self.tasks["task_uid"].tolist():
            print(f'В базе нет задачи {task_uid}')
            return None
        if pers_name not in pers_dict:
            print(f'В базе нет специалиста {pers_name}')
            return None
        if crit_name not in crit_dict:
            print(f'В базе нет критерия {crit_name}')
            return None
        if crit_val not in [i+1 for i in range(get_crit_range())]:
            print(f'Значение критерия {crit_val} за пределами диапазона')
            return None
        self.crit_facts = self.crit_facts.append({'task_uid':task_uid, 'pers_uid': pers_dict[pers_name], 'crit_uid': crit_dict[crit_name], 'crit_val': crit_val, 'added_dt': dt.datetime.now()}, ignore_index=True)
        self.save()

    def add_task_prop(self, task_uid, prop_name, opt_name):
        if task_uid not in self.tasks["task_uid"].tolist():
            print(f'В базе нет задачи {task_uid}')
            return None
        prop_dict = get_prop_dict()
        if prop_name not in prop_dict:
            print(f'В базе нет свойства {prop_name}')
            return None
        opt_dict = get_prop_option_dict(prop_dict[prop_name])
        if opt_name not in opt_dict:
            print(f'В базе нет варианта {opt_name} свойства {prop_name}')
            return None
        self.prop_facts = self.prop_facts.append({'task_uid':task_uid, 'prop_uid': prop_dict[prop_name], 'opt_uid': opt_dict[opt_name], 'added_dt': dt.datetime.now()}, ignore_index=True)
        self.save()

    def add_task_target(self, task_uid, target_val):
        if task_uid not in self.tasks["task_uid"].tolist():
            print(f'В базе нет задачи {task_uid}')
            return None
        self.target_facts = self.target_facts.append({'task_uid':task_uid, 'target_val': target_val, 'added_dt': dt.datetime.now()}, ignore_index=True)
        self.save()

    def add_performer(self, task_uid, pers_name, perform_status):
        if task_uid not in self.tasks["task_uid"].tolist():
            print(f'В базе нет задачи {task_uid}')
            return None
        pers_dict = get_pers_dict()
        if pers_name not in pers_dict:
            print(f'В базе нет специалиста {pers_name}')
            return None
        if perform_status not in [0,1]:
            print(f'Статус {task_uid} должен быть 0 или 1')
            return None
        self.performers = self.performers.append({'task_uid':task_uid, 'pers_uid': pers_dict[pers_name], 'status': perform_status, 'added_dt': dt.datetime.now()}, ignore_index=True)
        self.save()

    def dataset(self):
        pers_dict = get_pers_dict()
        dataset_df = pd.DataFrame(columns=get_feats_list()+list(pers_dict.values()))
        for i_row in self.crit_facts.index:
            dataset_df.loc[self.crit_facts.loc[i_row, 'task_uid'], "_".join([self.crit_facts.loc[i_row, 'pers_uid'], self.crit_facts.loc[i_row, 'crit_uid'], str(self.crit_facts.loc[i_row, 'crit_val'])])] = 1
        for i_row in self.prop_facts.index:
            dataset_df.loc[self.prop_facts.loc[i_row, 'task_uid'], "_".join([self.prop_facts.loc[i_row, 'prop_uid'], self.prop_facts.loc[i_row, 'opt_uid']])] = 1
        for i_row in self.performers.index:
            dataset_df.loc[self.performers.loc[i_row, 'task_uid'], self.performers.loc[i_row, 'pers_uid']] = self.performers.loc[i_row, 'status']
        tasks_df = self.tasks[['task_uid', 'description']].drop_duplicates(keep='last').set_index('task_uid')
        for i_task in self.tasks['task_uid'].unique():
            for i_pers in pers_dict:
                dataset_df.loc[i_task, pers_dict[i_pers]+"_days"] = self.get_days_after_last_crit(i_task, i_pers)
        target_df = self.target_facts[['task_uid', 'target_val']].drop_duplicates(keep='last').set_index('task_uid')
        #print(tasks_df.merge(target_df, how='left').fillna(0))
        dataset_df = dataset_df.fillna(0).join(target_df, how='left')
        return dataset_df
    
    def get_days_after_last_crit(self, task_uid, pers_name):
        pers_dict = get_pers_dict()
        dates_Seria = self.crit_facts.loc[(self.crit_facts['task_uid']==task_uid)&(self.crit_facts['pers_uid']==pers_dict[pers_name]), 'added_dt']
        if len(dates_Seria) > 0:
            max_dt = dates_Seria.max()
        else:
            max_dt = self.tasks.loc[self.tasks['task_uid']==task_uid, 'added_dt'].max()
        return (dt.datetime.now() - max_dt)/dt.timedelta(days=1)

def test_filling():
    TaskSPfacts = task_sp_facts()
    TaskSPfacts.add_task('TP-001', 'Тестовая задача 1')
    TaskSPfacts.add_task('TP-002', 'Тест. задача 2')
    TaskSPfacts.add_task('TP-033', 'Тест. задача без оценки')
    TaskSPfacts.add_task_crit('TP-001', 'Name1', 'skill', 3)
    TaskSPfacts.add_task_crit('TP-001', 'Name2', 'skill', 3)
    TaskSPfacts.add_task_crit('TP-001', 'Name2', 'cases', 1)
    TaskSPfacts.add_task_prop('TP-001', 'инструмент', 'instr1')
    TaskSPfacts.add_task_prop('TP-002', 'инструмент', 'instr2')
    TaskSPfacts.add_task_target('TP-001', 13)
    TaskSPfacts.add_task_target('TP-002', 10.5)
    TaskSPfacts.add_performer('TP-001', 'Name2', 1)
    TaskSPfacts.add_performer('TP-001', 'Name1', 1)
    TaskSPfacts.add_performer('TP-002', 'Name1', 1)
    TaskSPfacts.add_performer('TP-002', 'Name1', 0)
    TaskSPfacts.add_performer('TP-002', 'Name2', 1)
    TaskSPfacts.add_task_crit('TP-033', 'Name1', 'skill', 1)
    TaskSPfacts.add_task_crit('TP-033', 'Name2', 'skill', 2)
    TaskSPfacts.add_task_crit('TP-033', 'Name1', 'cases', 5)
    TaskSPfacts.add_task_crit('TP-033', 'Name2', 'cases', 1)
    TaskSPfacts.add_performer('TP-033', 'Name2', 1)
    TaskSPfacts.add_task_prop('TP-033', 'инструмент', 'instr1')
    #print(TaskSPfacts.dataset())

#test_filling()

def get_train_test():
    TaskSPfacts = task_sp_facts()
    dataset_df = TaskSPfacts.dataset()
    feats_X = dataset_df.columns.tolist()
    feats_X.remove('target_val')
    train_X = dataset_df.loc[~dataset_df['target_val'].isna(), feats_X]
    train_y = dataset_df.loc[~dataset_df['target_val'].isna(), 'target_val']
    pred_X = dataset_df.loc[dataset_df['target_val'].isna(), feats_X]
    pred_y = dataset_df.loc[dataset_df['target_val'].isna(), 'target_val']
    return train_X, train_y, pred_X, pred_y

#print(get_train_test())