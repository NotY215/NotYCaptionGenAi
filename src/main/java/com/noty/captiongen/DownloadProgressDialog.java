package com.noty.captiongen;

import javax.swing.*;
import java.awt.*;
import java.text.DecimalFormat;

public class DownloadProgressDialog extends JDialog {
    private JProgressBar progressBar;
    private JLabel lblPercent;
    private JLabel lblSize;
    private JLabel lblSpeed;
    private JButton btnCancel;
    private boolean cancelled = false;

    public DownloadProgressDialog(JFrame parent, String modelName, long totalSize) {
        super(parent, "Downloading Model", true);
        setSize(450, 220);
        setLocationRelativeTo(parent);
        setDefaultCloseOperation(JDialog.DO_NOTHING_ON_CLOSE);

        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel lblTitle = new JLabel("Downloading " + modelName);
        lblTitle.setFont(new Font("Segoe UI", Font.BOLD, 14));
        lblTitle.setAlignmentX(Component.CENTER_ALIGNMENT);
        panel.add(lblTitle);

        panel.add(Box.createRigidArea(new Dimension(0, 15)));

        progressBar = new JProgressBar(0, 100);
        progressBar.setStringPainted(true);
        progressBar.setPreferredSize(new Dimension(400, 25));
        progressBar.setAlignmentX(Component.CENTER_ALIGNMENT);
        panel.add(progressBar);

        panel.add(Box.createRigidArea(new Dimension(0, 10)));

        lblPercent = new JLabel("0%");
        lblPercent.setAlignmentX(Component.CENTER_ALIGNMENT);
        panel.add(lblPercent);

        lblSize = new JLabel(formatSize(0) + " / " + formatSize(totalSize));
        lblSize.setAlignmentX(Component.CENTER_ALIGNMENT);
        panel.add(lblSize);

        lblSpeed = new JLabel("Speed: 0 KB/s");
        lblSpeed.setAlignmentX(Component.CENTER_ALIGNMENT);
        panel.add(lblSpeed);

        panel.add(Box.createRigidArea(new Dimension(0, 15)));

        btnCancel = new JButton("Cancel Download");
        btnCancel.setAlignmentX(Component.CENTER_ALIGNMENT);
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