import re

percent = [25,50,75,100]
agent_size = [20,40,60,80,100]
for agent in agent_size:
    for agent_percent in percent:
        fileprefix = "output-srti-{}-{}".format(agent,agent_percent)
        inputfilename = fileprefix + ".txt"
        resultfilename= fileprefix +"new.txt"
        models = []
        cpu_time = []
        optimization = []
        linenum = 0
        model = re.compile("Models", re.IGNORECASE)  # Compile a case-insensitive regex
        time = re.compile("CPU Time", re.IGNORECASE)  
        with open (inputfilename, 'rt') as myfile:
            for line in myfile:
                if model.search(line) != None:
                    linenum += 1
                    models.append((linenum, line.rstrip()))
                if time.search(line) != None:
                    cpu_time.append((linenum, line.rstrip()))
        with open(resultfilename, 'w') as writer:
	        for (i,j) in zip(models,cpu_time):
		        writer.write("Instance " + str(i[0]) + ": " + i[1] + ", " + j[1] + "\n")

            
