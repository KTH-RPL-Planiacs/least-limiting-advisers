import java.io.File;
import java.io.FileNotFoundException;
import java.util.List;

import parser.Values;
import parser.ast.ModulesFile;
import parser.ast.PropertiesFile;
import prism.Prism;
import prism.PrismDevNullLog;
import prism.PrismException;
import prism.PrismLog;
import prism.Result;
import prism.UndefinedConstants;

public class PrismHandler {

	private Prism prism;
	
	public PrismHandler() {
		try  {
			// Create a log for PRISM output (hidden or stdout)
			PrismLog mainLog = new PrismDevNullLog();
			//PrismLog mainLog = new PrismFileLog("stdout");
			
			// Initialise PRISM engine 
			prism = new Prism(mainLog);
			prism.initialise();
			prism.setStoreVector(true);	//store results for all states
		} catch (PrismException e) {
			System.out.println("Error: " + e.getMessage());
			System.exit(1);
		}
	}
		
	public void loadModelFile(String filePath) {
		
		try  {	
			// Parse and load a PRISM model from a file
			System.out.println("Loading PRISM File from " + filePath);
			File file = new File(filePath);
			ModulesFile modulesFile = prism.parseModelFile(file);
			prism.loadPRISMModel(modulesFile);
		} catch (FileNotFoundException e) {
			System.out.println("Error: " + e.getMessage());
			// Close down PRISM
			prism.closeDown();
			System.exit(1);
		} catch (PrismException e) {
			System.out.println("Error: " + e.getMessage());
			System.exit(1);
		}
	}

	public boolean[] checkBoolProperty(String property) {
        boolean resultArray[] = null;
            try {
                // Model check a property specified as a string
                System.out.println("Checking property " + property);
                Result result = prism.modelCheck(property);
                int resultSize = result.getVector().getSize();
                resultArray = new boolean[resultSize];
                for (int i = 0; i < resultSize; i++) {
                    boolean res = (boolean) result.getVector().getValue(i);
                    resultArray[i] = res;
                }
            } catch (PrismException e) {
                System.out.println("Error: " + e.getMessage());
                System.exit(1);
            }
            return resultArray;
        }

	public double[] checkQuantProperty(String property) {
		double resultArray[] = null;
		try {
			// Model check a property specified as a string
			System.out.println("Checking property " + property);
			Result result = prism.modelCheck(property);
			int resultSize = result.getVector().getSize();
			resultArray = new double[resultSize];
			for (int i = 0; i < resultSize; i++) {
				Double res = (double) result.getVector().getValue(i);
				resultArray[i] = res;
			}
		} catch (PrismException e) {
			System.out.println("Error: " + e.getMessage());
			System.exit(1);
		}
		return resultArray;
	}
}
