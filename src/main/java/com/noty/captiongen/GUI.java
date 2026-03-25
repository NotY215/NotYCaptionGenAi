package com.noty.captiongen;

import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.nio.file.*;
import javax.swing.filechooser.FileNameExtensionFilter;

public class GUI extends JFrame {
    private JButton btnSelectFile;
    private JButton btnGenerate;
    private JButton btnDownloadModel;
    private JLabel lblFileInfo;
    private JLabel lblStatus;
    private JSlider letterSpacingSlider;
    private JLabel lblLetterSpacingValue;
    private JComboBox<String> languageCombo;
    private JCheckBox chkTransliterate;
    private File selectedFile;
    private ModelDownloader modelDownloader;
    private boolean modelAvailable;

    public GUI() {
        setTitle("NotYCaptionGenAi - AI Subtitle Generator");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(650, 550);
        setLocationRelativeTo(null);

        // Load icon
        try {
            ImageIcon icon = new ImageIcon(getClass().getResource("/app.ico"));
            setIconImage(icon.getImage());
        } catch (Exception e) {
            // Icon not found, continue without icon
        }

        initComponents();
        checkModelStatus();
        startModelCheckThread();
    }

    private void initComponents() {
        // Main panel with padding
        JPanel mainPanel = new JPanel();
        mainPanel.setLayout(new BoxLayout(mainPanel, BoxLayout.Y_AXIS));
        mainPanel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
        mainPanel.setBackground(new Color(245, 245, 245));

        // Title Panel
        JPanel titlePanel = new JPanel();
        titlePanel.setBackground(new Color(245, 245, 245));
        JLabel titleLabel = new JLabel("NotYCaptionGenAi");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 28));
        titleLabel.setForeground(new Color(66, 133, 244));
        titleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        titlePanel.add(titleLabel);

        JLabel subtitleLabel = new JLabel("AI-Powered Subtitle Generator");
        subtitleLabel.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        subtitleLabel.setForeground(Color.GRAY);
        subtitleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        titlePanel.add(subtitleLabel);

        // File Selection Panel
        JPanel filePanel = new JPanel(new BorderLayout(10, 10));
        filePanel.setBackground(Color.WHITE);
        filePanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(200, 200, 200)),
                BorderFactory.createEmptyBorder(15, 15, 15, 15)
        ));
        filePanel.setMaximumSize(new Dimension(600, 100));

        btnSelectFile = new JButton("📁 Select Video/Audio File");
        btnSelectFile.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        btnSelectFile.setBackground(new Color(66, 133, 244));
        btnSelectFile.setForeground(Color.WHITE);
        btnSelectFile.setFocusPainted(false);
        btnSelectFile.addActionListener(e -> selectFile());

        lblFileInfo = new JLabel("No file selected");
        lblFileInfo.setFont(new Font("Segoe UI", Font.ITALIC, 12));
        lblFileInfo.setForeground(Color.GRAY);

        filePanel.add(btnSelectFile, BorderLayout.CENTER);
        filePanel.add(lblFileInfo, BorderLayout.SOUTH);

        // Settings Panel
        JPanel settingsPanel = new JPanel();
        settingsPanel.setLayout(new GridBagLayout());
        settingsPanel.setBackground(Color.WHITE);
        settingsPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(200, 200, 200)),
                BorderFactory.createEmptyBorder(15, 15, 15, 15)
        ));
        settingsPanel.setMaximumSize(new Dimension(600, 250));

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(10, 10, 10, 10);

        // Letter Spacing
        gbc.gridx = 0;
        gbc.gridy = 0;
        JLabel letterSpacingLabel = new JLabel("Max Letters per Line:");
        letterSpacingLabel.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        settingsPanel.add(letterSpacingLabel, gbc);

        gbc.gridx = 1;
        letterSpacingSlider = new JSlider(20, 80, 42);
        letterSpacingSlider.setMajorTickSpacing(10);
        letterSpacingSlider.setPaintTicks(true);
        letterSpacingSlider.setPaintLabels(true);
        settingsPanel.add(letterSpacingSlider, gbc);

        gbc.gridx = 2;
        lblLetterSpacingValue = new JLabel("42");
        lblLetterSpacingValue.setFont(new Font("Segoe UI", Font.BOLD, 13));
        settingsPanel.add(lblLetterSpacingValue, gbc);

        letterSpacingSlider.addChangeListener(e -> {
            lblLetterSpacingValue.setText(String.valueOf(letterSpacingSlider.getValue()));
        });

        // Language Selection
        gbc.gridx = 0;
        gbc.gridy = 1;
        JLabel languageLabel = new JLabel("Language:");
        languageLabel.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        settingsPanel.add(languageLabel, gbc);

        gbc.gridx = 1;
        gbc.gridwidth = 2;
        String[] languages = {"Auto Detect", "English", "Hindi", "Japanese", "Spanish", "French", "German", "Chinese", "Arabic"};
        languageCombo = new JComboBox<>(languages);
        languageCombo.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        settingsPanel.add(languageCombo, gbc);

        // Transliteration Option
        gbc.gridx = 0;
        gbc.gridy = 2;
        gbc.gridwidth = 1;
        chkTransliterate = new JCheckBox("Transliterate to English (Hindi/Japanese support)");
        chkTransliterate.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        chkTransliterate.setBackground(Color.WHITE);
        settingsPanel.add(chkTransliterate, gbc);

        // Generate Button
        gbc.gridx = 0;
        gbc.gridy = 3;
        gbc.gridwidth = 3;
        btnGenerate = new JButton("🚀 Generate Subtitles");
        btnGenerate.setFont(new Font("Segoe UI", Font.BOLD, 14));
        btnGenerate.setBackground(new Color(76, 175, 80));
        btnGenerate.setForeground(Color.WHITE);
        btnGenerate.setFocusPainted(false);
        btnGenerate.setEnabled(false);
        btnGenerate.addActionListener(e -> generateSubtitles());
        settingsPanel.add(btnGenerate, gbc);

        // Model Download Button (initially hidden)
        gbc.gridy = 4;
        btnDownloadModel = new JButton("📥 Download Whisper Model");
        btnDownloadModel.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        btnDownloadModel.setBackground(new Color(255, 152, 0));
        btnDownloadModel.setForeground(Color.WHITE);
        btnDownloadModel.setFocusPainted(false);
        btnDownloadModel.setVisible(false);
        btnDownloadModel.addActionListener(e -> downloadModel());
        settingsPanel.add(btnDownloadModel, gbc);

        // Status Panel
        JPanel statusPanel = new JPanel(new BorderLayout());
        statusPanel.setBackground(Color.WHITE);
        statusPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(200, 200, 200)),
                BorderFactory.createEmptyBorder(10, 15, 10, 15)
        ));
        statusPanel.setMaximumSize(new Dimension(600, 80));

        lblStatus = new JLabel("✅ Ready. Select a file to begin.");
        lblStatus.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        lblStatus.setForeground(new Color(76, 175, 80));
        statusPanel.add(lblStatus, BorderLayout.CENTER);

        // Add all panels
        mainPanel.add(titlePanel);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 20)));
        mainPanel.add(filePanel);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 20)));
        mainPanel.add(settingsPanel);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 20)));
        mainPanel.add(statusPanel);

        add(mainPanel);
    }

    private void selectFile() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setDialogTitle("Select Video or Audio File");

        String[] extensions = {"wav", "mp4", "mp3", "m4a", "mkv", "avi", "wmv", "mpeg", "flac"};
        FileNameExtensionFilter filter = new FileNameExtensionFilter(
                "Media Files (WAV, MP4, MP3, M4A, MKV, AVI, WMV, MPEG, FLAC)", extensions);
        fileChooser.setFileFilter(filter);

        int result = fileChooser.showOpenDialog(this);
        if (result == JFileChooser.APPROVE_OPTION) {
            selectedFile = fileChooser.getSelectedFile();
            lblFileInfo.setText(selectedFile.getName() + " (" + (selectedFile.length() / 1024 / 1024) + " MB)");
            btnGenerate.setEnabled(modelAvailable);

            if (!modelAvailable) {
                lblStatus.setText("⚠️ Model not found. Please download the Whisper model first.");
                lblStatus.setForeground(Color.ORANGE);
            } else {
                lblStatus.setText("✅ File selected. Ready to generate.");
                lblStatus.setForeground(new Color(76, 175, 80));
            }
        }
    }

    private void generateSubtitles() {
        if (selectedFile == null) {
            JOptionPane.showMessageDialog(this, "Please select a file first!", "Error", JOptionPane.ERROR_MESSAGE);
            return;
        }

        if (!modelAvailable) {
            JOptionPane.showMessageDialog(this, "Whisper model not available. Please download it first!",
                    "Model Missing", JOptionPane.WARNING_MESSAGE);
            return;
        }

        // Disable button during processing
        btnGenerate.setEnabled(false);
        btnSelectFile.setEnabled(false);
        lblStatus.setText("⏳ Processing... Extracting audio (if needed)...");
        lblStatus.setForeground(Color.BLUE);

        SwingWorker<Void, String> worker = new SwingWorker<Void, String>() {
            @Override
            protected Void doInBackground() throws Exception {
                try {
                    publish("🎵 Extracting audio from media file...");
                    File audioFile = AudioExtractor.extractAudio(selectedFile);

                    publish("🎤 Transcribing with Whisper AI...");
                    String transcription = WhisperTranscriber.transcribe(audioFile,
                            languageCombo.getSelectedItem().toString());

                    publish("📝 Generating SRT subtitles...");
                    int maxLetters = letterSpacingSlider.getValue();
                    String srtContent = SRTGenerator.generateSRT(transcription, maxLetters);

                    publish("💾 Saving subtitle file...");
                    String outputPath = selectedFile.getParent() + File.separator +
                            getFileNameWithoutExtension(selectedFile) + ".srt";
                    Files.write(Paths.get(outputPath), srtContent.getBytes());

                    // Transliteration if needed
                    if (chkTransliterate.isSelected()) {
                        publish("🔄 Performing transliteration...");
                        String transliterated = Transliterator.transliterate(srtContent);
                        String translitPath = selectedFile.getParent() + File.separator +
                                getFileNameWithoutExtension(selectedFile) + "_translit.srt";
                        Files.write(Paths.get(translitPath), transliterated.getBytes());
                        publish("✅ Transliterated version saved separately.");
                    }

                    publish("🎉 Subtitle generation completed successfully!");

                    // Clean up temporary audio file if it was extracted
                    if (!selectedFile.getName().toLowerCase().endsWith(".wav")) {
                        audioFile.delete();
                    }

                    SwingUtilities.invokeLater(() -> {
                        JOptionPane.showMessageDialog(GUI.this,
                                "Subtitles generated successfully!\n\nSaved to:\n" + outputPath,
                                "Success", JOptionPane.INFORMATION_MESSAGE);
                    });

                } catch (Exception e) {
                    e.printStackTrace();
                    publish("❌ Error: " + e.getMessage());
                    SwingUtilities.invokeLater(() -> {
                        JOptionPane.showMessageDialog(GUI.this,
                                "Error generating subtitles:\n" + e.getMessage(),
                                "Error", JOptionPane.ERROR_MESSAGE);
                    });
                }
                return null;
            }

            @Override
            protected void process(java.util.List<String> chunks) {
                String lastMessage = chunks.get(chunks.size() - 1);
                lblStatus.setText(lastMessage);
            }

            @Override
            protected void done() {
                btnGenerate.setEnabled(true);
                btnSelectFile.setEnabled(true);
                if (modelAvailable) {
                    lblStatus.setText("✅ Ready for next file.");
                    lblStatus.setForeground(new Color(76, 175, 80));
                }
            }
        };

        worker.execute();
    }

    private void checkModelStatus() {
        File modelFile = new File("ggml-base.bin");
        modelAvailable = modelFile.exists() && modelFile.length() > 0;

        if (!modelAvailable) {
            btnDownloadModel.setVisible(true);
            btnGenerate.setEnabled(false);
            lblStatus.setText("⚠️ Whisper model not found. Please download it first.");
            lblStatus.setForeground(Color.ORANGE);
        } else {
            btnDownloadModel.setVisible(false);
            if (selectedFile != null) {
                btnGenerate.setEnabled(true);
            }
            lblStatus.setText("✅ Model available. Ready to generate subtitles.");
            lblStatus.setForeground(new Color(76, 175, 80));
        }
    }

    private void startModelCheckThread() {
        Timer timer = new Timer(5000, e -> checkModelStatus());
        timer.start();
    }

    private void downloadModel() {
        modelDownloader = new ModelDownloader();
        modelDownloader.downloadModel(this, new ModelDownloader.DownloadCallback() {
            @Override
            public void onProgress(int percent) {
                SwingUtilities.invokeLater(() -> {
                    lblStatus.setText("📥 Downloading model: " + percent + "%");
                });
            }

            @Override
            public void onComplete(boolean success) {
                SwingUtilities.invokeLater(() -> {
                    if (success) {
                        checkModelStatus();
                        lblStatus.setText("✅ Model downloaded successfully!");
                        lblStatus.setForeground(new Color(76, 175, 80));
                        JOptionPane.showMessageDialog(GUI.this,
                                "Whisper model downloaded successfully!",
                                "Success", JOptionPane.INFORMATION_MESSAGE);
                    } else {
                        lblStatus.setText("❌ Model download failed. Please check your internet connection.");
                        lblStatus.setForeground(Color.RED);
                        JOptionPane.showMessageDialog(GUI.this,
                                "Failed to download model. Please check your internet connection.",
                                "Error", JOptionPane.ERROR_MESSAGE);
                    }
                });
            }
        });
    }

    private String getFileNameWithoutExtension(File file) {
        String name = file.getName();
        int lastDot = name.lastIndexOf('.');
        if (lastDot > 0) {
            return name.substring(0, lastDot);
        }
        return name;
    }
}