import pandas as pd

class task_sp_db():
    def __init__(self, filepath):
        self.filepath = filepath
        self.persons = pd.read_excel(self.filepath, sheet_name='persons')
        self.crits = pd.read_excel(self.filepath, sheet_name='crits')
        self.props = pd.read_excel(self.filepath, sheet_name='props')
    
    def add_person(self, data):
        self.persons = self.persons.append(data, ignore_index=True)
    
    def add_crit(self, data):
        self.crits = self.crits.append(data, ignore_index=True)
    
    def add_prop(self, data):
        self.props = self.props.append(data, ignore_index=True)
    
    def commit_changes(self):
        with pd.ExcelWriter(self.filepath) as writer:  
            self.persons.to_excel(writer, sheet_name='persons', index=False)
            self.crits.to_excel(writer, sheet_name='crits', index=False)
            self.props.to_excel(writer, sheet_name='props', index=False)


# write python code creating class of excel database that read excel file and read pages "persons", "crits", "props" creates excel file if it not esists with functions for adding new elements in tables with generating uid in format "pers1" for table "pepsons", "crit1" for table "crits" and "prop1" for table "propss" and with autimatic committing changes

import pandas as pd
import datetime as dt
class task_sp_db:
    def __init__(self):
        self.filename = 'task_sp.xlsx'
        self.persons = pd.DataFrame(columns=['uid', 'name', 'description', 'added_dt'])
        self.crits = pd.DataFrame(columns=['uid', 'name', 'description', 'added_dt'])
        self.props = pd.DataFrame(columns=['uid', 'name', 'description', 'added_dt'])
        self.prop_opts = pd.DataFrame(columns=['prop_uid', 'uid','name', 'description', 'added_dt'])
        self.feats = pd.DataFrame(columns=['feat', 'added_dt'])
        self.ranges = 5
        self.read()
        
    def read(self):
        try:
            self.persons = pd.read_excel(self.filename, 'persons')
            self.crits = pd.read_excel(self.filename, 'critaria')
            self.props = pd.read_excel(self.filename, 'properties')
            self.prop_opts = pd.read_excel(self.filename, 'property_options')
            self.feats = pd.read_excel(self.filename, 'features')
        except:
            self.save()
            
    def save(self):
        with pd.ExcelWriter(self.filename) as writer:
            self.persons.to_excel(writer, sheet_name='persons', index=False)
            self.crits.to_excel(writer, sheet_name='critaria', index=False)
            self.props.to_excel(writer, sheet_name='properties', index=False)
            self.prop_opts.to_excel(writer, sheet_name='property_options', index=False)
            self.feats.to_excel(writer, sheet_name='features', index=False)
            
    def add_pers(self, name, desc):
        if name in self.persons["name"].tolist():
            print(f'Имя {name} уже в базе специалистов')
            return None
        uid = f'pers{len(self.persons) + 1}'
        self.persons = self.persons.append({'uid': uid, 'name': name, 'description': desc, 'added_dt': dt.datetime.now()}, ignore_index=True)
        self.generate_feats('pers', uid)
        self.save()
        return uid
        
    def add_crit(self, name, desc):
        if name in self.crits["name"].tolist():
            print(f'Название {name} уже в базе критериев')
            return None
        uid = f'crit{len(self.crits) + 1}'
        self.crits = self.crits.append({'uid': uid, 'name': name, 'description': desc, 'added_dt': dt.datetime.now()}, ignore_index=True)
        self.generate_feats('crit', uid)
        self.save()
        return uid
        
    def add_prop(self, name, desc):
        if name in self.props["name"].tolist():
            print(f'Название {name} уже в базе свойств')
            return None
        uid = f'prop{len(self.props) + 1}'
        self.props = self.props.append({'uid': uid, 'name': name, 'description': desc, 'added_dt': dt.datetime.now()}, ignore_index=True)
        self.save()
        return uid

    def add_prop_opt(self, prop_name, name, desc):
        if prop_name not in self.props["name"].tolist():
            print(f'Названия {prop_name} нет в базе свойств')
            return None
        prop_uid = self.props.loc[self.props['name']==prop_name]['uid'].iloc[0]
        prop_opts_df = self.prop_opts[self.prop_opts['prop_uid'] == prop_uid]
        if name in prop_opts_df["name"].tolist():
            print(f'Название {name} уже в базе вариантов свойства {prop_name}')
            return None
        uid = f'opt{len(prop_opts_df) + 1}'
        self.prop_opts = self.prop_opts.append({'prop_uid': prop_uid, 'uid': uid, 'name': name, 'description': desc, 'added_dt': dt.datetime.now()}, ignore_index=True)
        self.generate_feats('prop_opt', uid)
        self.save()
        return uid
    
    def generate_feats(self, type, uid):
        if type == 'prop_opt':
            prop_uid = self.prop_opts.loc[self.prop_opts['uid']==uid]['prop_uid'].iloc[0]
            self.feats = self.feats.append({'feat': prop_uid+"_"+uid, 'added_dt': dt.datetime.now()}, ignore_index=True)
        if type == 'pers':
            for i_crit in self.crits.uid:
                for i_range in [str(i+1) for i in range(self.ranges)]:
                    self.feats = self.feats.append({'feat': "_".join([uid, i_crit, i_range]), 'added_dt': dt.datetime.now()}, ignore_index=True)
        if type == 'crit':
            for i_pers in self.persons.uid:
                for i_range in [str(i+1) for i in range(self.ranges)]:
                    self.feats = self.feats.append({'feat': "_".join([i_pers, uid, i_range]), 'added_dt': dt.datetime.now()}, ignore_index=True)
    
def get_crit_dict():
    TaskSPDB = task_sp_db()
    return pd.Series(TaskSPDB.crits['uid'].values,index=TaskSPDB.crits['name']).to_dict()

def get_pers_dict():
    TaskSPDB = task_sp_db()
    return pd.Series(TaskSPDB.persons['uid'].values,index=TaskSPDB.persons['name']).to_dict()

def get_prop_dict():
    TaskSPDB = task_sp_db()
    return pd.Series(TaskSPDB.props['uid'].values,index=TaskSPDB.props['name']).to_dict()

def get_prop_option_dict(prop_uid):
    TaskSPDB = task_sp_db()
    prop_opt_df = TaskSPDB.prop_opts.loc[TaskSPDB.prop_opts['prop_uid']==prop_uid]
    return pd.Series(prop_opt_df['uid'].values,index=prop_opt_df['name']).to_dict()

def get_crit_range():
    TaskSPDB = task_sp_db()
    return TaskSPDB.ranges

def get_feats_list():
    TaskSPDB = task_sp_db()
    return TaskSPDB.feats['feat'].tolist()    

def test_filling():
    TaskSPDB = task_sp_db()
    TaskSPDB.add_pers('Name1', 'Full name 1')
    TaskSPDB.add_crit('volume', 'work volume')
    TaskSPDB.add_crit('skill', 'lack of skill')
    TaskSPDB.add_prop('instrument', 'instrument for perfomance')
    TaskSPDB.add_pers('Name2', 'Full name 2')
    TaskSPDB.add_crit('cases', 'lack of cases')
    TaskSPDB.add_prop_opt('instrument', 'instr1', 'work instrument 1')
    TaskSPDB.add_prop_opt('instrument', 'instr2', 'work instrument 2')

#test_filling()
#print(get_prop_dict())
#print(get_prop_option_dict('prop1'))
#
#
# print(get_feats_list())