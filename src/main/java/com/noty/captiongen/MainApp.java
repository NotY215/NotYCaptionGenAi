package com.noty.captiongen;

import javax.swing.*;
import java.awt.*;
import java.net.URL;

public class MainApp {
    public static void main(String[] args) {
        // Set system look and feel
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }

        // Check if Whisper JNI is available
        if (WhisperJNIWrapper.isAvailable()) {
            System.out.println("Whisper JNI native library loaded successfully");
        } else {
            System.out.println("Whisper JNI native library not found. Using fallback mode.");
        }

        // Start application
        SwingUtilities.invokeLater(() -> {
            GUI gui = new GUI();
            gui.setVisible(true);

            // Set taskbar icon for Windows
            setTaskbarIcon(gui);
        });
    }

    private static void setTaskbarIcon(JFrame frame) {
        try {
            // For Windows taskbar
            if (System.getProperty("os.name").toLowerCase().contains("win")) {
                java.awt.Taskbar taskbar = java.awt.Taskbar.getTaskbar();
                URL iconURL = MainApp.class.getResource("/app.ico");
                if (iconURL != null) {
                    ImageIcon icon = new ImageIcon(iconURL);
                    taskbar.setIconImage(icon.getImage());
                }
            }
        } catch (Exception e) {
            System.err.println("Could not set taskbar icon: " + e.getMessage());
        }
    }
}