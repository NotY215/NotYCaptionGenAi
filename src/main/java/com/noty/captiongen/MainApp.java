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

        // Load native library for Whisper
        try {
            System.loadLibrary("whisper-jni");
        } catch (UnsatisfiedLinkError e) {
            System.err.println("Whisper JNI library not found. Will use fallback mode.");
        }

        // Start application
        SwingUtilities.invokeLater(() -> {
            GUI gui = new GUI();
            gui.setVisible(true);
        });
    }
}