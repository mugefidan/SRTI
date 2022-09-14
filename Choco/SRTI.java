//
// Toolkit constraint encoding
//
import java.io.*;
import java.util.*;
import java.util.regex.*;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solution;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.exception.ContradictionException;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.variables.SetVar;
import org.chocosolver.util.iterators.DisposableValueIterator;
import org.chocosolver.util.tools.ArrayUtils;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.constraints.extension.Tuples;

public class SRTI {

	int n;
	List<List<List<Integer>>> prefList = new ArrayList<>();
	List<List<Integer>> flat_prefList = new ArrayList<>();
	Model model;
	Solver solver;
	IntVar[] agent; // domain of lenght of preference list
	
	long totalTime, modelTime, solveTime, readTime, modelSize;
	boolean search;
	int solutions, matchingSize;

	SRTI(String fname) throws IOException {
		search = true;
		totalTime = System.currentTimeMillis();
		readTime = System.currentTimeMillis();
		read(fname);
		readTime = System.currentTimeMillis() - readTime;
	}

	void read(String fname) throws IOException {
		BufferedReader fin = new BufferedReader(new FileReader(fname));
		n = Integer.parseInt(fin.readLine());
		for (int i = 0; i < n; i++) {
			StringTokenizer st = new StringTokenizer(fin.readLine(), "\n");
			int k = 0;
			List<List<Integer>> plist = new ArrayList<>();
			List<Integer> group = new ArrayList<>();
			List<Integer> dummy = new ArrayList<>();
			while (st.hasMoreTokens()) {
				String tie = st.nextToken();
				if(!tie.contains("{"))
				{
					StringTokenizer t1 = new StringTokenizer(tie, " ");
					while(t1.hasMoreTokens()){
						String tie1 = t1.nextToken();
						int j = Integer.parseInt(tie1)-1;
						List<Integer> tieGroup = new ArrayList<>();
						for(int j1 = 0; j1 < 1;j1++)
						{
							tieGroup.add(j);
						}
						plist.add(tieGroup);
					}
				}
				else
				{
					StringTokenizer t1 = new StringTokenizer(tie, " {}");
					while(t1.hasMoreTokens()){ 
					String tie1 = t1.nextToken();
					String[] items = tie1.split("\\s*,\\s*");
					List<Integer> tieGroup = new ArrayList<>();
					for(int j1 = 0; j1 < items.length;j1++)
					{
						tieGroup.add(Integer.parseInt(items[j1])-1);
					}
					plist.add(tieGroup);
				}}
			}
			dummy.add(i);
			plist.add(dummy);
			prefList.add(plist);
		}	
		fin.close();
		for (int i = 0; i < n; i++) {
        	flat_prefList.add(acceptableList(i));
		}		
	}

	List<Integer> acceptableList(int n){
		List<Integer> accept = new ArrayList<>();
		for (int i=0; i < prefList.get(n).size(); i++){
			for (int j=0; j <  prefList.get(n).get(i).size(); j++){
                accept.add(prefList.get(n).get(i).get(j));
			}
		}

		return accept;
	}
	int posInList(int agenti, int agentj){
		int pos = 0;
		for (int i=0; i < prefList.get(agenti).size(); i++){
            if(prefList.get(agenti).get(i).contains(agentj)){
				return pos;
			}
			else
				pos += 1;
		   }
		return -1;
	}

	int rank(int agenti, int agentj){
		int pos = 0;
		for (int i=0; i < flat_prefList.get(agenti).size(); i++){
            if(flat_prefList.get(agenti).get(i) == agentj){
				return pos;
			}
			else
				pos += 1;
		   }
		return -1;
	}

	int[] findNext(int i, int j){
        int r1 = posInList(i, j) +1;
		if(r1 == prefList.get(i).size()){
           r1 = -1;
		}
		int r2 = posInList(j, i) +1;
		if(r2 == prefList.get(j).size()){
           r2 = -1;
		}
		if(r1 != -1 && r2 != -1){
			r1 = rank(i, prefList.get(i).get(r1).get(0));
			r2 = rank(j, prefList.get(j).get(r2).get(0));
		}
		int[] res = new int[2];
		res[0] = r1;
		res[1] = r2;
		return res;
	}

	void build() {
		modelTime = System.currentTimeMillis();
		model = new Model();		
		agent = new IntVar[n];
	
		//define variables 
		for (int i=0;i<n;i++){
			int[] domSet= acceptableList(i).stream().mapToInt(Integer::intValue).toArray();			
			agent[i] = model.intVar("agent_"+Integer.toString(i),domSet);
        }

        for(int i=0; i<n ;i++){
            for (int j = i+1; j < n; j++) {
				int upti = posInList(i,j);
				int uptj = posInList(j,i);
				//symmetric
				model.ifOnlyIf(model.arithm(agent[i], "=", j), model.arithm(agent[j], "=", i));
				//acceptable
				if(upti!=-1 && uptj!=-1){
					List<Integer> flat_ipref = acceptableList(i);
                    List<Integer> flat_jpref = acceptableList(j);
					int isize = flat_ipref.size();
					int jsize = flat_jpref.size();

					int[] next = findNext(i, j);
					if(next[0] ==-1)
						next[0]= isize;
					if(next[1]==-1)
						next[1] = jsize;

					//bool variable
					BoolVar bij = model.boolVar("bij");
					BoolVar bji = model.boolVar("bji");

					for(int k1=next[0]; k1<isize;k1++){
							model.ifThen(model.arithm(agent[i],"=",flat_ipref.get(k1)),model.arithm(bij,"=",1));
					}
					for(int l1=next[1]; l1<jsize;l1++){
							model.ifThen(model.arithm(agent[j],"=",flat_jpref.get(l1)),model.arithm(bji,"=",1));
					}
					model.ifThen(model.arithm(bij,"=",1),model.arithm(bji,"=",0));
					
				}
			}
		}
		solver = model.getSolver();
        modelTime = System.currentTimeMillis() - modelTime;
        modelSize = (Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()) / 1024; // kilobytes
        
	}

	void solve() throws ContradictionException {
		solutions = matchingSize = 0;
		solveTime = System.currentTimeMillis();
		//solver.setVarIntSelector(new StaticVarOrder(solver,solver.getVar(agent)));
		
        if (solver.solve()) {
			solutions = 1;
            System.out.println();
		}
		solveTime = System.currentTimeMillis() - solveTime;
		totalTime = System.currentTimeMillis() - totalTime;
	}

	

	void display() {
		for (int i = 0; i < n; i++) {
			int j = agent[i].getValue();
            if(i<j){
			    System.out.print((i+1) + "-" + (j+1));
			    System.out.println();
		}}

	}
	void stats(){
		solver.printStatistics();
		System.out.print("solutions: "+ solutions +" ");
		if (search) System.out.print("nodes: "+ solver.getNodeCount() +"  ");
		System.out.print("modelTime: "+ modelTime +"  ");
		if (search) System.out.print("solveTime: "+ solveTime +"  ");
		System.out.print("totalTime: "+ totalTime +"  ");
		System.out.print("modelSize: "+ modelSize +"  ");
		System.out.print("readTime: "+ readTime +" ");
		System.out.println();
	}
	public static void main(String[] args) throws IOException, ContradictionException {
		SRTI sr = new SRTI(args[0]);
		sr.build();
        sr.solve();
		sr.display();
        sr.stats();
	}
}