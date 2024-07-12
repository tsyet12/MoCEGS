from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import subprocess
import sys
import zipfile
import os
import glob

environmental_impacts = [0,1,100,10000,1000000,100000000,10000000000]

start_time=datetime.now()
foldermaster="./Pareto"
# interval=relativedelta(months=1)

env_original="environmental_impact_cost_factor = 1"
path=os.path.dirname(os.path.abspath(__file__))
os.chdir(path)
caselist=[[False,False,False],[True,False,False],[True,True,False],[True,True,True]]
c1="apply_border_penalty = True"
c2= "use_margin_upper_bound = True"
c3= "weigh_margin_with_population = True"

for _c in range(len(caselist)):
    for envin in environmental_impacts:
        folder=foldermaster+str(_c+1)+"//"
        case=caselist[_c]
        env_replace = f"\n\nenvironmental_impact_cost_factor = {envin}"
        c1r= f"apply_border_penalty = {case[0]}"
        c2r= f"use_margin_upper_bound = {case[1]}"
        c3r= f"weigh_margin_with_population = {case[2]}"
        print(f"\n\nEnvironmental factor: {envin}")
        with open('energy_pgraph_10_optimize.py', 'r') as original:
            filecontent = original.read()
        with open('energy_pgraph_10_optimize_temp.py', 'w') as modified:
            fc=filecontent.replace(env_original,env_replace)
            fc=fc.replace(c1,c1r).replace(c2,c2r).replace(c3,c3r)
            modified.write(fc)

        with open('energy_pgraph_10_plot.py', 'r') as original:
            filecontent1 = original.read()
        with open('energy_pgraph_10_plot_temp.py', 'w') as modified:
            fc1=filecontent1.replace(c1,c1r)
            modified.write(fc1)

        
        print("Optimize")
        process_opt = subprocess.Popen(["python", "energy_pgraph_10_optimize_temp.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # process_opt.wait()
        # stdout = process_opt.communicate()[0]
        # print (stdout)
        while True:
            output = process_opt.stdout.readline()
            if process_opt.poll() is not None:
                break
            # if output:
                # print (output.strip())
        rc = process_opt.poll()
        new_graph_count = len([f for f in os.listdir("P-graphs") if datetime.fromtimestamp(os.path.getmtime("P-graphs\\"+f)) >= start_time])
        if new_graph_count < 17520:
            print('''
    *****************************
    *      OPTIMIZER ERROR      *
    *****************************
    ''')
        
        print("Plot")
        process_plot = subprocess.Popen(["python", "energy_pgraph_10_plot.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # process_plot.wait()
        while True:
            output = process_plot.stdout.readline()
            if process_plot.poll() is not None:
                break
            # if output:
            #     print (output.strip())
        rc = process_plot.poll()
        if not os.path.isfile("Figures6-7\\FigureMargin.png"):
            print('''
    *****************************
    *         PLOT ERROR        *
    *****************************
    ''')
        
        print("Zip")
        cost_impact_file = folder+f"cost_impact_2022_penalty_env{envin}.zip"
        if os.path.exists(cost_impact_file):
            os.remove(cost_impact_file)
        reszip = zipfile.ZipFile(cost_impact_file, "w")
        reszip.write("cost_impact_sum.txt")
        reszip.write("total_cost_pickle.txt")
        reszip.write("total_environmental_impact_pickle.txt")
        reszip.close()
        
        import_export_file = folder+f"import_export_capacity_2022_env{envin}.zip"
        if os.path.exists(import_export_file):
            os.remove(import_export_file)
        reszip2 = zipfile.ZipFile(import_export_file, "w")
        for file in glob.glob('capacityOptimized/*'):
            reszip2.write(file)
        for file in glob.glob('exportOptimized/*'):
            reszip2.write(file)
        for file in glob.glob('importOptimized/*'):
            reszip2.write(file)
        reszip2.close()
        
        figures_file = folder+f"figures_env{envin}.zip"
        if os.path.exists(figures_file):
            os.remove(figures_file)
        reszip3 = zipfile.ZipFile(figures_file, "w")
        for file in glob.glob(folder+'Figures6-7/*'):
            reszip3.write(file)
        reszip3.close()
        
