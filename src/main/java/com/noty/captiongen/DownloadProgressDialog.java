package com.noty.captiongen;

import javax.swing.*;

public class DownloadProgressDialog extends JDialog {

    private JProgressBar progressBar;

    public DownloadProgressDialog() {
        setTitle("Downloading Model...");
        setSize(300, 100);
        setLocationRelativeTo(null);

        progressBar = new JProgressBar(0, 100);
        progressBar.setStringPainted(true);

        add(progressBar);
    }

    public void updateProgress(int value) {
        progressBar.setValue(value);
    }
}
