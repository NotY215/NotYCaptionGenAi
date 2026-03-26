package com.noty.captiongen;

import javax.swing.*;

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
        });
    }
}