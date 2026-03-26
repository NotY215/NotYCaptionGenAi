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
    private JComboBox<String> modelCombo;
    private JLabel lblFileInfo;
    private JLabel lblStatus;
    private JSlider letterSpacingSlider;
    private JLabel lblLetterSpacingValue;
    private JComboBox<String> languageCombo;
    private JCheckBox chkTransliterate;
    private JLabel lblModelSize;
    private File selectedFile;
    private ModelDownloader modelDownloader;
    private boolean modelAvailable;
    private DownloadProgressDialog downloadDialog;
    private String selectedModelPath;

    // Model information
    private static final class ModelInfo {
        String name;
        String url;
        String fileName;
        long sizeBytes;

        ModelInfo(String name, String url, String fileName, long sizeBytes) {
            this.name = name;
            this.url = url;
            this.fileName = fileName;
            this.sizeBytes = sizeBytes;
        }
    }

    private final ModelInfo[] MODELS = {
            new ModelInfo("Tiny (39 MB)",
                    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin",
                    "ggml-tiny.bin", 39 * 1024 * 1024),
            new ModelInfo("Base (142 MB)",
                    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
                    "ggml-base.bin", 142 * 1024 * 1024),
            new ModelInfo("Small (466 MB)",
                    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
                    "ggml-small.bin", 466 * 1024 * 1024),
            new ModelInfo("Medium (1.5 GB)",
                    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin",
                    "ggml-medium.bin", 1536 * 1024 * 1024),
            new ModelInfo("Large V1 (2.9 GB)",
                    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v1.bin",
                    "ggml-large-v1.bin", 2900 * 1024 * 1024)
    };

    public GUI() {
        setTitle("NotYCaptionGenAi - AI Subtitle Generator");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(700, 700);
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

        JLabel subtitleLabel = new JLabel("AI-Powered Subtitle Generator v2.0");
        subtitleLabel.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        subtitleLabel.setForeground(Color.GRAY);
        subtitleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        titlePanel.add(subtitleLabel);

        JLabel creditLabel = new JLabel("Developed By NotY215 | LGPL v3 License");
        creditLabel.setFont(new Font("Segoe UI", Font.ITALIC, 11));
        creditLabel.setForeground(new Color(150, 150, 150));
        creditLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        titlePanel.add(creditLabel);

        // File Selection Panel
        JPanel filePanel = new JPanel(new BorderLayout(10, 10));
        filePanel.setBackground(Color.WHITE);
        filePanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(200, 200, 200)),
                BorderFactory.createEmptyBorder(15, 15, 15, 15)
        ));
        filePanel.setMaximumSize(new Dimension(660, 100));

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

        // Model Selection Panel
        JPanel modelPanel = new JPanel(new GridBagLayout());
        modelPanel.setBackground(Color.WHITE);
        modelPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(200, 200, 200)),
                BorderFactory.createEmptyBorder(15, 15, 15, 15)
        ));
        modelPanel.setMaximumSize(new Dimension(660, 120));

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(5, 10, 5, 10);

        gbc.gridx = 0;
        gbc.gridy = 0;
        JLabel modelLabel = new JLabel("Whisper Model:");
        modelLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        modelPanel.add(modelLabel, gbc);

        gbc.gridx = 1;
        gbc.gridwidth = 2;
        String[] modelNames = new String[MODELS.length];
        for (int i = 0; i < MODELS.length; i++) {
            modelNames[i] = MODELS[i].name;
        }
        modelCombo = new JComboBox<>(modelNames);
        modelCombo.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        modelCombo.addActionListener(e -> updateModelInfo());
        modelPanel.add(modelCombo, gbc);

        gbc.gridx = 0;
        gbc.gridy = 1;
        gbc.gridwidth = 1;
        JLabel sizeLabel = new JLabel("Model Size:");
        sizeLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        modelPanel.add(sizeLabel, gbc);

        gbc.gridx = 1;
        gbc.gridwidth = 2;
        lblModelSize = new JLabel("");
        lblModelSize.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        lblModelSize.setForeground(new Color(100, 100, 100));
        modelPanel.add(lblModelSize, gbc);

        gbc.gridx = 0;
        gbc.gridy = 2;
        gbc.gridwidth = 3;
        btnDownloadModel = new JButton("📥 Download Selected Model");
        btnDownloadModel.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        btnDownloadModel.setBackground(new Color(255, 152, 0));
        btnDownloadModel.setForeground(Color.WHITE);
        btnDownloadModel.setFocusPainted(false);
        btnDownloadModel.addActionListener(e -> confirmAndDownloadModel());
        modelPanel.add(btnDownloadModel, gbc);

        // Settings Panel
        JPanel settingsPanel = new JPanel();
        settingsPanel.setLayout(new GridBagLayout());
        settingsPanel.setBackground(Color.WHITE);
        settingsPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(200, 200, 200)),
                BorderFactory.createEmptyBorder(15, 15, 15, 15)
        ));
        settingsPanel.setMaximumSize(new Dimension(660, 220));

        gbc = new GridBagConstraints();
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
        String[] languages = {"Auto Detect", "English", "Hindi", "Japanese", "Spanish", "French", "German", "Chinese", "Arabic", "Russian", "Korean"};
        languageCombo = new JComboBox<>(languages);
        languageCombo.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        settingsPanel.add(languageCombo, gbc);

        // Transliteration Option
        gbc.gridx = 0;
        gbc.gridy = 2;
        gbc.gridwidth = 3;
        chkTransliterate = new JCheckBox("🔄 Transliterate to English (Hindi, Japanese, Arabic, Chinese, Korean, Russian)");
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
        btnGenerate.addActionListener(e -> confirmAndGenerate());
        settingsPanel.add(btnGenerate, gbc);

        // Status Panel
        JPanel statusPanel = new JPanel(new BorderLayout());
        statusPanel.setBackground(Color.WHITE);
        statusPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(200, 200, 200)),
                BorderFactory.createEmptyBorder(10, 15, 10, 15)
        ));
        statusPanel.setMaximumSize(new Dimension(660, 80));

        lblStatus = new JLabel("✅ Ready. Select a file and model to begin.");
        lblStatus.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        lblStatus.setForeground(new Color(76, 175, 80));
        statusPanel.add(lblStatus, BorderLayout.CENTER);

        // Add all panels
        mainPanel.add(titlePanel);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 20)));
        mainPanel.add(filePanel);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 20)));
        mainPanel.add(modelPanel);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 20)));
        mainPanel.add(settingsPanel);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 20)));
        mainPanel.add(statusPanel);

        add(mainPanel);
        updateModelInfo();
    }

    private void updateModelInfo() {
        int index = modelCombo.getSelectedIndex();
        if (index >= 0 && index < MODELS.length) {
            long sizeMB = MODELS[index].sizeBytes / (1024 * 1024);
            lblModelSize.setText(String.format("%d MB", sizeMB));

            // Check if this model exists
            File modelFile = new File(MODELS[index].fileName);
            if (modelFile.exists() && modelFile.length() > 0) {
                modelAvailable = true;
                selectedModelPath = modelFile.getAbsolutePath();
                btnDownloadModel.setText("✓ Model Available");
                btnDownloadModel.setEnabled(false);
                btnGenerate.setEnabled(selectedFile != null);
                lblStatus.setText("✅ Model available. Ready to generate.");
                lblStatus.setForeground(new Color(76, 175, 80));
            } else {
                modelAvailable = false;
                btnDownloadModel.setText("📥 Download Selected Model");
                btnDownloadModel.setEnabled(true);
                btnGenerate.setEnabled(false);
                lblStatus.setText("⚠️ Model not found. Please download it first.");
                lblStatus.setForeground(Color.ORANGE);
            }
        }
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

            if (modelAvailable) {
                btnGenerate.setEnabled(true);
                lblStatus.setText("✅ File selected. Ready to generate.");
            }
        }
    }

    private void confirmAndDownloadModel() {
        int index = modelCombo.getSelectedIndex();
        if (index < 0 || index >= MODELS.length) return;

        ModelInfo model = MODELS[index];
        long sizeMB = model.sizeBytes / (1024 * 1024);

        int response = JOptionPane.showConfirmDialog(this,
                String.format("Download %s (%d MB)?\n\nThis may take several minutes depending on your internet speed.",
                        model.name, sizeMB),
                "Confirm Download",
                JOptionPane.YES_NO_OPTION);

        if (response == JOptionPane.YES_OPTION) {
            downloadModel(model);
        }
    }

    private void confirmAndGenerate() {
        if (selectedFile == null) {
            JOptionPane.showMessageDialog(this, "Please select a file first!", "Error", JOptionPane.ERROR_MESSAGE);
            return;
        }

        if (!modelAvailable) {
            JOptionPane.showMessageDialog(this, "Whisper model not available. Please download it first!",
                    "Model Missing", JOptionPane.WARNING_MESSAGE);
            return;
        }

        int response = JOptionPane.showConfirmDialog(this,
                String.format("Generate subtitles for:\n%s\n\nModel: %s\nLanguage: %s\nMax letters: %d\nTransliteration: %s",
                        selectedFile.getName(),
                        MODELS[modelCombo.getSelectedIndex()].name,
                        languageCombo.getSelectedItem(),
                        letterSpacingSlider.getValue(),
                        chkTransliterate.isSelected() ? "Yes" : "No"),
                "Confirm Generation",
                JOptionPane.YES_NO_OPTION);

        if (response == JOptionPane.YES_OPTION) {
            generateSubtitles();
        }
    }

    private void downloadModel(ModelInfo model) {
        // Disable all buttons during download
        setButtonsEnabled(false);

        downloadDialog = new DownloadProgressDialog(this, model.name, model.sizeBytes);
        downloadDialog.setVisible(true);

        modelDownloader = new ModelDownloader();
        modelDownloader.downloadModel(model.url, model.fileName, model.sizeBytes, new ModelDownloader.DownloadCallback() {
            @Override
            public void onProgress(int percent, long downloaded, long total, double speed) {
                SwingUtilities.invokeLater(() -> {
                    if (downloadDialog != null && !downloadDialog.isCancelled()) {
                        downloadDialog.updateProgress(percent, downloaded, total, speed);
                    }
                });
            }

            @Override
            public void onComplete(boolean success) {
                SwingUtilities.invokeLater(() -> {
                    if (downloadDialog != null) {
                        downloadDialog.dispose();
                    }
                    setButtonsEnabled(true);

                    if (success) {
                        checkModelStatus();
                        JOptionPane.showMessageDialog(GUI.this,
                                "Model downloaded successfully!",
                                "Success", JOptionPane.INFORMATION_MESSAGE);
                    } else {
                        JOptionPane.showMessageDialog(GUI.this,
                                "Failed to download model. Please check your internet connection.",
                                "Error", JOptionPane.ERROR_MESSAGE);
                    }
                });
            }

            @Override
            public void onCancel() {
                SwingUtilities.invokeLater(() -> {
                    if (downloadDialog != null) {
                        downloadDialog.dispose();
                    }
                    setButtonsEnabled(true);
                    lblStatus.setText("❌ Download cancelled.");
                    lblStatus.setForeground(Color.RED);
                });
            }
        });
    }

    private void setButtonsEnabled(boolean enabled) {
        btnSelectFile.setEnabled(enabled);
        btnGenerate.setEnabled(enabled && modelAvailable && selectedFile != null);
        btnDownloadModel.setEnabled(enabled && !modelAvailable);
        modelCombo.setEnabled(enabled);
        languageCombo.setEnabled(enabled);
        letterSpacingSlider.setEnabled(enabled);
        chkTransliterate.setEnabled(enabled);
    }

    private void checkModelStatus() {
        int index = modelCombo.getSelectedIndex();
        if (index >= 0 && index < MODELS.length) {
            File modelFile = new File(MODELS[index].fileName);
            modelAvailable = modelFile.exists() && modelFile.length() > 0;

            if (modelAvailable) {
                selectedModelPath = modelFile.getAbsolutePath();
                btnDownloadModel.setText("✓ Model Available");
                btnDownloadModel.setEnabled(false);
                btnGenerate.setEnabled(selectedFile != null);
                lblStatus.setText("✅ Model available. Ready to generate.");
                lblStatus.setForeground(new Color(76, 175, 80));
            } else {
                btnDownloadModel.setText("📥 Download Selected Model");
                btnDownloadModel.setEnabled(true);
                btnGenerate.setEnabled(false);
                lblStatus.setText("⚠️ Model not found. Please download it first.");
                lblStatus.setForeground(Color.ORANGE);
            }
        }
    }

    private void generateSubtitles() {
        // Disable all buttons during generation
        setButtonsEnabled(false);
        btnGenerate.setEnabled(false);

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
                            languageCombo.getSelectedItem().toString(),
                            selectedModelPath);

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
                                "Subtitles generated successfully!\n\nSaved to:\n" + outputPath +
                                        (chkTransliterate.isSelected() ? "\n\nTransliterated version also saved." : ""),
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
                setButtonsEnabled(true);
                if (modelAvailable && selectedFile != null) {
                    btnGenerate.setEnabled(true);
                }
                lblStatus.setText("✅ Ready for next file.");
                lblStatus.setForeground(new Color(76, 175, 80));
            }
        };

        worker.execute();
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