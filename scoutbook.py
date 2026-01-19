#!/usr/bin/env python3

import pandas as pd
import csv
import numpy as np
import argparse
from pandas import Series, DataFrame

class Advancement:
    file_headers=["BSA Member ID","First Name","Middle Name","Last Name","Advancement Type","Advancement","Version",
                  "Date Completed","Approved","Awarded","MarkedCompletedBy","MarkedCompletedDate","CounselorApprovedBy",
                  "CounselorApprovedDate","LeaderApprovedBy","LeaderApprovedDate","AwardedBy","AwardedDate", "Unk", "Unk2"]    

    ScoutRanks = { 'Scout' : 1, 'Tenderfoot' : 2, 'Second Class' : 3, 'First Class' : 4, 'Star Scout': 5, 'Life Scout': 6, 'Eagle Scout': 7 }

    EagleReqMB = [ "First Aid", "Citizenship in the Community", "Citizenship in the Nation", "Citizenship in Society",
                   "Citizenship in the World", "Communication", "Cooking", "Personal Fitness", "Emergency Preparedness", "Lifesaving",
                   "Environmental Science", "Sustainability", "Personal Management", "Hiking", "Swimming", "Cycling",
                   "Camping", "Family Life" ]
    
    def __init__( self ):
        self.df = DataFrame()

    def get_rank_order(self, advancement):
        return self.ScoutRanks[advancement]
        
    def load_file (self, filename):
        """ Load an advancement export file in """
        
        df = pd.read_csv(filename, skiprows=1, names=self.file_headers)

        print("Reading from {}".format(filename))
        print(df.head())
        print(df.describe())

        self.df = pd.concat([self.df, df])

        self.rank = self.df[["BSA Member ID","First Name","Middle Name","Last Name","Advancement","Approved",
                             "Awarded","Date Completed","LeaderApprovedBy","LeaderApprovedDate"]][self.df["Advancement"].isin(self.ScoutRanks)]

        self.mb = self.df[["BSA Member ID","First Name","Middle Name","Last Name","Advancement Type", "Advancement","Approved",
                           "Awarded","Date Completed","LeaderApprovedBy","LeaderApprovedDate"]][self.df["Advancement Type"] == "Merit Badge"]

        self.award = self.df[["BSA Member ID","First Name","Middle Name","Last Name","Advancement Type", "Advancement","Approved",
                           "Awarded","Date Completed","LeaderApprovedBy","LeaderApprovedDate"]][self.df["Advancement Type"] == "Award"]

    def load_fixups(self, filename):
        """ load a csv file with the format (bsa id#, first name, last name) that contains name changes """

        self.fixups = {}

        with open(filename, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if len(row) == 3:
                    self.fixups[int(row[0])] = { "First Name": row[1], "Last Name": row[2] }



    def load_roster(self, filename):
        """ read in the troop roster """

        self.roster = {}

        self.rosterTuples = set()

        with open(filename, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if len(row) > 3 and len(row[2]) > 0:
                    self.rosterTuples.add((row[1],row[2]))
                    if row[2] in self.roster:
                        self.roster[row[2]].append( row[1] )
                    else:
                        self.roster[row[2]] = [ row[1] ]


    def generate_coh (self, outputfile):
        """ generate a coh spreadsheet """

        rank = self.rank[self.rank.Awarded != 1]
        indices_to_delete = []

        for idx, row in rank.iterrows():
            id = row['BSA Member ID']
            if id in self.fixups:  
                rank.at[idx, "First Name"] = self.fixups[id]['First Name']
                rank.at[idx, "Last Name"] = self.fixups[id]['Last Name']

            if row["Last Name"] in self.roster:
                for fn in self.roster[row["Last Name"]]:
                    if fn == row["First Name"]:
                        found = 1

            if found == 0:
                print("Dropping: ", row["First Name"], row["Last Name"])
                indices_to_delete.append(idx)

        rank = rank.drop(indices_to_delete)
        sorted_rank = rank.copy()
        sorted_rank['rank_order'] = rank['Advancement'].apply(self.get_rank_order)
        sorted_rank = sorted_rank.sort_values(by='rank_order')
        sorted_rank = sorted_rank.drop(columns=['rank_order'])
    
        mb = self.mb[self.mb.Awarded != 1]
        indices_to_delete = []

        for idx, row in mb.iterrows():
            id = row['BSA Member ID']
            if id in self.fixups:  
                mb.at[idx, "First Name"] = self.fixups[id]['First Name']
                mb.at[idx, "Last Name"] = self.fixups[id]['Last Name']

            if row["Last Name"] in self.roster:
                for fn in self.roster[row["Last Name"]]:
                    if fn == row["First Name"]:
                        found = 1

            if found == 0:
                print("Dropping: ", row["First Name"], row["Last Name"])
                indices_to_delete.append(idx)

        mb = mb.drop(indices_to_delete)
        sorted_mb = mb.copy()
        sorted_mb = sorted_mb.sort_values(by='Advancement')

        award = self.award[self.award.Awarded != 1]
        indices_to_delete = []

        for idx, row in award.iterrows():
            id = row['BSA Member ID']
            if id in self.fixups:  
                award.at[idx, "First Name"] = self.fixups[id]['First Name']
                award.at[idx, "Last Name"] = self.fixups[id]['Last Name']

            if row["Last Name"] in self.roster:
                for fn in self.roster[row["Last Name"]]:
                    if fn == row["First Name"]:
                        found = 1

            if found == 0:
                print("Dropping: ", row["First Name"], row["Last Name"])
                indices_to_delete.append(idx)

        award = award.drop(indices_to_delete)

        with pd.ExcelWriter(outputfile) as writer:
            sorted_rank.to_excel(writer, sheet_name="Rank", index=False, columns=["First Name","Last Name","Advancement",
                                                                          "Date Completed","LeaderApprovedBy","LeaderApprovedDate"])
            sorted_mb.to_excel(writer, sheet_name="Merit Badges", index=False, columns=["First Name","Last Name","Advancement Type", "Advancement",
                                                                          "Date Completed","LeaderApprovedBy","LeaderApprovedDate"])
            award.to_excel(writer, sheet_name="Awards", index=False, columns=["First Name","Last Name","Advancement Type", "Advancement",
                                                                          "Date Completed","LeaderApprovedBy","LeaderApprovedDate"])



        #with pd.ExcelWriter(outputfile) as writer:
        #    self.rank[self.rank.Awarded != 1].to_excel(writer, sheet_name="Rank", index=False, columns=["First Name","Last Name","Advancement",
        #                                                                                      "Date Completed","LeaderApprovedBy","LeaderApprovedDate"])
        #    self.mb[self.mb.Awarded != 1].to_excel(writer, sheet_name="Merit Badges", index=False, columns=["First Name","Last Name","Advancement Type", "Advancement",
        #                                                                                          "Date Completed","LeaderApprovedBy","LeaderApprovedDate"])
        #    self.award[self.award.Awarded != 1].to_excel(writer, sheet_name="Awards", index=False, columns=["First Name","Last Name","Advancement Type", "Advancement",
        #                                                                                          "Date Completed","LeaderApprovedBy","LeaderApprovedDate"])

    def generate_adv (self, outputfile):

        columns = ["BSA Member ID", "First Name", "Last Name"]
        columns.extend(self.ScoutRanks.keys())
        columns.extend(self.EagleReqMB)
        
        df = DataFrame(columns=columns)
        df = df.set_index("BSA Member ID", drop=True)

        print (df.describe)

        ids = set(self.df["BSA Member ID"].to_list())
        results = []

        advTuples = set() 

        for id in ids:
            found = 0
            d = {}
            ranks = self.rank[(self.rank["BSA Member ID"] == id) & (self.rank["Approved"] == 1)]["Advancement"].to_list()
            for rank in ranks:
                d[rank] = "y"

            mbs = self.mb[(self.mb["BSA Member ID"] == id) & (self.mb["Approved"] == 1)]["Advancement"].to_list()
            for mb in mbs:
                if mb in self.EagleReqMB:
                    d[mb] = "y"

            d["BSA Member ID"] = id
            if id in self.fixups:
                d["First Name"] = self.fixups[id]['First Name']
                d["Last Name"] = self.fixups[id]['Last Name']
            else:
                d["First Name"] = self.df[self.df["BSA Member ID"] == id]["First Name"].iloc[0]
                d["Last Name"] = self.df[self.df["BSA Member ID"] == id]["Last Name"].iloc[0]
            
            # only write out people in the roster
            if d["Last Name"] in self.roster:
                for fn in self.roster[d["Last Name"]]:
                    if fn == d["First Name"]:
                        results.append(d)
                        advTuples.add((d["First Name"],d["Last Name"]))
                        found = 1

            if found == 0:
                print("Dropping: ", d["First Name"], d["Last Name"])

        # add in scouts in roster that haven't advanced
        diffTuples = self.rosterTuples - advTuples
        fakeBSAID = 0
        for ( fn, ln ) in diffTuples:
            d = { "BSA Member ID" : fakeBSAID, "First Name" : fn, "Last Name" : ln }
            results.append(d)
            
            print(f'Adding New Scouts: {d["First Name"]} {d["Last Name"]}')
            fakeBSAID += 1

        cdf = pd.concat([df, DataFrame(results)])
        
        with pd.ExcelWriter(outputfile) as writer:
            cdf.to_excel(writer, sheet_name="Advancement", index=False)


if __name__ == "__main__" :

    parser = argparse.ArgumentParser(description='Scoutbook Helper')
    parser.add_argument("--advancement", dest='advancement', nargs="+", required=True, help='Advancement record export csv from scoutbook')
    parser.add_argument("--fixups", dest='fixups', required=False, help="CSV file of name fixes.")
    parser.add_argument("--roster", dest='roster', required=False, help="CSV file of troop roster.")

    parser.add_argument("--coh", dest='coh', required=False, help='Generate a CoH spreadsheet and write to here (filename.xlsx)')
    parser.add_argument("--adv", dest='adv', required=False, help='Generate a Advancement Report spreadsheet and write to here (filename.xlsx)')
    args = parser.parse_args()

    print (args.advancement)

    adv = Advancement()

    for fn in args.advancement:
        adv.load_file(fn)

    if args.fixups:
        adv.load_fixups(args.fixups)
    
    if args.roster:
        adv.load_roster(args.roster)

    if args.coh:
        adv.generate_coh(args.coh)
    
    if args.adv:
        adv.generate_adv(args.adv)
        
