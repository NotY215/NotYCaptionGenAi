package com.noty.captiongen;

import javax.swing.*;
import java.awt.*;

public class MainApp {
    public static void main(String[] args) {
        // Set system look and feel
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }

        // Start application
        SwingUtilities.invokeLater(() -> {
            GUI gui = new GUI();
            gui.setVisible(true);
        });
    }
}