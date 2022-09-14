from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from os import defpath
from ortools.sat.python import cp_model
import sys
import time


def flatten(preflis):
    li = []
    for el in preflis:
        li.extend([int(x) for x in el.split(' ')])
    return li

    


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, x):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.x = x
        self.__solution_count = 0

    def on_solution_callback(self):
        #print(self.x[0].Value)
        """print('x1',self.Value(self.x[1]))
        print('x2',self.Value(self.x[2]))
        print('x3',self.Value(self.x[3]))
        print('x4',self.Value(self.x[4]))
        print('x5',self.Value(self.x[5]))
        print('x6',self.Value(self.x[6]))
        print('----------')"""
        self.__solution_count += 1

    def solution_count(self):
        return self.__solution_count


class Instance:
    def __init__(self, agentList):
        self.agentList = agentList
        

        self.numberOfAgent = len(agentList.keys())

    def getAcceptableAgentSet(self, index):
        d = set()
        for el in self.agentList[index]:
            for x in el.split(' '):
                d.add(int(x))
        #d.add(int(index))
        return d

    def nextAgent(self, agent1ID, agent2ID):
        plis = self.agentList[agent1ID]
        for idx, x in enumerate(plis):
            d = [int(z) for z in x.split(' ')]
            if agent2ID in d and idx + 1 != len(plis):
                return plis[idx + 1]
        return -1


    def findNext(self, agent1ID, agent2ID):
        next = self.nextAgent(agent1ID, agent2ID)
        if next == -1:
            b1 = next
        elif len(next.split(' ')) ==1:
            b1 = flatten(self.agentList[agent1ID]).index(int(next))
        elif len(next.split(' ')) > 1:
            b1 = flatten(self.agentList[agent1ID]).index(int(next.split(' ')[-1]))

        next = self.nextAgent(agent2ID, agent1ID)
        if next == -1:
            b2 = next
        elif len(next.split(' ')) == 1:
            b2 = flatten(self.agentList[agent2ID]).index(int(next))
        elif len(next.split(' ')) > 1:
            b2 = flatten(self.agentList[agent2ID]).index(int(next.split(' ')[-1]))

        return b1, b2

    def isInAgentList(self, agent1ID, agent2ID):
        if agent1ID in self.getAcceptableAgentSet(agent2ID):
            for idx, el in enumerate(self.agentList[agent2ID]):
                d = [int(x) for x in el.split(' ')]
                if agent1ID in d:
                    return True, idx
        else:
            return False, -1

    def createModel(self):
        m = cp_model.CpModel()
        n = self.numberOfAgent
        x = {}
        
        
        for i in range(1, self.numberOfAgent+1):
            x[i] = m.NewIntVarFromDomain(cp_model.Domain.FromValues(self.getAcceptableAgentSet(i)), name='a{}'.format(i))
       
        for i in range(1, self.numberOfAgent+1):
            for j in range(i+1, self.numberOfAgent+1):
                t1 = self.isInAgentList(i,j)[0]
                t2 = self.isInAgentList(j,i)[0]
                b = m.NewBoolVar('b')
                m.Add(x[i]==j).OnlyEnforceIf(b)
                m.Add(x[j]==i).OnlyEnforceIf(b)
                m.Add(x[i]!=j).OnlyEnforceIf(b.Not())
                m.Add(x[j]!=i).OnlyEnforceIf(b.Not())
                if t1 and t2:
                    # eliminate illegal roommates
                    
                    ipref = flatten(self.agentList[i])
                    jpref = flatten(self.agentList[j])

                    updatedi = ipref.index(j)
                    updatedj= jpref.index(i)
                    """for k in range(len(ipref)):
                        if k != updatedi:
                            m.AddForbiddenAssignments([x[i], x[j]], [(ipref[k], i)])
                    for k in range(len(jpref)):
                        if k != updatedj:
                            m.AddForbiddenAssignments([x[j], x[i]], [(jpref[k], j)])"""
                    # eliminate blocking pairs
                    b1, b2 = self.findNext(i, j)

                    if b1 == -1:
                        b1 = len(ipref) - 1
                    if b2 == -1:
                        b2 = len(jpref) - 1
                    #add auxiliary variables
                    bij = m.NewBoolVar('b_%i_% j')
                    bji = m.NewBoolVar('b_%j_% i')

                    for k in range(b1,len(ipref)):
                        #i1.append(ipref[k])
                        #m.AddAllowedAssignments([x[i],b[i,j]],[(ipref[k],1)])     
                        m.AddForbiddenAssignments([x[i],bij],[(ipref[k],0)])     
                        
                    for l in range(b2,len(jpref)):
                        #j1.append(jpref[l])
                        #m.AddAllowedAssignments([x[j],b[i,j]],[(jpref[l],1)])     
                        m.AddForbiddenAssignments([x[j],bji],[(jpref[l],0)])               


                    m.AddBoolOr([bij.Not(),bji.Not()])


        return m, x


def GenerateRankList(preferencesInLine):
    res= []
    element = preferencesInLine.split(" ")
    for i in element:
        if '{' not in i:
            res.append(i)
        else:
            tie = i[1:-1].replace(","," ")
            res.append(tie)
    return res




def main():
    with open(sys.argv[1],"r") as f:
        lines = f.readlines()
        prefix = sys.argv[1][:sys.argv[1].find(".txt")]
    f.close()
    START_TIME = time.time()

    numberOfAgent = int(lines[0])

    AgentList = {}
    start = time.time()
    for i in range(1, 1 + numberOfAgent):
        line = lines[i]  # line = "ID Preferences"
        line = line.replace("\n", "")  # getting rid of \n character at the end of the line
        id = i  # this is the id of agent
        #if line[-1]==" ":
        line = line.strip()
        preferenceList = GenerateRankList(line)  
        AgentList[id] = preferenceList
        AgentList[id].append(str(id))
    #print(AgentList)
    
   
    i = Instance(AgentList)
    m,a = i.createModel()
    solver = cp_model.CpSolver()
    status = solver.Solve(m)
    #c = SolutionPrinter(a)
    #solver.SearchForAllSolutions(m, c)
    #print(c.solution_count())
    end = time.time()
    runtime = end-start
    print(m.ModelStats())
    print(solver.ResponseStats())
    print('Runtime is',format(runtime,".4f"))
    if status == cp_model.OPTIMAL:
        print("Solution: Exits")
        print("Roommate Pairs: ")
        for i in range(1, numberOfAgent+1):
            j= solver.Value(a[i])
            if i<j:
                print("("+str(i)+","+str(j)+")")
    else:
        print("No solution!")


if __name__ == '__main__':
    main()
