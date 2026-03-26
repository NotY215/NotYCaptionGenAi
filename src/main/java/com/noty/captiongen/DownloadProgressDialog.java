package com.noty.captiongen;

import javax.swing.*;
import java.awt.*;
import java.awt.geom.*;

public class DownloadProgressDialog extends JDialog {
    private JProgressBar progressBar;
    private JLabel lblPercent;
    private JLabel lblSize;
    private JLabel lblSpeed;
    private JButton btnCancel;
    private boolean cancelled = false;

    private final Color DARK_BG = new Color(18, 18, 24);
    private final Color CARD_BG = new Color(28, 28, 35);
    private final Color LIGHT_TEXT = new Color(240, 240, 245);
    private final Color ACCENT_BLUE = new Color(64, 128, 255);
    private final Color ACCENT_RED = new Color(255, 80, 80);

    public DownloadProgressDialog(JFrame parent, String modelName, long totalSize) {
        super(parent, "Downloading Model", true);
        setSize(500, 280);
        setLocationRelativeTo(parent);
        setDefaultCloseOperation(JDialog.DO_NOTHING_ON_CLOSE);

        getContentPane().setBackground(DARK_BG);

        JPanel panel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2d = (Graphics2D) g;
                g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
                GradientPaint gp = new GradientPaint(0, 0, DARK_BG, getWidth(), getHeight(), new Color(13, 13, 18));
                g2d.setPaint(gp);
                g2d.fillRect(0, 0, getWidth(), getHeight());
            }
        };
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
        panel.setOpaque(false);

        JLabel lblTitle = new JLabel("Downloading " + modelName);
        lblTitle.setFont(new Font("Segoe UI", Font.BOLD, 14));
        lblTitle.setForeground(LIGHT_TEXT);
        lblTitle.setAlignmentX(Component.CENTER_ALIGNMENT);
        panel.add(lblTitle);

        panel.add(Box.createRigidArea(new Dimension(0, 15)));

        progressBar = new JProgressBar(0, 100);
        progressBar.setStringPainted(true);
        progressBar.setPreferredSize(new Dimension(450, 30));
        progressBar.setAlignmentX(Component.CENTER_ALIGNMENT);
        progressBar.setBackground(new Color(40, 40, 50));
        progressBar.setForeground(ACCENT_BLUE);
        panel.add(progressBar);

        panel.add(Box.createRigidArea(new Dimension(0, 10)));

        lblPercent = new JLabel("0%");
        lblPercent.setAlignmentX(Component.CENTER_ALIGNMENT);
        lblPercent.setForeground(LIGHT_TEXT);
        lblPercent.setFont(new Font("Segoe UI", Font.BOLD, 16));
        panel.add(lblPercent);

        lblSize = new JLabel(formatSize(0) + " / " + formatSize(totalSize));
        lblSize.setAlignmentX(Component.CENTER_ALIGNMENT);
        lblSize.setForeground(new Color(150, 150, 170));
        panel.add(lblSize);

        lblSpeed = new JLabel("Speed: 0 KB/s");
        lblSpeed.setAlignmentX(Component.CENTER_ALIGNMENT);
        lblSpeed.setForeground(new Color(150, 150, 170));
        panel.add(lblSpeed);

        panel.add(Box.createRigidArea(new Dimension(0, 15)));

        btnCancel = new JButton("Cancel Download");
        btnCancel.setAlignmentX(Component.CENTER_ALIGNMENT);
        btnCancel.setBackground(ACCENT_RED);
        btnCancel.setForeground(Color.WHITE);
        btnCancel.setFocusPainted(false);
        btnCancel.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        btnCancel.addActionListener(e -> {
            cancelled = true;
            dispose();
        });
        panel.add(btnCancel);

        add(panel);
    }

    public void updateProgress(int percent, long downloaded, long total, double speed) {
        if (!cancelled) {
            progressBar.setValue(percent);
            lblPercent.setText(percent + "%");
            lblSize.setText(formatSize(downloaded) + " / " + formatSize(total));
            lblSpeed.setText(String.format("Speed: %.2f KB/s", speed));
        }
    }

    private String formatSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return String.format("%.1f KB", bytes / 1024.0);
        if (bytes < 1024 * 1024 * 1024) return String.format("%.1f MB", bytes / (1024.0 * 1024));
        return String.format("%.2f GB", bytes / (1024.0 * 1024 * 1024));
    }

    public boolean isCancelled() {
        return cancelled;
    }
}