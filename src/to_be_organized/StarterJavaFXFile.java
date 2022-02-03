/**Name: Catherine McCaffery
 * Course: ICS4U/C
 * Teacher: Mrs. McCaffery
 * Date: Nov 14, 2021
 * Description: Hello World program with a GUI interface using JavaFX
 */

package to_be_organized;

import javafx.application.Application;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.text.Font;
import javafx.scene.text.Text;
import javafx.stage.Stage;

public class StarterJavaFXFile extends Application 
{
	@Override
	public void start(Stage primaryStage) throws Exception 
	{
		Text text = new Text(10,50,"Hello World");
		text.setFont(Font.font(50));
		
		Group root = new Group (text);
		Scene scene = new Scene (root);
		
		primaryStage.setTitle("Welcome to JavaFX");
		primaryStage.setScene(scene);
		primaryStage.show();
		
	}// end start method

	public static void main(String[] args) 
	{
		launch(args);
	}//end main method

}//end class StarterJavaFXFile
