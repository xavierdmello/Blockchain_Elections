/**Name: Catherine McCaffery
 * Course: ICS3U/C
 * Teacher: Mrs. McCaffery
 * Date: Nov 14, 2021
 * Description: Asks for a user's name and prints a greeting to the screen
 */

package to_be_organized;

import java.util.*;

public class StarterFile 
{
	public static void main(String[] args) 
	{
		//Asks for the user's name and then prints it to the screen
		String name = askName();
		System.out.println("Hello " + name);
		
	}//end main
	
	/**Method Name: askName
	 * Description: Asks for then returns the user's name
	 * Parameters: n/a
	 * Returns: String user's name
	 */
	public static String askName()
	{
		//initializes Scanner
		Scanner myInput = new Scanner (System.in);
		
		//asks for the user name and collects it
		System.out.println("Please enter your name.");
		String userName = myInput.next();
		
		//returns the name entered
		return userName;
		
	} // end method askName
	
}//end class
