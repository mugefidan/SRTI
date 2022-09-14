# Writing to an excel  
# sheet using Python 
import xlwt 
from xlwt import Workbook 
import re

agent_size = [20,40,60,80,100]
percent=[25,50,75,100]


def average(list1):
    summ = []
    if len(list1)>0:
        for i in range(len(list1)):
            list1[i] = [float(x) for x in list1[i].split(",")]
            summ += list1[i]
        summation = sum(map(float,summ))
        average = summation/len(list1)
    else:
        average=0
    return average

def appendTime(filename,models,cpu_time):
    time=[]
    num= []
    unsatis_time=[]
    for i in range(len(models)):
        models[i] = cpu_time[i].split(":")[0][-2:]
        if int(models[i]) < 21 and cpu_time[i].split(",")[0][-1] != "0":
            time.append(cpu_time[i].split(",")[1][15:21])
            num.append(cpu_time[i].split(",")[0][-1])
        elif int(models[i]) < 21 and cpu_time[i].split(",")[0][-1] == "0":
            unsatis_time.append(cpu_time[i].split(",")[1][15:21])
    return str(len(num)),average(time),average(unsatis_time)

# Workbook is created 
wb = Workbook() 
  
# add_sheet is used to create sheet. 
sheet1 = wb.add_sheet('Sheet 1') 
  
sheet1.write(0, 0, 'Copmleteness Degree') 
sheet1.write(0, 1,'Input size') 
sheet1.write(0, 2,'Number of solution') 
sheet1.write(0, 3, 'CPU Time (exist)') 
sheet1.write(0, 4,'CPU Time (no solution)')

i=1
for agent in agent_size:
    k=0
    for percentage in percent:
        fileprefix = "output-srti-{}-{}new".format(agent,percentage)
        inputfilename = fileprefix + ".txt"
        models = []
        cpu_time = []
        linenum = 0
        model = re.compile("Instance", re.IGNORECASE)  # Compile a case-insensitive regex
        time = re.compile("CPU Time", re.IGNORECASE)
# Open the input file
        with open (inputfilename, 'rt') as myfile:
            for line in myfile:
                if model.search(line) != None:
                    linenum += 1      # If a match is found
                    models.append((linenum))
                if time.search(line) != None:
                    cpu_time.append((line.rstrip()))
        sheet1.write(7*k+i,1,agent)
        sheet1.write(7*k+i,0,percentage)
        sheet1.write(7*k+i,2,str(appendTime(inputfilename,models,cpu_time)[0]))
        sheet1.write(7*k+i,3,format(appendTime(inputfilename,models,cpu_time)[1],".3f"))
        sheet1.write(7*k+i,4,format(appendTime(inputfilename,models,cpu_time)[2],".3f"))
        k+=1
    i+=1
wb.save('arg.xls') 


