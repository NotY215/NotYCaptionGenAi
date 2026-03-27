package pro.noty.caption;

import java.io.File;
import java.io.IOException;

public class Launcher {
    public static void main(String[] args) {
        // Set console encoding to UTF-8 for better display
        System.setProperty("file.encoding", "UTF-8");

        try {
            // Create a new console for better input handling
            if (System.console() == null) {
                // Fallback when running in IDE
                System.out.println("Starting in fallback mode...");
            }

            // Launch the main application
            Main.main(args);

        } catch (Exception e) {
            System.err.println("Error launching application: " + e.getMessage());
            e.printStackTrace();
            System.out.println("\nPress Enter to exit...");
            try {
                System.in.read();
            } catch (IOException ex) {
                // Ignore
            }
        }
    }
}